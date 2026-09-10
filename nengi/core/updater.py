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

_VERSION_RE = re.compile(r"v?(\d+(?:\.\d+){0,3})")


class UpdateCheckError(Exception):
    """Kullaniciya gosterilebilir, Turkce güncelleme hatasi."""


@dataclass
class UpdateInfo:
    has_update: bool
    local_version: str
    remote_version: str
    download_url: Optional[str]
    notes: str = ""


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
    has_update = is_newer(local, remote)
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
    )


# ---------------------------------------------------------------------------
# Indirme + kurulum (stdlib)
# ---------------------------------------------------------------------------

def get_temp_installer_path(filename: str = "NeNgi_PDF_Setup.exe") -> str:
    safe = os.path.basename(filename) or "NeNgi_PDF_Setup.exe"
    return os.path.join(tempfile.gettempdir(), safe)


def download_file(
    url: str,
    dest_path: str,
    progress_callback: Optional[Callable[[int, int], None]] = None,
    timeout: int = 60,
    chunk_size: int = 1024 * 64,
) -> str:
    """URL'yi dest_path'e indirir, boyutu dondurur. Hata -> UpdateCheckError."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            total = int(resp.getheader("Content-Length") or 0)
            downloaded = 0
            os.makedirs(os.path.dirname(os.path.abspath(dest_path)), exist_ok=True)
            with open(dest_path, "wb") as f:
                while True:
                    chunk = resp.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback:
                        try:
                            progress_callback(downloaded, total)
                        except Exception:
                            pass
    except (urllib.error.URLError, OSError, TimeoutError) as e:
        raise UpdateCheckError(
            "Kurulum dosyası indirilemedi. İnternet bağlantınızı "
            "kontrol edip tekrar deneyin."
        ) from e
    try:
        size = os.path.getsize(dest_path)
    except OSError as e:
        raise UpdateCheckError("İndirilen dosya doğrulanamadı.") from e
    if size <= 0:
        try:
            os.remove(dest_path)
        except OSError:
            pass
        raise UpdateCheckError(
            "İndirilen kurulum dosyası bozuk (0 bayt). Lütfen tekrar deneyin."
        )
    return dest_path


def launch_silent_install(installer_path: str) -> None:
    """NSIS sessiz kurulumu baslatir ("/S"). Donmez; hata -> UpdateCheckError."""
    if not installer_path or not os.path.isfile(installer_path):
        raise UpdateCheckError("Kurulum dosyası bulunamadı.")
    if os.path.getsize(installer_path) <= 0:
        raise UpdateCheckError("Kurulum dosyası bozuk (0 bayt).")
    try:
        if sys.platform.startswith("win"):
            # Ayrı konsolsuz süreç; kurucu eski EXE'yi kapatıp üzerine yazar.
            subprocess.Popen(
                [installer_path, "/S"],
                close_fds=True,
                creationflags=getattr(subprocess, "DETACHED_PROCESS", 0),
            )
        else:
            subprocess.Popen([installer_path, "/S"], close_fds=True)
    except OSError as e:
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
    ) -> str:
        filename = os.path.basename(url.split("?")[0]) or "NeNgi_PDF_Setup.exe"
        dest = dest_path or get_temp_installer_path(filename)
        return download_file(url, dest, progress_callback=progress_callback)

    def install_silently(self, installer_path: str) -> None:
        launch_silent_install(installer_path)


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

        def run(self):  # type: ignore[override]
            try:
                path = self._checker.download(
                    self._url,
                    dest_path=self._dest_path,
                    progress_callback=lambda d, t: self.progress.emit(d, t),
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
