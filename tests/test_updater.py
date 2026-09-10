"""Updater surum-karsilastirma testleri (ag mock'lu)."""

import urllib.error

from nengi.core import updater
from nengi.core.updater import UpdateCheckError, check_for_update


def _release(version: str):
    return {
        "tag_name": "latest-build",
        "name": f"NeNgi PDF – Son Derleme (v{version})",
        "body": "yenilikler",
        "assets": [
            {
                "name": f"NeNgi_PDF_v{version}_Setup.exe",
                "browser_download_url": f"https://github.com/turkerpro/NeNgi-PDF/releases/download/latest-build/NeNgi_PDF_v{version}_Setup.exe",
                "size": 10_000_000,
            },
            {
                "name": f"NeNgi_PDF_v{version}_Portable.exe",
                "browser_download_url": "https://example.com/portable.exe",
                "size": 9_000_000,
            },
        ],
    }


def test_yeni_surum_algilanir(monkeypatch):
    monkeypatch.setattr(updater, "fetch_latest_release", lambda timeout=12: _release("2.1.0"))
    info = check_for_update("2.0.0")
    assert info.has_update is True
    assert info.local_version == "2.0.0"
    assert info.remote_version == "2.1.0"
    assert info.download_url is not None and "Setup.exe" in info.download_url


def test_guncel_surumde_guncelleme_yok(monkeypatch):
    monkeypatch.setattr(updater, "fetch_latest_release", lambda timeout=12: _release("2.0.0"))
    info = check_for_update("2.0.0")
    assert info.has_update is False
    assert info.remote_version == "2.0.0"


def test_ag_hatasinda_graceful_mesaj(monkeypatch):
    def _boom(request, timeout=12):
        raise urllib.error.URLError("no network")

    monkeypatch.setattr(updater.urllib.request, "urlopen", _boom)
    try:
        check_for_update("2.0.0")
    except UpdateCheckError as e:
        assert "nternet" in str(e) or "ula" in str(e)
    else:
        raise AssertionError("UpdateCheckError bekleniyordu")
