"""SVG rendering for the Raven-matrix port.

This package is intentionally empty of re-exports.  Import the SVG renderer via
``raven_matrix.render.svg`` and the optional raster backend (the ``raster``
extra) via ``raven_matrix.render.raster``.

Import-hygiene contract (Phase-8 WASM dependency, asserted by
``tests/test_import_hygiene.py``): this module must NOT import or re-export
``render.raster`` or ``rasterise``, and ``render.svg`` must not import
``resvg_py``.  That keeps ``import raven_matrix.render`` / ``render.svg`` free of
the optional raster dependency.
"""
