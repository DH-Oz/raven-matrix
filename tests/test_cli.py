"""CLI tests via typer's ``CliRunner`` (Phase 7, Task 1).

The CLI is the imperative edge layer: it parses flags, calls the pure core
(``config_from_controls`` / ``build_from_code`` / ``build`` / ``label`` /
``build_pass_map``), and writes SVG/PNG/text. These tests exercise the edge
behaviour -- exit codes, well-formed output, error messages -- not the core
generation (covered in Phase 4). Error messages are written to stderr and read via
``result.stderr``; primary output goes to stdout (``result.stdout``).

The ``--png`` magic-bytes assertion needs the optional ``raster`` extra
(``resvg_py``); it is skipped when the backend is absent (so the default
``uv run pytest`` stays green) and runs under ``--all-extras``.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
from typer.testing import CliRunner

from raven_matrix.cli import app

runner = CliRunner()

_RASTER_AVAILABLE = importlib.util.find_spec("resvg_py") is not None
_PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def test_build_from_code_emits_svg() -> None:
    result = runner.invoke(app, ["build", "--code", "A1", "--seed", "0"])

    assert result.exit_code == 0
    assert "<svg" in result.stdout
    assert "</svg>" in result.stdout


def test_build_from_code_prints_structure_code() -> None:
    result = runner.invoke(app, ["build", "--code", "A1", "--seed", "0"])

    assert result.exit_code == 0
    # The Structure code is reported (the GUI "explanation" equivalent); it goes
    # to stderr so stdout stays a clean SVG document for piping.
    assert "A1" in result.stderr


def test_build_explicit_flags_matches_code_build() -> None:
    from_code = runner.invoke(app, ["build", "--code", "A1", "--seed", "0"])
    from_flags = runner.invoke(
        app,
        [
            "build",
            "--relation",
            "shape_repetition",
            "--direction",
            "horizontal",
            "--layers",
            "1",
            "--position",
            "1",
            "--seed",
            "0",
        ],
    )

    assert from_code.exit_code == 0
    assert from_flags.exit_code == 0
    # An explicit-flags A1 build is equivalent to the --code A1 build at the same
    # seed: identical SVG.
    assert from_flags.stdout == from_code.stdout


def test_build_with_supplemental_flag() -> None:
    result = runner.invoke(
        app,
        [
            "build",
            "--relation",
            "shape_repetition",
            "--direction",
            "horizontal",
            "--supplemental",
            "rotation:vertical",
            "--seed",
            "0",
        ],
    )

    assert result.exit_code == 0
    assert "<svg" in result.stdout


def test_build_answers_sheet() -> None:
    result = runner.invoke(
        app, ["build", "--code", "A1", "--seed", "0", "--answers"]
    )

    assert result.exit_code == 0
    # The answer sheet has a black background (render_answers_svg).
    assert 'fill="black"' in result.stdout


def test_build_writes_to_out_path(tmp_path) -> None:
    out = tmp_path / "matrix.svg"
    result = runner.invoke(
        app, ["build", "--code", "A1", "--seed", "0", "--out", str(out)]
    )

    assert result.exit_code == 0
    assert out.read_text(encoding="utf-8").startswith("<svg")


def test_build_malformed_code_exits_nonzero() -> None:
    result = runner.invoke(app, ["build", "--code", "Q9", "--seed", "0"])

    assert result.exit_code != 0
    assert result.stdout == ""  # no half-written SVG on stdout
    # A clear, actionable error -- prefixed "error:" and naming the offending
    # token (the 'Q' that no relation letter matches), not a raw traceback.
    assert result.stderr.startswith("error:")
    assert "Q" in result.stderr
    assert "Traceback" not in result.stderr


@pytest.mark.skipif(
    not _RASTER_AVAILABLE, reason="requires the 'raster' extra (resvg_py)"
)
def test_build_png_emits_magic_bytes(tmp_path) -> None:
    out = tmp_path / "matrix.png"
    result = runner.invoke(
        app, ["build", "--code", "A1", "--seed", "0", "--png", "--out", str(out)]
    )

    assert result.exit_code == 0
    assert out.read_bytes().startswith(_PNG_MAGIC)


def test_oracle_known_code_prints_rows() -> None:
    result = runner.invoke(app, ["oracle", "--code", "A1"])

    assert result.exit_code == 0
    # Every oracle row for A1 names a stimulus and its correct answer.
    assert "A1" in result.stdout
    assert "A1_1" in result.stdout  # a Stimulus Name under the A1 code


def test_oracle_known_code_reports_round_trip_status() -> None:
    result = runner.invoke(app, ["oracle", "--code", "A1"])

    assert result.exit_code == 0
    lowered = result.stdout.lower()
    assert "pass" in lowered or "exact" in lowered


def test_oracle_unknown_code_reports_not_found() -> None:
    result = runner.invoke(app, ["oracle", "--code", "ZZ9"])

    assert result.exit_code != 0
    assert "not found" in result.stderr.lower()


# ---------------------------------------------------------------------------
# Finding 1: graceful error when the oracle CSV is missing
# ---------------------------------------------------------------------------


def test_oracle_missing_csv_exits_1_with_actionable_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When the oracle CSV cannot be found, exit 1 with an actionable message.

    The resolver (_oracle_csv_path) is monkeypatched to return a path that
    does not exist so the real data/ravens_oracle.csv is never touched.
    """
    import raven_matrix.cli as cli_module

    nonexistent = Path("/tmp/raven_matrix_test_no_such_file_ravens_oracle.csv")
    monkeypatch.setattr(cli_module, "_oracle_csv_path", lambda: nonexistent)

    result = runner.invoke(app, ["oracle", "--code", "A1"])

    assert result.exit_code == 1
    assert result.stdout == ""  # stdout must be clean
    assert "tools/extract_oracle.py" in result.stderr


