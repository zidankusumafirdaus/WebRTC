import importlib
import sys


def _bootstrap_test_env(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-jwt-secret")
    monkeypatch.setenv("MAX_FILE_SIZE_MB", "10")
    monkeypatch.setenv("ALLOWED_MIME_PREFIXES", "image/")
    monkeypatch.setenv("ALLOWED_MIME_FULL", "image/png")
    monkeypatch.setenv("REPORT_ALLOWED_MIME_FULL", "application/pdf")

    for module_name in ["config", "apps", "apps.__init__"]:
        if module_name in sys.modules:
            del sys.modules[module_name]

    import config

    importlib.reload(config)


def test_health_endpoint(monkeypatch):
    _bootstrap_test_env(monkeypatch)
    from apps import create_app

    app = create_app()
    client = app.test_client()

    response = client.get("/api/health/")

    assert response.status_code == 200
    payload = response.get_json()
    assert "redis" in payload
    assert "configured" in payload["redis"]
