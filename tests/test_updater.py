"""Updater surum-karsilastirma testleri (ag mock'lu)."""

import urllib.error

from nengi.core import updater
from nengi.core.updater import (
    UpdateCheckError,
    api_url_for_channel,
    check_for_update,
    compare_versions,
    normalize_channel,
    tag_for_channel,
)


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
    monkeypatch.setattr(updater, "fetch_latest_release", lambda timeout=12, **kwargs: _release("2.1.0"))
    info = check_for_update("2.0.0")
    assert info.has_update is True
    assert info.local_version == "2.0.0"
    assert info.remote_version == "2.1.0"
    assert info.download_url is not None and "Setup.exe" in info.download_url


def test_guncel_surumde_guncelleme_yok(monkeypatch):
    monkeypatch.setattr(updater, "fetch_latest_release", lambda timeout=12, **kwargs: _release("2.0.0"))
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


def test_kanal_tag_eslemesi():
    assert tag_for_channel("beta") == "beta-build"
    assert tag_for_channel("stabil") == "latest-build"
    assert normalize_channel("bilinmeyen") == "beta"


def test_beta_tag_url():
    assert api_url_for_channel("beta").endswith("/releases/tags/beta-build")
    assert api_url_for_channel("stabil").endswith("/releases/tags/latest-build")


def test_beta_soneki_karsilastirma():
    assert compare_versions("2.1.0-beta", "2.1.0") == -1
    assert compare_versions("2.1.0", "2.1.0-beta") == 1
    assert compare_versions("2.1.0-beta", "2.1.0-beta") == 0
    assert compare_versions("2.0.0", "2.1.0-beta") == -1


def test_beta_kanali_beta_releasesini_sorgular(monkeypatch):
    seen = {}

    def _fake_get(url, timeout=12):
        seen["url"] = url
        return _release("2.1.0-beta")

    monkeypatch.setattr(updater, "_http_get_json", _fake_get)
    info = check_for_update("2.0.0", channel="beta")
    assert "beta-build" in seen["url"]
    assert info.has_update is True
    assert info.remote_version == "2.1.0-beta"


def test_stabil_kanal_latest_build_sorgular(monkeypatch):
    seen = {}

    def _fake_get(url, timeout=12):
        seen["url"] = url
        return _release("2.0.0")

    monkeypatch.setattr(updater, "_http_get_json", _fake_get)
    info = check_for_update("2.0.0", channel="stabil")
    assert "latest-build" in seen["url"]
    assert info.has_update is False
