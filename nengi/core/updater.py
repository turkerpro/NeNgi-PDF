"""
NeNgi PDF - Uygulama Ici Guncelleyici (In-App Updater).

GitHub `turkerpro/NeNgi-PDF` deposundaki `latest-build` release'ini
sadece standart kutuphane (urllib) ile sorgular, yerel __version__
ile karsilastirir, yeni `*Setup.exe` varligini %TEMP% dizinine indirir
(ilerleme callback destekli), dogrular (boyut > 0) ve NSIS sessiz
kurulum bayragi ("/S") ile baslatip uygulamayi kapatir.

Ag yoksa / repo ozelse / API yanit vermezse: exception yerine
Turkce "graceful" hata mesaji tasiyan UpdateCheckError yukseltilir;
UI katmani bunu QMessageBox ile gosterir.

Kural: `requests` YOK, `PyQt-network` (QNetworkAccessManager) YOK.
Ag isleri stdlib, arka plan calisma QThread/worker ile yapilir.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Optional

try:
    from PyQt6.QtCore import QThread, pyqtSignal
    _QT_AVAILABLE = True
except Exception:  # pragma: no cover - Qt'siz ortamda (saf mantik testleri)
    QThread = object  # type: ignore
    pyqtSignal = lambda *a, **k: None  # type: ignore
    _QT_AVAILABLE = False

from nengi import __version__ as LOCAL_VERSION

GITHUB_OWNER = "turkerpro"
GITHUB_REPO = "NeNgi-PDF"
RELEASE_TAG = "latest-build"
BETA_TAG = "beta-build"
CHANNEL_TAGS = {
    "beta": BETA_TAG,
    "stabil": RELEASE_TAG,
}
DEFAULT_CHANNEL = "beta"
API_URL = (
    f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"
    f"/releases/tags/{RELEASE_TAG}"
)
USER_AGENT = "NeNgi-PDF-Updater"
REQUEST_TIMEOUT = 12
# Yarım/bozuk Setup.exe'yi çalıştırmamak için minimum kurulum boyutu (10 MB).
MIN_INSTALLER_BYTES = 10 * 1024 * 1024

_VERSION_RE = re.compile(r"v?(\d+(?:\.\d+){0,3})")


class UpdateCheckError(Exception):
    """Kullaniciya gosterilebilir, Turkce güncelleme hatasi."""


class DownloadCancelledError(UpdateCheckError):
    """İndirme kullanıcı tarafından iptal edildi (yarım dosya temizlenir)."""


@dataclass
class UpdateInfo:
    has_update: bool
    local_version: str
    remote_version: str
    download_url: Optional[str]
    notes: str = ""
    published_at: str = ""


# ---------------------------------------------------------------------------
# Guncelleme kanali (beta + stabil)
# ---------------------------------------------------------------------------

def normalize_channel(channel: Optional[str]) -> str:
    """Kanal adini normalize et: 'beta' veya 'stabil'. Bilinmeyende default."""
    text = (channel or "").strip().lower()
    if text in ("stabil", "stable", "latest", "latest-build"):
        return "stabil"
    if text in ("beta", "beta-build"):
        return "beta"
    return DEFAULT_CHANNEL


def tag_for_channel(channel: Optional[str] = None) -> str:
    """Kanala karsilik gelen release tag'i dondur."""
    return CHANNEL_TAGS[normalize_channel(channel)]


def api_url_for_channel(channel: Optional[str] = None) -> str:
    """Kanalin GitHub release API URL'sini dondur."""
    tag = tag_for_channel(channel)
    return (
        f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"
        f"/releases/tags/{tag}"
    )


def get_update_channel() -> str:
    """QSettings 'update_channel' degerini oku (default 'beta')."""
    try:
        from PyQt6.QtCore import QSettings
        value = QSettings("NeNgi", "NeNgiPDF").value("update_channel", DEFAULT_CHANNEL)
        return normalize_channel(str(value) if value is not None else DEFAULT_CHANNEL)
    except Exception:
        return DEFAULT_CHANNEL


