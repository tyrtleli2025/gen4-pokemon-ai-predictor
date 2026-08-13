"""ScoreDist: an exact probability distribution over score deltas.

Every AI probability is a fraction with a power-of-two denominator (n/256 and
compounds of it), so the whole engine uses Fraction and never floats. A
ScoreDist is a {delta: probability} table whose weights sum to exactly 1.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Iterable


class ScoreDist:
    __slots__ = ("table",)

    def __init__(self, table: dict[int, Fraction]):
        clean = {d: Fraction(p) for d, p in table.items() if p != 0}
        total = sum(clean.values(), Fraction(0))
        if total != 1:
            raise ValueError(f"probabilities must sum to 1, got {total}")
        self.table = dict(sorted(clean.items()))

    @classmethod
    def certain(cls, delta: int = 0) -> ScoreDist:
        """The delta happens with probability 1."""
        return cls({delta: Fraction(1)})

    @classmethod
    def mix(cls, branches: Iterable[tuple[Fraction, ScoreDist]]) -> ScoreDist:
        """Weighted mixture: with probability p, behave like dist p."""
        out: dict[int, Fraction] = {}
        for weight, dist in branches:
            weight = Fraction(weight)
            if weight == 0:
                continue
            for delta, p in dist.table.items():
                out[delta] = out.get(delta, Fraction(0)) + weight * p
        return cls(out)

    def convolve(self, other: ScoreDist) -> ScoreDist:
        """Distribution of the sum of two independent deltas."""
        out: dict[int, Fraction] = {}
        for d1, p1 in self.table.items():
            for d2, p2 in other.table.items():
                out[d1 + d2] = out.get(d1 + d2, Fraction(0)) + p1 * p2
        return ScoreDist(out)

    def shift(self, n: int) -> ScoreDist:
        """Add a constant to every outcome."""
        return ScoreDist({d + n: p for d, p in self.table.items()})

    def probability_of(self, delta: int) -> Fraction:
        return self.table.get(delta, Fraction(0))

    @property
    def support(self) -> list[int]:
        return list(self.table)

    def __eq__(self, other) -> bool:
        return isinstance(other, ScoreDist) and self.table == other.table

    def __repr__(self) -> str:
        inner = ", ".join(f"{d}: {p}" for d, p in self.table.items())
        return f"ScoreDist({{{inner}}})"
