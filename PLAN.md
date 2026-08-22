# Kaizo AI Move-Choice Probability Engine — Project Plan

## Goal

Given a description of a Pokémon Platinum Kaizo battle at a single moment, compute
the *exact* probability distribution over which move the trainer AI will choose —
and, in doubles, which target it aims at.

Not an estimate. Every AI decision is built from fixed, known probabilities
(things like "68.8% chance of +2"), so the answer can be computed exactly with
probability math, the same way you'd compute exact odds for a sequence of coin
flips rather than simulating them.

## The pipeline

The program is one chain of stages. Each stage takes a plain Python object and
produces a new one — no files, no user input, nothing printed until the very end.
This is what makes every stage independently testable.

```
Battle  →  legal_actions  →  Context (per action)  →  ScoreDist (per action)
                                                              ↓
                                        combine flags  →  ScoreDist (per action, combined)
                                                              ↓
                                              select   →  probabilities (one dict)
```

| Stage | Input | Output | Lives in |
|---|---|---|---|
| 1. Describe the situation | — (built by hand, later from JSON/UI) | `Battle` object | `state.py` |
| 2. Enumerate the choices | `Battle` | `list[Action]` | `state.py` |
| 3. Answer the AI's questions | `Battle`, `Action` | `Context` | `predicates.py` |
| 4. Score one flag, one move | `Context` | `ScoreDist` | `script.py` + `flags/` |
| 5. Combine all active flags | several `ScoreDist` | one `ScoreDist` per action | `scoring.py` |
| 6. Decide the winner | `dict[Action, ScoreDist]` | `dict[Action, float]` | `select.py` |

The single function tying it together:

```python
def move_probabilities(battle: Battle) -> dict[Action, float]:
    actions = legal_actions(battle)
    dists = {a: score_distribution(battle, a, Context(battle, a)) for a in actions}
    return action_probabilities(dists)
```

## Data sources

Four external references anchor the whole project — nothing here is guessed:

1. **Move-by-move AI scoring** — https://bparkpk.github.io/PKMoveScoring/
   One page per move, listing every flag's scoring procedure for that move,
   in near-machine-readable form. Kaizo-specific, and therefore the
   authoritative source. Scraped and deduplicated — see
   `aicalc/flags/_scraped/dedup.md`.
2. **Kaizo game data** — the community Platinum Kaizo spreadsheet, exported to
   `data/` (move table, move/ability diffs, AI changes). See `data/README.md`.
   Kaizo rewrites many move *effects*, and the AI scores by effect, so vanilla
   move knowledge cannot be used anywhere.
