# Kaizo AI Move-Choice Probability Engine

Given a Pokémon Platinum Kaizo battle state, computes the *exact* probability
distribution over which move the trainer AI will select — and against which
target, in doubles.

See [`spec.md`](spec.md) for the full design writeup, section by section.

## Status

Early scaffold. Nothing is implemented yet — see `spec.md` for the build order.

## Setup

Requires Python 3.13+.

```bash
python -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate
pip install pytest
```

## Running tests

```bash
pytest test.py -v
```

## Layout

```
aicalc/
  dist.py        # exact probability distributions over score deltas
  state.py       # battle state: Pokemon, Side, Field, Battle, Action
  predicates.py  # the yes/no/numeric facts scripts query
  script.py      # the small DSL scripts are written in, + evaluator
  scoring.py     # combines all active flags into one distribution per move
  select.py      # picks the winning move, handling ties
  sim.py         # Monte Carlo cross-check, used only in tests
  calc/          # ported damage calculator (KO / damage predicates)
  flags/         # one file per AI flag (Basic, Evaluate Attacks, Expert, ...)
cases/           # JSON battle scenarios + expected probability tables
test.py          # test suite, built up section by section
```

## Sources

- Move-by-move AI scoring procedures:
  https://bparkpk.github.io/PKMoveScoring/
- Flag-by-flag AI behavior reference:
  https://gist.github.com/lhearachel/ff61af1f58c84c96592b0b8184dba096
- Damage calculator reference:
  https://hzla.github.io/Dynamic-Calc-Decomps/
