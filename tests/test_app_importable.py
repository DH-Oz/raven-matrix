"""Smoke test for the marimo app module (Phase 7, Task 2).

``app.py`` is a marimo edge layer; its reactive behaviour is verified by UAT
(``marimo edit app.py``), not automated tests. This smoke test only guards CI
against syntax/import breakage: importing the module must succeed and expose a
marimo ``App`` instance named ``app``.

marimo lives in the optional ``ui`` extra and is absent from the default test
environment. The test SKIPS cleanly when marimo is missing (so the default
``uv run pytest`` stays green) and RUNS the real assertions under
``uv run --extra ui pytest`` -- the same guard pattern Task 1's ``test_cli.py``
uses for the ``raster`` extra.
"""

from __future__ import annotations

import importlib
import importlib.util
from pathlib import Path

import pytest

# Skip the whole module unless marimo (the `ui` extra) is installed. The app
# module imports marimo at top level, so without the extra the import would
# error rather than skip; importorskip turns the absence into a clean skip.
pytest.importorskip("marimo", reason="requires the 'ui' extra (marimo)")

import marimo  # noqa: E402  (imported after the importorskip guard)

# app.py lives at the REPO ROOT (two parents up from this test file), not in the
# package, so `marimo edit app.py` / `marimo export html-wasm app.py` are clean.
_APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


def _load_app_module():
    """Import the repo-root ``app.py`` by file path (it is not on sys.path)."""
    spec = importlib.util.spec_from_file_location("raven_matrix_app", _APP_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_app_file_exists() -> None:
    assert _APP_PATH.is_file()


def test_app_module_imports_and_exposes_app() -> None:
    module = _load_app_module()

    # The module parsed and executed; it exposes a marimo App named `app`, which
    # is what `marimo edit app.py` / `marimo export html-wasm app.py` consume.
    assert hasattr(module, "app")
    assert isinstance(module.app, marimo.App)
