"""Script DSL -- Chance, If, Add, Stop, Seq, and the evaluator.

One flag's scoring procedure for one move effect is a tree of these nodes.
Evaluating it against a Context yields an exact ScoreDist.

Semantics, matching the decomp (see aicalc/flags/_scraped/DECOMP_NOTES.md):

* `Stop` is the scripts' `PopOrEnd`: it ends *this flag's* script only. Once a
  path has stopped, later statements leave it untouched.
* `If` conditions are deterministic given the Context, so they never branch the
  distribution -- only `Chance` introduces randomness. That keeps the state
  space tiny and the result exact.
* `Chance(n, d, body)` runs `body` with probability n/d. Note the decomp writes
  the *inverse*: `IfRandomLessThan val, <terminate>` jumps away with probability
  val/256, so the body it guards has probability (256 - val)/256.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Callable

from .dist import ScoreDist

# A path's state while the script runs: how much score it has accrued, and
# whether it has terminated.
State = tuple[int, bool]
StateDist = dict[State, Fraction]


class Node:
    """Base class for DSL nodes."""

    def run(self, states: StateDist, ctx) -> StateDist:
        raise NotImplementedError


def _live(states: StateDist) -> tuple[StateDist, StateDist]:
    """Split into (still running, already stopped)."""
    running = {s: p for s, p in states.items() if not s[1]}
    stopped = {s: p for s, p in states.items() if s[1]}
    return running, stopped


def _merge(*parts: StateDist) -> StateDist:
    out: StateDist = {}
    for part in parts:
        for state, p in part.items():
            if p:
                out[state] = out.get(state, Fraction(0)) + p
    return out


@dataclass(frozen=True)
class Add(Node):
    """Add a fixed amount to the running score."""

    delta: int

    def run(self, states: StateDist, ctx) -> StateDist:
        running, stopped = _live(states)
        moved = {(d + self.delta, False): p for (d, _), p in running.items()}
        return _merge(moved, stopped)


@dataclass(frozen=True)
class Stop(Node):
    """Terminate this flag's script for the current path."""

    def run(self, states: StateDist, ctx) -> StateDist:
        running, stopped = _live(states)
        halted = {(d, True): p for (d, _), p in running.items()}
        return _merge(halted, stopped)


@dataclass(frozen=True)
class Seq(Node):
    """Run nodes in order."""

    nodes: tuple[Node, ...]

    def __init__(self, *nodes: Node):
        object.__setattr__(self, "nodes", tuple(nodes))

    def run(self, states: StateDist, ctx) -> StateDist:
        for node in self.nodes:
            states = node.run(states, ctx)
        return states


@dataclass(frozen=True)
class If(Node):
    """Deterministic branch on a predicate of the Context."""

    predicate: Callable[[object], bool]
    then: Node
    otherwise: Node | None = None

    def run(self, states: StateDist, ctx) -> StateDist:
        running, stopped = _live(states)
        if not running:
            return states
        branch = self.then if self.predicate(ctx) else self.otherwise
        if branch is None:
            return states
        return _merge(branch.run(running, ctx), stopped)


@dataclass(frozen=True)
class Chance(Node):
    """Run `body` with probability numerator/denominator."""

    numerator: int
    denominator: int
    body: Node

    def __post_init__(self):
        if not 0 <= self.numerator <= self.denominator:
            raise ValueError(f"bad odds {self.numerator}/{self.denominator}")

    def run(self, states: StateDist, ctx) -> StateDist:
        running, stopped = _live(states)
        if not running:
            return states
        p = Fraction(self.numerator, self.denominator)
        taken = {s: w * p for s, w in running.items()}
        skipped = {s: w * (1 - p) for s, w in running.items()}
        return _merge(self.body.run(taken, ctx), skipped, stopped)


def evaluate(node: Node, ctx) -> ScoreDist:
    """Run a script against a Context and marginalise out the stopped flag."""
    states: StateDist = {(0, False): Fraction(1)}
    states = node.run(states, ctx)
    out: dict[int, Fraction] = {}
    for (delta, _), p in states.items():
        out[delta] = out.get(delta, Fraction(0)) + p
    return ScoreDist(out)
