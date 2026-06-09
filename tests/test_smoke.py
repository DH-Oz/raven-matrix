"""Greenfield smoke test: the package imports and exposes its version.

This exists so pytest (and CI) have a real green check before any feature
code lands. It is replaced in spirit by Phase 2's first real tests.
"""

import raven_matrix


def test_package_imports_with_version() -> None:
    assert raven_matrix.__version__ == "0.1.0"