def set_update_channel(channel: str) -> str:
    """QSettings 'update_channel' degerini yaz, normalize edilmis degeri dondur."""
    normalized = normalize_channel(channel)
    try:
        from PyQt6.QtCore import QSettings
        QSettings("NeNgi", "NeNgiPDF").setValue("update_channel", normalized)
    except Exception:
        pass
    return normalized


# ---------------------------------------------------------------------------
# Surum karsilastirma (saf mantik - ag gerektirmez, test edilebilir)
# ---------------------------------------------------------------------------

def parse_version(version: str) -> tuple[int, ...]:
    """'v2.0.0' -> (2, 0, 0). Sayisal olmayan ekler (beta vb.) yoksayilir."""
    text = (version or "").strip()
    match = _VERSION_RE.search(text)
    if not match:
        return (0,)
    parts = []
    for chunk in match.group(1).split("."):
        digits = re.sub(r"\D", "", chunk)
        parts.append(int(digits) if digits else 0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts)


def compare_versions(local: str, remote: str) -> int:
    """Karsilastir: -1 local<remote (guncelleme var), 0 esit, +1 local>remote.

    '-beta' soneki anlasilir: '2.1.0-beta' < '2.1.0' (sayisal kisim esitse
    beta one-surum sayilir ve kucuktur).
    """
    lv, rv = parse_version(local), parse_version(remote)
    length = max(len(lv), len(rv))
    lv += (0,) * (length - len(lv))
    rv += (0,) * (length - len(rv))
    if lv < rv:
        return -1
    if lv > rv:
        return 1
    local_beta = "beta" in (local or "").lower()
    remote_beta = "beta" in (remote or "").lower()
    if local_beta and not remote_beta:
        return -1
    if remote_beta and not local_beta:
        return 1
    return 0


def is_newer(local: str, remote: str) -> bool:
    """Remote, local'den yeniyse True."""
    return compare_versions(local, remote) < 0


# ---------------------------------------------------------------------------
# GitHub API (stdlib urllib)
# ---------------------------------------------------------------------------

def _http_get_json(url: str, timeout: int = REQUEST_TIMEOUT) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/vnd.github+json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        if e.code in (403, 404, 451):
            raise UpdateCheckError(
                "Güncelleme bilgisi alınamadı. Sürüm henüz yayınlanmamış "
                "veya depo özel olabilir. (HTTP %s)" % e.code
            ) from e
        if e.code == 429:
            raise UpdateCheckError(
                "GitHub istek limiti aşıldı (HTTP 429). Lütfen birkaç "
                "dakika sonra tekrar deneyin."
            ) from e
        raise UpdateCheckError(
            "Güncelleme sunucusuna ulaşılamadı (HTTP %s). "
            "İnternet bağlantınızı kontrol edin." % e.code
        ) from e
    except urllib.error.URLError as e:
        raise UpdateCheckError(
            "İnternet bağlantısı yok veya güncelleme sunucusuna "
            "ulaşılamadı. Bağlantınızı kontrol edip tekrar deneyin."
        ) from e
    except TimeoutError as e:
        raise UpdateCheckError(
            "Güncelleme denetimi zaman aşımına uğradı. "
            "Lütfen tekrar deneyin."
        ) from e
    except OSError as e:
        raise UpdateCheckError(
            "Ağ hatası: güncelleme denetlenemedi (%s)." % e
        ) from e
    try:
        data = json.loads(raw)
    except (ValueError, json.JSONDecodeError) as e:
        raise UpdateCheckError(
            "Güncelleme sunucusundan geçersiz yanıt alındı."
        ) from e
    if not isinstance(data, dict):
        raise UpdateCheckError("Güncelleme sunucusundan geçersiz yanıt alındı.")
    return data


