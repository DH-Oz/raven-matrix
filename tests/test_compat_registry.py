"""Tests for CompatFlags + the self-enforcing compat registry (Task 1).

AC6.2: every CompatFlags field must have exactly one documented row in
docs/compat-registry.md, and no registry row may name a non-existent flag.
This keeps the growing registry honest: adding a flag without documenting it
(or vice versa) fails the build.
"""

from __future__ import annotations

import dataclasses
import pathlib
import re

import pytest

from raven_matrix.compat import DEFAULT_FLAGS, CompatFlags

_REGISTRY_PATH = (
    pathlib.Path(__file__).resolve().parents[1] / "docs" / "compat-registry.md"
)


def _registry_flag_names() -> set[str]:
    """Extract the flag name from each Markdown table data row.

    A registry row looks like ``| line_shape_enabled | … | … | … |``; the first
    cell is the flag name verbatim. Header and separator rows (which contain no
    CompatFlags field name) are naturally excluded by matching field names.
    """
    text = _REGISTRY_PATH.read_text(encoding="utf-8")
    names: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        first_cell = stripped.strip("|").split("|", 1)[0].strip()
        # A flag name is a bare identifier; skip header/separator cells.
        if re.fullmatch(r"[a-z_][a-z0-9_]*", first_cell):
            names.add(first_cell)
    return names


# ---------------------------------------------------------------------------
# CompatFlags defaults
# ---------------------------------------------------------------------------


def test_compatflags_defaults_are_both_false() -> None:
    flags = CompatFlags()
    assert flags.line_shape_enabled is False
    assert flags.relocate_correct_answer is False


def test_default_flags_singleton_matches_defaults() -> None:
    assert CompatFlags() == DEFAULT_FLAGS


def _set_attr(target: object, name: str, value: object) -> None:
    """Dynamic attribute set, isolated so the field name is not a literal.

    Routing the mutation through a helper keeps ty from resolving the
    (read-only) CompatFlags field statically, and keeps ruff's B010 quiet
    (the attribute name is a parameter, not a literal at the call site), while
    still triggering the frozen dataclass's runtime FrozenInstanceError.
    """
    setattr(target, name, value)


def test_compatflags_is_frozen() -> None:
    flags = CompatFlags()
    with pytest.raises(dataclasses.FrozenInstanceError):
        _set_attr(flags, "line_shape_enabled", True)


# ---------------------------------------------------------------------------
# AC6.2 — registry completeness (self-enforcing)
# ---------------------------------------------------------------------------


def test_registry_exists() -> None:
    assert _REGISTRY_PATH.is_file(), f"missing registry at {_REGISTRY_PATH}"


def test_every_compatflag_field_has_a_registry_row() -> None:
    """Each dataclass field of CompatFlags appears as a documented row."""
    field_names = {f.name for f in dataclasses.fields(CompatFlags)}
    documented = _registry_flag_names()
    missing = field_names - documented
    assert not missing, f"flags missing from registry: {sorted(missing)}"


def test_no_registry_row_names_a_nonexistent_flag() -> None:
    """No registry row may name a flag absent from CompatFlags."""
    field_names = {f.name for f in dataclasses.fields(CompatFlags)}
    documented = _registry_flag_names()
    stale = documented - field_names
    assert not stale, f"registry rows for non-existent flags: {sorted(stale)}"
