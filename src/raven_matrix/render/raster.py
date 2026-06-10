"""Optional SVG→PNG rasterisation (the ``raster`` extra).

The canonical render format is SVG (``render.svg``); this module "renders down"
an SVG string to PNG bytes on demand via ``resvg_py`` (a self-contained Rust
``resvg`` wheel, MIT).  It lives behind the ``raster`` optional dependency.

Import-hygiene contract (Phase-8 WASM dependency, asserted by
``tests/test_import_hygiene.py`` in Phase 8): the ``resvg_py`` import lives
*inside* ``rasterise``, never at module scope, and ``render/__init__.py`` must
not re-export this module.  So ``import raven_matrix.render`` and
``import raven_matrix.render.svg`` stay free of the optional backend, and
``raster`` is reachable only via the explicit ``raven_matrix.render.raster``
path.  Treat this as a hard rule, not a stylistic preference.
"""

from __future__ import annotations

_MISSING_BACKEND_HINT = (
    "The 'raster' extra is required to rasterise SVG to PNG. "
    "Install it with: pip install 'raven-matrix[raster]' (or uv sync --all-extras)."
)


def rasterise(svg: str) -> bytes:
    """Render an SVG document string to PNG bytes.

    Args:
        svg: A complete SVG document (e.g. the output of
            ``render.svg.render_matrix_svg``).

    Returns:
        PNG-encoded image bytes (begins with the PNG magic ``\\x89PNG\\r\\n\\x1a\\n``).

    Raises:
        ImportError: if the optional ``raster`` extra (``resvg_py``) is not
            installed.  The message hints at the install command.
    """
    try:
        import resvg_py
    except ImportError as exc:  # extra not installed
        raise ImportError(_MISSING_BACKEND_HINT) from exc

    return bytes(resvg_py.svg_to_bytes(svg_string=svg))