def extract_remote_version(release: dict) -> str:
    """Release JSON icinden surum cikar: name -> tag_name -> asset adlari.

    '-beta' soneki korunur: kaynak metinde 'beta' geciyorsa donen surume
    '-beta' eklenir (or. '2.1.0-beta').
    """
    for key in ("name", "tag_name"):
        value = str(release.get(key) or "")
        match = _VERSION_RE.search(value)
        if match:
            # tag "latest-build"/"beta-build" sayi icermez; name "(vX.Y.Z)" icerir.
            if key == "tag_name" and "latest" in value.lower() and not re.search(r"\d", value):
                continue
            if key == "tag_name" and "beta-build" in value.lower() and not re.search(r"\d", value):
                continue
            version = match.group(1)
            if "beta" in value.lower() and "beta" not in version.lower():
                version = f"{version}-beta"
            return version
    for asset in release.get("assets") or []:
        asset_name = str(asset.get("name") or "")
        match = _VERSION_RE.search(asset_name)
        if match:
            version = match.group(1)
            if "beta" in asset_name.lower() and "beta" not in version.lower():
                version = f"{version}-beta"
            return version
    return ""


def find_setup_asset_url(release: dict) -> Optional[str]:
    """`*Setup.exe` varligini bul (onerilen kurucu). Yoksa None."""
    assets = release.get("assets") or []
    setup_candidates = [
        a for a in assets
        if str(a.get("name", "")).lower().endswith("setup.exe")
    ]
    if not setup_candidates:
        # Yedek: adi setup iceren herhangi bir .exe
        setup_candidates = [
            a for a in assets
            if str(a.get("name", "")).lower().endswith(".exe")
            and "setup" in str(a.get("name", "")).lower()
        ]
    if not setup_candidates:
        return None
    # En buyuk dosyayi tercih et (bos/golge assetleri ele).
    setup_candidates.sort(key=lambda a: int(a.get("size") or 0), reverse=True)
    url = setup_candidates[0].get("browser_download_url")
    return str(url) if url else None


def fetch_latest_release(timeout: int = REQUEST_TIMEOUT, channel: Optional[str] = None) -> dict:
    """Kanalin release JSON'unu indirir (beta -> `beta-build`, stabil -> `latest-build`)."""
    resolved = normalize_channel(channel) if channel is not None else get_update_channel()
    return _http_get_json(api_url_for_channel(resolved), timeout=timeout)


# ---------------------------------------------------------------------------
# Rolling-tag körlüğü: sürüm eşitse yayın zamanı karşılaştır
# ---------------------------------------------------------------------------

_PUBLISHED_AT_KEY = "installed_release_published_at"


def _parse_github_time(value: object) -> Optional[datetime]:
    """GitHub ISO-8601 zamanını UTC datetime'a çevirir (çevrilemezse None)."""
    text = str(value or "").strip()
    if not text:
        return None
    try:
        iso = text.replace("Z", "+00:00") if text.endswith(("Z", "z")) else text
        parsed = datetime.fromisoformat(iso)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except (ValueError, OverflowError):
        return None


def extract_release_published_at(release: dict) -> str:
    """Release/asset zaman damgalarından en yeniyi normalize ISO string döner.

    Rolling-tag (`latest-build`/`beta-build`) her derlemede yeniden yayınlanır;
    sürüm dizesi aynı kalsa bile `published_at` ilerler. Boş string = damga yok.
    """
    candidates: list[str] = []
    if isinstance(release, dict):
        for key in ("published_at", "created_at", "updated_at", "pushed_at"):
            value = release.get(key)
            if value:
                candidates.append(str(value))
        assets = release.get("assets") or []
        if isinstance(assets, list):
            for asset in assets:
                if isinstance(asset, dict) and asset.get("updated_at"):
                    candidates.append(str(asset.get("updated_at")))
    best: Optional[datetime] = None
    for raw in candidates:
        parsed = _parse_github_time(raw)
        if parsed is not None and (best is None or parsed > best):
            best = parsed
    if best is not None:
        return best.isoformat()
    for raw in candidates:
        if raw.strip():
            return raw.strip()
    return ""


