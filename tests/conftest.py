import shutil
from pathlib import Path

import pytest


def pytest_sessionstart(session: pytest.Session) -> None:
    """Hook that runs before test collection.

    Ensures static files from ui/src are copied to src/meitav_view/static if missing.
    """
    repo_root = Path(__file__).resolve().parent.parent
    static_dir = repo_root / "src" / "meitav_view" / "static"
    ui_src_dir = repo_root / "ui" / "src"
    index_file = static_dir / "index.html"

    if not index_file.exists() and ui_src_dir.exists():
        static_dir.mkdir(parents=True, exist_ok=True)
        shutil.copytree(ui_src_dir, static_dir, dirs_exist_ok=True)
