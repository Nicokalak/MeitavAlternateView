from collections.abc import Iterator
from pathlib import Path

import pytest
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

from meitav_view import app as app_module


@pytest.fixture(autouse=True)
def static_tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    """Point the app at a minimal built-UI tree so tests never depend on a UI build."""
    (tmp_path / "assets").mkdir()
    (tmp_path / "favicon").mkdir()
    (tmp_path / "index.html").write_text("<!doctype html><title>index</title>")
    (tmp_path / "401.html").write_text("<!doctype html><title>401</title>")
    (tmp_path / "assets" / "app-abc123.js").write_text("export {};")
    (tmp_path / "favicon" / "favicon.svg").write_text("<svg xmlns='http://www.w3.org/2000/svg'/>")

    monkeypatch.setattr(app_module, "STATIC_DIR", tmp_path)
    for route in app_module.app.routes:
        if isinstance(route, Mount) and isinstance(route.app, StaticFiles) and route.name in {"assets", "favicon"}:
            mounted = route.app
            monkeypatch.setattr(mounted, "directory", tmp_path / route.name)
            monkeypatch.setattr(mounted, "all_directories", [tmp_path / route.name])
    yield tmp_path