def get_installed_published_at() -> Optional[str]:
    """Kurulu derlemenin yayın damgasını oku (yoksa None)."""
    try:
        from PyQt6.QtCore import QSettings
        value = QSettings("NeNgi", "NeNgiPDF").value(_PUBLISHED_AT_KEY, None)
    except Exception:
        return None
    text = str(value).strip() if value is not None else ""
    return text or None


def set_installed_published_at(published_at: str) -> None:
    """Kurulu derlemenin yayın damgasını kaydet (kurulum sonrası çağrılır)."""
    try:
        from PyQt6.QtCore import QSettings
        QSettings("NeNgi", "NeNgiPDF").setValue(
            _PUBLISHED_AT_KEY, (published_at or "").strip()
        )
    except Exception:
        pass


def check_for_update(
    current_version: Optional[str] = None,
    channel: Optional[str] = None,
) -> UpdateInfo:
    """Bloke edici denetim: release'i al, karsilastir, UpdateInfo dondur.

    UI thread'de dogrudan cagirmayin; UpdateCheckWorker kullanin.
    Hata durumunda UpdateCheckError yukseltir (graceful Turkce mesaj).
    `channel` verilmezse QSettings'teki 'update_channel' kullanilir.
    """
    local = (current_version or LOCAL_VERSION or "0.0.0").strip()
    resolved = normalize_channel(channel) if channel is not None else get_update_channel()
    release = fetch_latest_release(channel=resolved)
    remote = extract_remote_version(release)
    if not remote:
        raise UpdateCheckError(
            "Uzak sürüm bilgisi okunamadı. Lütfen daha sonra tekrar deneyin."
        )
    download_url = find_setup_asset_url(release)
    notes = str(release.get("body") or "")
    published_at = extract_release_published_at(release)
    if is_newer(local, remote):
        has_update = True
    elif compare_versions(local, remote) == 0 and published_at:
        # Rolling-tag körlüğü: sürüm dizesi aynı ama daha yeni bir derleme
        # yayınlanmış olabilir (published_at ilerlemişse yeni build var).
        baseline = get_installed_published_at()
        has_update = (baseline or "") != published_at
    else:
        has_update = False
    if has_update and not download_url:
        raise UpdateCheckError(
            f"Yeni sürüm ({remote}) bulundu ancak kurulum dosyası "
            "bulunamadı. Lütfen GitHub sayfasından el ile indirin."
        )
    return UpdateInfo(
        has_update=has_update,
        local_version=local,
        remote_version=remote,
        download_url=download_url,
        notes=notes,
        published_at=published_at,
    )


# ---------------------------------------------------------------------------
# Indirme + kurulum (stdlib)
# ---------------------------------------------------------------------------

def get_temp_installer_path(filename: str = "NeNgi_PDF_Setup.exe") -> str:
    safe = os.path.basename(filename) or "NeNgi_PDF_Setup.exe"
    return os.path.join(tempfile.gettempdir(), safe)


def _safe_remove(path: str) -> None:
    """Yarım/bozuk dosyayı sessizce sil (yoksa no-op)."""
    try:
        if path and os.path.isfile(path):
            os.remove(path)
    except OSError:
        pass