3. **Flag-by-flag AI reference** — the lhearachel gist
   (`gen4_trainer_ai.md`). Documents *vanilla* Gen 4. Useful for flag
   structure and for ambiguities (base score is 100, ties break uniformly at
   random, "terminate" ends only the current flag's script), but its per-move
   rules are wrong wherever Kaizo changed an effect — 25 vanilla moves don't
   even exist in Kaizo.
4. **Damage calculator** — https://hzla.github.io/Dynamic-Calc-Decomps/
   Source for the damage/KO logic. To be ported to Python, in an "AI mode"
   that uses the AI's actual max-roll KO check rather than the player-facing
   damage spread.

~~One known discrepancy to resolve empirically: the two AI sources disagree on
which side of a coin flip triggers the 4×-effectiveness bonus in Evaluate
Attacks (176/256 vs 80/256).~~ **Resolved — bparkpk's 176/256 is correct.**
The pokeplatinum decomp's `IfRandomLessThan <val>, <label>` jumps when
`rand % 256 < val`, so the score on the fall-through path has probability
`(256 − val)/256`; the gist read the jump threshold as the success probability
and inverted it. See `aicalc/flags/_scraped/DECOMP_NOTES.md`.

A fifth reference, used **only** to disambiguate nesting in bparkpk's flat prose:
the **pret/pokeplatinum decomp** (clone as a sibling of this repo). It is vanilla
Platinum, so it never overrides bparkpk on values or conditions — disagreements
are recorded in `DECOMP_NOTES.md` instead.

## Build order

Each stage is only started once the stage before it is tested and stable.

- [x] **Stage 1 — `state.py`**: `Pokemon`, `Side`, `Field`, `Battle`, `Action`
      dataclasses. Pure data, no logic beyond `hp_percent()`.
- [x] **Stage 2 — `legal_actions`**: given a `Battle`, list the candidate
      `Action`s. Trivial in singles (one per known move); the interface is
      written now so doubles later doesn't require a rewrite.
- [x] **Scrape + dedupe the move-scoring site**: all 466 move pages scraped
      (raw HTML in `scrape_raw/`, deduplicated text in
      `aicalc/flags/_scraped/dedup.md`, machine-readable in `per_move.json`).
      **236 distinct scoring blocks** to encode: basic 105, expert 114,
      evaluate_attacks 9, baton_pass 6, prio_damage 1, setup_first_turn 1.
      Coverage verified complete against `data/moves.csv` (every Kaizo move has
      a scoring page except `Struggle`, which the AI never scores) — join the
      two sources via `data/move_aliases.json`.
      `Risky` has since been extracted the same way (from cache, no
      re-fetching): a single block — 50% (128/256) chance of +2 — across 61
      effect-gated moves. The cached raw HTML still holds `Doubles vs
      Opponent`, `Doubles vs Ally`, `Check HP`, `Weather` and `Harassment`
      unextracted; extend the `FLAGS` map in `tools/scrape.py` and re-run the
      dedup when needed.
- [x] **Stage 3 — `predicates.py`**: `Context` class answering each derived
      question. Non-damage questions first (first turn, hazards active,
      knows-move, etc.); damage-dependent questions (`can_ko`,
      `is_best_damaging_move`, `effectiveness`) stubbed via a hand-supplied
      `DamageBackend` until the damage calculator exists.
- [x] **Stage 4 — `script.py` + `dist.py`**: the small DSL (`Chance`, `If`,
      `Add`, `Stop`) and its evaluator; `ScoreDist` as an exact
      `{delta: Fraction}` table supporting `mix` and `convolve`.
- [x] **Encode flag scripts** (`flags/basic.py`, `evaluate_attacks.py`,
      `expert.py`, `setup_first_turn.py`, `prio_damage.py`, `baton_pass.py`):
      **all 237/237 blocks encoded** — setup_first_turn 1, prio_damage 1,
      evaluate_attacks 9, baton_pass 6, basic 105, expert 114, risky 1
      (added for the Roark/Bonsly case; `flags/risky.py`). A test asserts
      every scraped block id has an encoding, so gaps fail loudly.
      Damage-dependent questions still route through `DamageBackend`, so a
      real end-to-end run needs the damage calculator (or a hand-supplied
      backend).
      `state.py` gained `Pokemon.last_move` and `Pokemon.protect_streak`, and
      `predicates.py` gained `last_move`, `used_protect_last`,
      `protect_streak`, and `user_is_faster` (exact, via `Fraction` — boosts,
      paralysis, Tailwind, Trick Room) to support `baton_pass`'s
      Detect/Protect block and future `expert`/`basic` needs.
- [x] **Stage 5 — `scoring.py`**: convolve all active flags into one
      `ScoreDist` per action, on top of a base score of 100. Flags are
      independent (no encoded block reads another flag's score), so the
      combined distribution is their convolution. A battle carrying a flag we
      have not encoded (`risky`, `check_hp`, …) raises `UnsupportedFlags`
      rather than silently under-counting.
      **Not yet validated against the Teddiursa scenario** — `cases/` is empty,
      so the named scenario has no data to run against. Currently covered by
      synthetic tests instead: base score, per-flag convolution, turn
      sensitivity, no-procedure moves contributing exactly 0, and a
      deterministic immunity case.
- [x] **Stage 6 — `select.py`**: argmax with uniform tie-breaking among equal
      scores, via exact naive enumeration over the product of the actions'
      supports (tie-count DP deferred until it's ever slow).
      `move_probabilities(battle, damage)` is now the single entry point for
      the whole pipeline.
      First real scenario validated end to end with a hand-supplied damage
      backend: `cases/roark_bonsly_vs_machop.json` (screenshot in `cases/`) —
      Stealth Rock 68.72%, Brick Break 21.70%, Selfdestruct 9.59%,
      Accelerock 0%; pinned as a regression test and independently
      hand-computed. (An earlier 89.6/10.4 figure fed the backend a wrong
      damage-comparison fact — the AI zeroes Selfdestruct out of its
      highest-damage comparison; see DECOMP_NOTES.md.) The Mars/Skarmory scenario (Tailwind
      50.20%, Stealth Rock 40.79%, Iron Head 9.01%, Pluck 0%) still needs its
      battle data entered to validate against known-good numbers.
- [x] **Scenario files + runner**: scenarios are now declarative JSON in
      `cases/` (format 1: battle + hand-supplied `damage` facts + optional
      `expected` pick probabilities), loaded by `aicalc/case_loader.py`
      (`load_case` / `load_case_dict`, the latter being the future web-UI
      seam) and run via `python3 -m aicalc.run cases --check`. Move and flag
      names are auto-canonicalised from display spellings ("Thunder Punch" →
      `ThunderPunch`) via `aicalc/names.py`; the one genuine collision
      (Solar-Beam vs SolarBeam, distinct Kaizo moves) errors instead of
      guessing. Unknown keys, moves, flags, abilities (validated against the
      Kaizo per-Pokémon ability table) and off-scale effectiveness all fail
      loudly with JSON-path locations. The `damage` section becomes optional
      once `calc/` lands.
- [ ] **Damage calculator port** (`calc/`): can proceed in parallel with the
      above, gated behind the `Context` interface so nothing downstream needs
      to change when it lands.
- [ ] **Speed + validation**: tie-count DP to replace naive subset
      enumeration; Monte Carlo oracle for cross-checking; in-game
      save-state resampling to validate the transcribed scripts themselves.
- [ ] **Doubles support**: extend `legal_actions`, add the `Doubles` flag
      scripts, extend tie-breaking beyond 4 actions.
- [ ] **UI**: a calculator-style front end (in the spirit of the existing
      HZLA damage calculator) that lets a user set up a battle and see the
      resulting move/target probability tables.

## Explicitly out of scope for now

Switch decisions, trainer item usage, multi-turn lookahead, PP/Disable/Choice
restrictions, ally-targeting moves, and modeling what the AI does or doesn't
know about the player's team.

## Repo

`aicalc/` (package) · `cases/` (saved battle scenarios, JSON) · `test.py`
(test suite, built up section by section) · `README.md` · `spec.md` (detailed
section-by-section design notes).
