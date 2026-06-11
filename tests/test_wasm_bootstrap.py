"""Guard: the WASM bootstrap's wheel name must track the package version.

``app.py`` ``_wasm_bootstrap`` micropip-installs a *versioned* wheel filename
(``raven_matrix-<version>-py3-none-any.whl``) that the Pages deploy bundles into
the export's ``assets/``. If the package version bumps but the bootstrap string is
not updated in lockstep, the in-browser install 404s and the app never loads. This
test fails loudly on that drift (the wheel name is not derivable at runtime in the
browser, so it is pinned in the source and guarded here instead).
"""

from __future__ import annotations

from pathlib import Path

from raven_matrix import __version__


def test_bootstrap_wheel_name_tracks_version() -> None:
    app_src = (Path(__file__).resolve().parents[1] / "app.py").read_text()
    expected = f"raven_matrix-{__version__}-py3-none-any.whl"
    assert expected in app_src, (
        f"app.py WASM bootstrap must micropip-install {expected!r}; "
        "update the bootstrap string when the package version changes."
    )