def download_file(
    url: str,
    dest_path: str,
    progress_callback: Optional[Callable[[int, int], None]] = None,
    timeout: int = 60,
    chunk_size: int = 1024 * 64,
    min_size: int = MIN_INSTALLER_BYTES,
    should_cancel: Optional[Callable[[], bool]] = None,
) -> str:
    """URL'yi `.part` dosyasına indirip atomik rename ile dest_path'e taşır.

    Bütünlük kuralları:
    - Content-Length biliniyorsa eksik indirme reddedilir.
    - `min_size` (varsayılan 10 MB) altındaki dosyalar bozuk sayılıp silinir.
    - Hata/iptal durumunda yarım `.part` dosyası silinir; asla yarım exe
      hedef yola taşınmaz. Hata -> UpdateCheckError.
    """
    part_path = dest_path + ".part"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    downloaded = 0
    total = 0
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            getheader = getattr(resp, "getheader", None)
            if callable(getheader):
                try:
                    total = int(getheader("Content-Length") or 0)
                except (TypeError, ValueError):
                    total = 0
            os.makedirs(os.path.dirname(os.path.abspath(dest_path)), exist_ok=True)
            with open(part_path, "wb") as f:
                while True:
                    if should_cancel is not None:
                        try:
                            cancelled = bool(should_cancel())
                        except DownloadCancelledError:
                            raise
                        except Exception:
                            cancelled = False
                        if cancelled:
                            raise DownloadCancelledError(
                                "İndirme iptal edildi. Yarım dosya temizlendi."
                            )
                    chunk = resp.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback:
                        try:
                            progress_callback(downloaded, total)
                        except DownloadCancelledError:
                            raise
                        except Exception:
                            pass
    except DownloadCancelledError:
        _safe_remove(part_path)
        raise
    except (urllib.error.URLError, OSError, TimeoutError) as e:
        _safe_remove(part_path)
        raise UpdateCheckError(
            "Kurulum dosyası indirilemedi. İnternet bağlantınızı "
            "kontrol edip tekrar deneyin."
        ) from e
    if total > 0 and downloaded != total:
        _safe_remove(part_path)
        raise UpdateCheckError(
            "Kurulum dosyası eksik indirildi (%s/%s bayt). "
            "Lütfen tekrar deneyin." % (downloaded, total)
        )
    try:
        size = os.path.getsize(part_path)
    except OSError as e:
        _safe_remove(part_path)
        raise UpdateCheckError("İndirilen dosya doğrulanamadı.") from e
    if size <= 0:
        _safe_remove(part_path)
        raise UpdateCheckError(
            "İndirilen kurulum dosyası bozuk (0 bayt). Lütfen tekrar deneyin."
        )
    if min_size and min_size > 0 and size < min_size:
        _safe_remove(part_path)
        raise UpdateCheckError(
            "İndirilen kurulum dosyası eksik/bozuk görünüyor "
            "(%s bayt, en az %s bayt bekleniyordu). Lütfen tekrar deneyin."
            % (size, min_size)
        )
    try:
        os.replace(part_path, dest_path)
    except OSError as e:
        _safe_remove(part_path)
        raise UpdateCheckError("İndirilen dosya doğrulanamadı.") from e
    return dest_path


def launch_silent_install(installer_path: str) -> None:
    """NSIS sessiz kurulumu baslatir ("/S"). Donmez; hata -> UpdateCheckError.

    Windows'ta UAC uyumu icin "runas" ile yükseltilmiş baslatilir
    (ctypes ShellExecuteW); kullanici UAC'yi reddederse "yönetici gerekli"
    mesaji yükseltilir.
    """
    if not installer_path or not os.path.isfile(installer_path):
        raise UpdateCheckError("Kurulum dosyası bulunamadı.")
    if os.path.getsize(installer_path) <= 0:
        raise UpdateCheckError("Kurulum dosyası bozuk (0 bayt).")
    try:
        if sys.platform.startswith("win"):
            import ctypes

            SW_SHOWNORMAL = 1
            rc = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", installer_path, "/S", None, SW_SHOWNORMAL
            )
            if int(rc or 0) <= 32:
                raise UpdateCheckError(
                    "Kurulum için yönetici izni gerekli. Lütfen açılan "
                    "kullanıcı hesabı denetimi (UAC) penceresinde 'Evet'e basın."
                )
        else:
            subprocess.Popen([installer_path, "/S"], close_fds=True)
    except UpdateCheckError:
        raise
    except OSError as e:
        raise UpdateCheckError("Kurulum başlatılamadı: %s" % e) from e
    except Exception as e:
        raise UpdateCheckError("Kurulum başlatılamadı: %s" % e) from e


