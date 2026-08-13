# Platinum Kaizo game data

Exported from the community Platinum Kaizo spreadsheet:
https://docs.google.com/spreadsheets/d/1y95UYKY9HNgZjUlbeZbQ3BWf5IqcFqAkmstC-OSa6vc/

| File | Source tab | Contents |
|---|---|---|
| `moves.csv` | Moves | Full Kaizo move table: effect, category, power, type, accuracy, PP, target, priority, contact/Protect/Magic Coat flags |
| `move_changes.csv` | Move Changes | Human-readable diff vs. vanilla Platinum |
| `ai_changes.csv` | AI Changes | Kaizo-specific deviations from vanilla Gen 4 trainer AI |
| `ability_changes.csv` | Ability Changes | Ability diffs vs. vanilla |
| `move_aliases.json` | — | Name mismatches between the scoring site and this sheet |

## Reconciling the two sources by move name

The scoring site and this spreadsheet do not always agree on a move's *name*, so
join them through `move_aliases.json` rather than by string equality.

- **Accelerock (site) = Rollout (sheet)** — the same move. Kaizo repurposed the
  Rollout slot into Accelerock; the sheet kept the vanilla slot name while the
  scoring site uses the new one. The sheet's row (Physical, 40 bp, Rock, 100 acc,
  5 PP, priority +1, no added effect) matches Accelerock exactly. Scoring text for
  this move therefore lives under `Accelerock` in `per_move.json`.

Everything else reconciles. The only remaining names in the sheet with no scoring
page are `Struggle` (never scored as a normal AI option, and PP is out of scope)
and rows 468–470, which are unnamed placeholders whose "name" is just their ID.

Note `SolarBeam` and `Solar-Beam` are two **distinct** moves in Kaizo — the vanilla
charging SolarBeam, plus a 120 bp Grass special with no charge turn occupying the
old Skull Bash slot. Both exist in both sources; do not normalise them together.

## Why this matters for the AI engine

The AI scores moves by **effect index**, not by move name. Kaizo rewrites many move
effects, so vanilla Gen 4 AI references cannot be applied move-by-move.

**Source precedence:** the scraped move-scoring site
(https://bparkpk.github.io/PKMoveScoring/) is Kaizo-specific and authoritative.
The lhearachel gist (`gen4_trainer_ai.md`) documents *vanilla* Gen 4 and is a
cross-check for flag structure only — its per-move rules are wrong wherever Kaizo
changed an effect.

Independent confirmation the scrape is Kaizo-aware: the scraped Basic-flag text
checks `Water Absorb or Dry Skin`, whereas vanilla omits Dry Skin due to a bug —
and `ai_changes.csv` states the Dry Skin bug is fixed in Kaizo.

### 25 vanilla moves no longer exist

Taunt, Trick, Switcheroo, Snatch, Nightmare, Defense Curl, Conversion, Healing Wish,
Heal Block, Covet, Rapid Spin, Spit Up, Mud Sport, Water Sport, Skull Bash, Magnitude,
Psywave, Splash, Barrage, Spike Cannon, Horn Attack, Comet Punch, Bind, Arm Thrust, Spark.

Vanilla AI rules keyed to these are dead code in Kaizo — e.g. "opponent is Taunted"
(Counter/Metal Burst), "opponent knows Snatch" (Recovery/Rest), "opponent knows
Defense Curl" (Protect), the Nightmare and Conversion routines, and Conversion's
entry in the Setup First Turn effect list.

### Effects repurposed (vanilla name, Kaizo behaviour)

- **Heart Swap** — stat swap → Water special 95 bp, drains 50% of damage
- **Memento** — stat-drop sacrifice → Selfdestruct/Explosion effect, 255 bp Dark
- **Sheer Cold** — OHKO → ordinary 70 bp Ice, always hits in Hail (Guillotine / Horn Drill / Fissure remain OHKO)
- **Thief** — item steal → Splash effect (does nothing)
- **Shadow Claw** — single hit → 2-5 hit, 25 bp
- **Stockpile** — stockpile counter → raises Def and SpDef
- **Yawn** — delayed sleep → causes Sleep, 70 acc

### AI behaviour changes (from `ai_changes.csv`)

- Dry Skin AI bug **fixed**.
- `1/2 recoil` moves (Draco Meteor, Hyper Beam, Giga Impact, …) follow the intended
  recoil routine instead of vanilla's bugged targeting — **except Head Smash**, which
  keeps vanilla AI for now (the sheet notes this reverts next patch).
- `1/4 recoil` moves (Brave Bird, Close Combat, Take Down) use a new routine:
  −1 if the target resists/is immune; −1 if slower and user HP > 59%; −1 if faster and user HP > 40%.
- Triple Axel and Fury Cutter use the vanilla Triple Kick effect and are treated as
  **Risky** moves (Triple Kick and Rock Wrecker are not).
- Hurricane does **not** use the Thunder routine despite a similar accuracy check.

Priority values changed extensively (Tailwind +5, Trick Room +7, Block +7, Fake Out +3,
ExtremeSpeed/Sucker Punch/Tail Glow +2, many +1). This feeds both speed-order predicates
and Evaluate Attacks' "+1 priority effect" branch — read priority from `moves.csv`,
never from vanilla knowledge.
