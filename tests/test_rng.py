"""Tests for JavaRandom: faithful port of java.util.Random.

Loads the committed golden fixture (tests/golden/javarandom_vectors.json) and
verifies each block against a fresh JavaRandom instance. Every block is a
separate parametrized case so failures name the offending seed/method/bound
directly.

AC4.2 edges named explicitly:
- bound == 2: power-of-two fast path.
- bound in {3, 5, 6}: rejection-loop path.
"""
from __future__ import annotations

import json
import pathlib

import pytest

from raven_matrix.rng import JavaRandom

_FIXTURE_PATH = pathlib.Path(__file__).parent / "golden" / "javarandom_vectors.json"
_FIXTURE = json.loads(_FIXTURE_PATH.read_text())


def _block_id(block: dict) -> str:
    method = block["method"]
    seed = block["seed"]
    bound = block.get("bound")
    if bound is not None:
        return f"{method}_seed{seed}_bound{bound}"
    return f"{method}_seed{seed}"


@pytest.mark.parametrize(
    "block",
    _FIXTURE["vectors"],
    ids=[_block_id(b) for b in _FIXTURE["vectors"]],
)
def test_block_matches_golden(block: dict) -> None:
    """Each fixture block must reproduce exactly against JavaRandom."""
    seed: int = block["seed"]
    method: str = block["method"]
    count: int = block["count"]
    expected: list = block["values"]

    rng = JavaRandom(seed)

    if method == "nextInt":
        bound: int = block["bound"]
        actual = [rng.next_int(bound) for _ in range(count)]
    elif method == "nextBoolean":
        actual = [rng.next_boolean() for _ in range(count)]
    else:
        pytest.fail(f"Unknown method in fixture: {method!r}")

    if actual != expected:
        first_diff = next(
            i
            for i, (a, e) in enumerate(zip(actual, expected, strict=True))
            if a != e
        )
        pytest.fail(
            f"Mismatch for seed={seed} method={method} "
            f"bound={block.get('bound')}: first diff at index {first_diff}"
        )


# --- Explicit AC4.2 edge assertions ---

def _get_blocks(method: str, **filters) -> list[dict]:
    return [
        b for b in _FIXTURE["vectors"]
        if b["method"] == method and all(b.get(k) == v for k, v in filters.items())
    ]


def test_ac4_2_power_of_two_bound_present() -> None:
    """At least one nextInt block with bound==2 (power-of-two fast path) exists."""
    blocks = _get_blocks("nextInt", bound=2)
    assert blocks, "No fixture block with bound==2 (power-of-two fast path)"


def test_ac4_2_non_power_of_two_bound_present() -> None:
    """At least one nextInt block with a non-power-of-two bound (3, 5, or 6) exists."""
    blocks = [
        b for b in _FIXTURE["vectors"]
        if b["method"] == "nextInt" and b.get("bound") in {3, 5, 6}
    ]
    assert blocks, "No fixture block with bound in {3,5,6} (rejection-loop path)"


def test_ac4_2_power_of_two_sequence_correct() -> None:
    """Spot-check: bound==2 sequence for seed==0 matches the fixture value."""
    blocks = _get_blocks("nextInt", bound=2)
    # Pick seed==0 for a deterministic spot-check.
    block = next((b for b in blocks if b["seed"] == 0), blocks[0])
    rng = JavaRandom(block["seed"])
    actual = [rng.next_int(2) for _ in range(block["count"])]
    assert actual == block["values"]


def test_ac4_2_rejection_loop_sequence_correct() -> None:
    """Spot-check: non-power-of-two bound (3) sequence for seed==0 matches fixture."""
    blocks = _get_blocks("nextInt", bound=3)
    block = next((b for b in blocks if b["seed"] == 0), blocks[0])
    rng = JavaRandom(block["seed"])
    actual = [rng.next_int(3) for _ in range(block["count"])]
    assert actual == block["values"]