# ---------------------------------------------------------------------------
# UpdateChecker vitrini + QThread worker'lar (UI ile ayni sinif kullanilir)
# ---------------------------------------------------------------------------

class UpdateChecker:
    """Tek giris noktasi: denetle -> indir -> sessiz kur.

    main_window.py ve settings_dialog.py ikisi de bu sinifi kullanir.
    Ag cagrilari bloke edicidir; UI'da UpdateCheckWorker/UpdateDownloadWorker
    ile (QThread) cagirin.
    """

    def __init__(self, current_version: Optional[str] = None, channel: Optional[str] = None):
        self.current_version = (current_version or LOCAL_VERSION or "0.0.0").strip()
        self.channel = normalize_channel(channel) if channel is not None else get_update_channel()

    def check(self) -> UpdateInfo:
        return check_for_update(self.current_version, channel=self.channel)

    def download(
        self,
        url: str,
        dest_path: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        min_size: int = MIN_INSTALLER_BYTES,
        should_cancel: Optional[Callable[[], bool]] = None,
    ) -> str:
        filename = os.path.basename(url.split("?")[0]) or "NeNgi_PDF_Setup.exe"
        dest = dest_path or get_temp_installer_path(filename)
        return download_file(
            url,
            dest,
            progress_callback=progress_callback,
            min_size=min_size,
            should_cancel=should_cancel,
        )

    def install_silently(self, installer_path: str) -> None:
        launch_silent_install(installer_path)


def shutdown_app_for_update(source_widget=None) -> None:
    """Kurulum öncesi uygulamayı sessiz kapanışa hazırla.

    - Ana pencerede `_updating_for_restart` bayrağı koyar (closeEvent tray'e
      gömülmeden kabul edilir).
    - Tray agent'ı durdurur (`_is_quitting=True` + simgeyi gizler).
    - Single-instance QLocalServer'ı kapatıp soket adını temizler; aksi halde
      kurucu dosya kilidine takılabilir / eski süreç hayatta kalır.
    Hiçbir adımda exception yükseltmez.
    """
    main_win = None
    try:
        if source_widget is not None:
            cur = source_widget
            seen_ids: set[int] = set()
            while cur is not None and id(cur) not in seen_ids:
                seen_ids.add(id(cur))
                if hasattr(cur, "tray_agent") or hasattr(cur, "_updating_for_restart"):
                    main_win = cur
                    break
                try:
                    cur = cur.parent()
                except Exception:
                    cur = None
            if main_win is None:
                try:
                    cand = source_widget.window()
                    if cand is not None and cand is not source_widget:
                        main_win = cand
                except Exception:
                    pass
        if main_win is None:
            try:
                from PyQt6.QtWidgets import QApplication

                app = QApplication.instance()
                if app is not None:
                    for top in app.topLevelWidgets():
                        if hasattr(top, "tray_agent"):
                            main_win = top
                            break
            except Exception:
                pass
    except Exception:
        pass
    if main_win is None:
        return
    try:
        setattr(main_win, "_updating_for_restart", True)
    except Exception:
        pass
    tray = getattr(main_win, "tray_agent", None)
    if tray is not None:
        try:
            setattr(tray, "_is_quitting", True)
        except Exception:
            pass
        try:
            icon = getattr(tray, "tray_icon", None)
            if icon is not None:
                try:
                    icon.hide()
                except Exception:
                    pass
                try:
                    setattr(tray, "tray_icon", None)
                except Exception:
                    pass
        except Exception:
            pass
    # Single-instance dinleyicisi: önce bilinen öznitelikler, sonra nesne ağacı.
    try:
        for attr in (
            "instance_mgr",
            "instance_manager",
            "single_instance_mgr",
            "single_instance_manager",
            "_instance_mgr",
            "_single_instance_mgr",
        ):
            mgr = getattr(main_win, attr, None)
            srv = getattr(mgr, "server", None) if mgr is not None else None
            if srv is not None:
                try:
                    srv.close()
                except Exception:
                    pass
                try:
                    setattr(mgr, "server", None)
                except Exception:
                    pass
    except Exception:
        pass
    try:
        from PyQt6.QtNetwork import QLocalServer

        servers: list = []
        try:
            servers.extend(list(main_win.findChildren(QLocalServer)))
        except Exception:
            pass
        try:
            from PyQt6.QtWidgets import QApplication

            app = QApplication.instance()
            if app is not None:
                for srv in app.findChildren(QLocalServer):
                    if srv not in servers:
                        servers.append(srv)
        except Exception:
            pass
        for srv in servers:
            try:
                srv.close()
            except Exception:
                pass
        try:
            from nengi.core.single_instance import IPC_SOCKET_NAME

            try:
                QLocalServer.removeServer(IPC_SOCKET_NAME)
            except Exception:
                pass
        except Exception:
            pass
    except Exception:
        pass


