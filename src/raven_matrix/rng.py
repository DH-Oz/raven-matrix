"""A faithful port of java.util.Random — only the methods SGMT uses.

The algorithm is mandated by the Java SE specification (unchanged since Java 1.0):
a 48-bit linear congruential generator. Upstream uses only nextInt(bound) and
nextBoolean (source-verified), so that is all we expose, plus the protected next()
they are built on.
"""

from __future__ import annotations

_MULTIPLIER = 0x5DEECE66D
_ADDEND = 0xB
_MASK = (1 << 48) - 1


def _to_int32(value: int) -> int:
    """Interpret the low 32 bits as a signed Java int."""
    value &= 0xFFFFFFFF
    return value - (1 << 32) if value & 0x80000000 else value


class JavaRandom:
    """java.util.Random with the SGMT-reachable surface."""

    __slots__ = ("_seed",)

    def __init__(self, seed: int) -> None:
        self.set_seed(seed)

    def set_seed(self, seed: int) -> None:
        self._seed = (seed ^ _MULTIPLIER) & _MASK

    def next(self, bits: int) -> int:
        """Advance state; return the top `bits` as a signed int32."""
        self._seed = (self._seed * _MULTIPLIER + _ADDEND) & _MASK
        return _to_int32(self._seed >> (48 - bits))

    def next_int(self, bound: int) -> int:
        if bound <= 0:
            raise ValueError("bound must be positive")
        # Power-of-two fast path.
        if (bound & -bound) == bound:
            return (bound * self.next(31)) >> 31
        # Rejection loop for uniformity.
        while True:
            bits = self.next(31)
            val = bits % bound
            if bits - val + (bound - 1) >= 0:
                return val

    def next_boolean(self) -> bool:
        return self.next(1) != 0