# ---------------------------------------------------------------------------
# Finding 2: --layers 2 produces a well-formed SVG
# ---------------------------------------------------------------------------


def test_build_two_layers_via_flag() -> None:
    """--layers 2 repeats the same relation across two identical layers."""
    result = runner.invoke(
        app,
        [
            "build",
            "--relation",
            "shape_repetition",
            "--direction",
            "horizontal",
            "--layers",
            "2",
            "--position",
            "1",
            "--seed",
            "0",
        ],
    )

    assert result.exit_code == 0
    assert "<svg" in result.stdout
    assert "</svg>" in result.stdout
    # The Structure code on stderr must reflect two layers: two relation letters.
    # A1A1 or A1 repeated — either way the code contains "A1" twice, or the
    # reported Structure line contains at least 4 characters encoding two layers.
    assert "Structure:" in result.stderr
    structure_line = next(
        line for line in result.stderr.splitlines() if line.startswith("Structure:")
    )
    code_part = structure_line.split(":", 1)[1].strip()
    # Two-layer codes are always longer than a single-layer code (>=4 chars,
    # e.g. "A1A1"); a single-layer code for shape_repetition/horizontal is "A1".
    assert len(code_part) >= 4, f"expected a two-layer code, got {code_part!r}"


# ---------------------------------------------------------------------------
# Coverage gap: packaged-wheel branch of _oracle_csv_path (True branch)
# ---------------------------------------------------------------------------


def test_oracle_csv_path_packaged_branch(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """``_oracle_csv_path`` returns the packaged copy when ``is_file()`` is True.

    In an editable checkout ``src/raven_matrix/data/`` does not exist, so only
    the fallback (source-tree) branch is exercised by the suite.  This test
    drives the True branch by patching ``importlib.resources.files`` -- as
    referenced inside ``cli.py`` -- to return a real ``tmp_path`` directory that
    contains a real ``data/ravens_oracle.csv`` stub.

    Because ``pathlib.Path`` implements the ``Traversable`` protocol
    (``__truediv__``, ``is_file()``, ``open()`` …), ``tmp_path`` can stand in
    directly for the Traversable returned by ``files()``.
    """
    import raven_matrix.cli as cli_module

    # Arrange: create the fake packaged data file.
    packaged_data_dir = tmp_path / "data"
    packaged_data_dir.mkdir()
    packaged_csv = packaged_data_dir / "ravens_oracle.csv"

    # Copy three header rows from the real oracle so the stub is a valid CSV.
    real_csv = Path(__file__).resolve().parents[1] / "data" / "ravens_oracle.csv"
    with real_csv.open(encoding="utf-8", newline="") as fh:
        header = fh.readline()
        first_row = fh.readline()
    packaged_csv.write_text(header + first_row, encoding="utf-8")

    # Act: patch files() so files("raven_matrix") returns tmp_path (a Traversable).
    monkeypatch.setattr(cli_module.importlib.resources, "files", lambda _pkg: tmp_path)

    from raven_matrix.cli import _oracle_csv_path

    result = _oracle_csv_path()

    # Assert: the True branch was taken -- result must point at the tmp packaged
    # copy, not the source-tree fallback.
    assert result == packaged_csv, (
        f"expected packaged path {packaged_csv}, got {result}; "
        "the True branch was not taken"
    )
    # And it must be distinct from the source-tree fallback path.
    source_tree_fallback = (
        Path(cli_module.__file__).resolve().parents[2] / "data" / "ravens_oracle.csv"
    )
    assert result != source_tree_fallback, (
        "resolver returned the source-tree fallback rather than the packaged copy"
    )