if _QT_AVAILABLE:  # pragma: no cover - GUI ortami gerektirir

    class UpdateCheckWorker(QThread):
        """Arka planda surum denetimi yapar (UI donmaz)."""

        finished = pyqtSignal(object)  # UpdateInfo
        failed = pyqtSignal(str)       # Turkce hata mesaji

        def __init__(self, current_version: Optional[str] = None, channel: Optional[str] = None, parent=None):
            super().__init__(parent)
            self._checker = UpdateChecker(current_version, channel=channel)

        def run(self):  # type: ignore[override]
            try:
                info = self._checker.check()
            except UpdateCheckError as e:
                self.failed.emit(str(e))
            except Exception as e:  # beklenmeyen: graceful'a cevir
                self.failed.emit("Güncelleme denetlenemedi: %s" % e)
            else:
                self.finished.emit(info)

    class UpdateDownloadWorker(QThread):
        """Arka planda Setup.exe indirir, ilerleme yayinlar."""

        progress = pyqtSignal(int, int)  # (indirilen, toplam)
        finished = pyqtSignal(str)       # yerel dosya yolu
        failed = pyqtSignal(str)         # Turkce hata mesaji

        def __init__(self, url: str, dest_path: Optional[str] = None, parent=None):
            super().__init__(parent)
            self._url = url
            self._checker = UpdateChecker()
            self._dest_path = dest_path
            self._cancelled = False

        def cancel(self) -> None:
            """Kullanıcı iptali: yarım `.part` dosyası temizlenir."""
            self._cancelled = True

        def _emit_progress(self, downloaded: int, total: int) -> None:
            if self._cancelled:
                raise DownloadCancelledError(
                    "İndirme iptal edildi. Yarım dosya temizlendi."
                )
            try:
                self.progress.emit(downloaded, total)
            except Exception:
                pass

        def run(self):  # type: ignore[override]
            try:
                path = self._checker.download(
                    self._url,
                    dest_path=self._dest_path,
                    progress_callback=self._emit_progress,
                    should_cancel=lambda: self._cancelled,
                )
            except UpdateCheckError as e:
                self.failed.emit(str(e))
            except Exception as e:
                self.failed.emit("İndirme başarısız: %s" % e)
            else:
                self.finished.emit(path)

else:  # pragma: no cover
    class UpdateCheckWorker:  # type: ignore
        def __init__(self, *a, **k):
            raise RuntimeError("PyQt6 yok: worker kullanılamaz.")

    class UpdateDownloadWorker:  # type: ignore
        def __init__(self, *a, **k):
            raise RuntimeError("PyQt6 yok: worker kullanılamaz.")
