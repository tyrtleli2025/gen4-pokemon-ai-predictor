"""Run saved battle scenarios: python3 -m aicalc.run cases [--check]

Each argument is a case .json file, or a directory whose *.json files are all
run in sorted order. --check compares the computed pick probabilities against
each file's "expected" section and fails loudly on any mismatch.
"""
from __future__ import annotations

import argparse
import sys
from fractions import Fraction
from pathlib import Path

from .calc import NeedsManualFact
from .case_loader import Case, CaseError, load_case
from .predicates import Context
from .scoring import action_score_distributions, active_flags, flag_distribution
from .select import action_probabilities
from .state import legal_actions


def report(case: Case) -> str:
    lines = [f"=== {case.name}"]
    if case.source:
        lines.append(f"    source: {case.source}")
    lines.append(f"    active flags: {active_flags(case.battle)}")
    lines.append("")

    for action in legal_actions(case.battle):
        ctx = Context(battle=case.battle, action=action, damage=case.damage)
        parts = {flag: flag_distribution(flag, ctx)
                 for flag in active_flags(case.battle)}
        lines.append(f"{action.move}:")
        for flag, dist in parts.items():
            if dist.table != {0: Fraction(1)}:
                lines.append(f"    {flag:18} {dist}")
        lines.append("")

    dists = action_score_distributions(case.battle, case.damage)
    lines.append("final score distributions (base 100):")
    for action, dist in dists.items():
        lines.append(f"    {action.move:14} {dist}")

    lines.append("")
    lines.append("pick probabilities:")
    for action, p in sorted(action_probabilities(dists).items(),
                            key=lambda kv: -kv[1]):
        lines.append(f"    {action.move:14} {float(p) * 100:7.3f}%   ({p})")
    return "\n".join(lines)


def check(case: Case) -> list[str]:
    """Mismatches between computed picks and the file's expected block."""
    if case.expected is None:
        return ["no 'expected' section to check against"]
    dists = action_score_distributions(case.battle, case.damage)
    picks = {a.move: p for a, p in action_probabilities(dists).items()}
    return [
        f"{move}: got {picks[move]}, expected {expected}"
        for move, expected in sorted(case.expected.items())
        if picks[move] != expected
    ]


def _expand(paths: list[str]) -> list[Path]:
    out: list[Path] = []
    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            found = sorted(path.glob("*.json"))
            if not found:
                raise CaseError(f"{path}: directory contains no .json cases")
            out.extend(found)
        else:
            out.append(path)
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 -m aicalc.run",
        description="Run saved battle scenarios (cases/*.json).")
    parser.add_argument("paths", nargs="+",
                        help="case .json files and/or directories of them")
    parser.add_argument("--check", action="store_true",
                        help="verify computed picks against 'expected' sections")
    args = parser.parse_args(argv)

    status = 0
    try:
        paths = _expand(args.paths)
    except CaseError as exc:
        print(exc, file=sys.stderr)
        return 2

    for i, path in enumerate(paths):
        if i:
            print()
        try:
            case = load_case(path)
        except CaseError as exc:
            print(f"{exc}", file=sys.stderr)
            status = 2
            continue
        try:
            print(report(case))
        except NeedsManualFact as exc:
            print(f"{path}: {exc}", file=sys.stderr)
            status = 2
            continue
        if args.check:
            problems = check(case)
            if problems:
                status = max(status, 1)
                for problem in problems:
                    print(f"    CHECK MISMATCH  {problem}")
            else:
                print("    CHECK OK")
    return status


if __name__ == "__main__":
    raise SystemExit(main())
