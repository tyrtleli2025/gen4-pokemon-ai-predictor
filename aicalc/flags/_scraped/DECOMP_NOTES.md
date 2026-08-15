# Using the pokeplatinum decomp to disambiguate nesting

Clone (sibling of this repo, deliberately outside it):

    ../../../pokeplatinum        # git clone --depth 1 https://github.com/pret/pokeplatinum

Relevant files:

| Path | Contents |
|---|---|
| `src/battle/trainer_ai/script.s` | The AI scripts themselves — commented, labelled, explicit control flow |
| `src/battle/trainer_ai/trainer_ai.c` | The interpreter: what each script command actually does |
| `generated/ai_flags.txt` | Flag list and order |

## Rule of use

**The decomp is vanilla Platinum. bparkpk documents Kaizo.** Use the decomp *only*
to resolve nesting/control-flow ambiguity in bparkpk's flat prose. Where the two
disagree on a number or a condition, **keep bparkpk's value** and record the
disagreement in the "Disagreements" section below.

## Flag mapping (confirmed 1:1)

| Our module | Decomp flag | Script label |
|---|---|---|
| `basic` | `AI_FLAG_BASIC` | `Basic_Main` |
| `evaluate_attacks` | `AI_FLAG_EVAL_ATTACK` | `EvalAttack_Main` |
| `expert` | `AI_FLAG_EXPERT` | `Expert_Main` |
| `setup_first_turn` | `AI_FLAG_SETUP_FIRST_TURN` | `SetupFirstTurn_Main` |
| `prio_damage` | `AI_FLAG_PRIORITIZE_EXTREMES` | `PrioritizeExtremes_Main` |
| `baton_pass` | `AI_FLAG_BATON_PASS` | `BatonPass_Main` |

`Expert_Main` dispatches on `BATTLE_EFFECT_*` via `IfCurrentMoveEffectEqualTo`,
confirming that scoring is keyed by move *effect* rather than move name.

## THE critical semantic: `IfRandomLessThan`

From `trainer_ai.c:528`:

```c
if ((BattleSystem_RandNext(battleSys) % 256) < val) {
    AIScript_Iter(battleCtx, jump);   // take the jump
}
```

So for `IfRandomLessThan <val>, <label>`:

- **P(jump taken) = val / 256**
- **P(fall through) = (256 − val) / 256**

The jump almost always goes to a *terminate* label, meaning the score is applied on
the **fall-through** path. Read every random branch this way — the naive reading
("val/256 chance of the thing that follows") is backwards.

### This resolves the open discrepancy in PLAN.md

The 4×-effectiveness bonus in Evaluate Attacks:

```asm
EvalAttack_TryScorePlus2:
    IfRandomLessThan 80, EvalAttack_Terminate
    AddToMoveScore 2
```

P(+2) = (256 − 80)/256 = **176/256 = 68.75%**, and the decomp's own comment says
"68.75% chance of score +2". **bparkpk (176/256) is correct; the gist's 80/256 was
a misreading of this exact instruction** — it took the jump threshold as the
success probability. Treat 176/256 as settled, and treat the gist's probabilities
generally with suspicion wherever a random branch is involved.

Same pattern verified in three more places, all agreeing with bparkpk:

| Routine | Decomp | Implied P | bparkpk | Agrees |
|---|---|---|---|---|
| Setup First Turn +2 | `IfRandomLessThan 80` | 176/256 = 68.75% | 68.75% (176/256) | yes |
| Prioritize Extremes +2 | `IfRandomLessThan 100` | 156/256 = 60.94% | 61% (156/256) | yes |
| Eval Attack deprioritize −2 | `IfRandomLessThan 51` | 205/256 = 80.08% | ~80% | yes |

## Disagreements (bparkpk wins; recorded for later empirical checks)

Both are in `baton_pass`, both off by exactly one out of 256:

| Branch | Decomp (vanilla) | bparkpk (Kaizo) | Kept |
|---|---|---|---|
| No scoring change when user doesn't know Baton Pass | `IfRandomLessThan 80` → 80/256 = 31.25% | "31.25% **(81/256)**" | bparkpk's 81/256 |
| Score +3 fall-through | `IfRandomLessThan 20` → 236/256 = 92.19% | "92% **(235/256)**" | bparkpk's 235/256 |

Note bparkpk's *percentage* in the first row (31.25%) equals 80/256, not the 81/256
it prints alongside — so bparkpk is internally inconsistent there. The discrepancy is
confined to `baton_pass`; the other flags match exactly, so this is more likely a
transcription slip than a Kaizo change. Worth settling with the save-state
resampling planned in PLAN.md.

## Confirmed-correct oddities (not transcription errors)

Some scraped conditions look wrong at a glance but are verbatim-correct vanilla
AI behavior. Checked here so they aren't "fixed" during encoding by mistake.

### Bide/Metal Burst check "Stall ability or holding a Shiny Stone" — genuine game bug

`dedup.md`'s `basic` block for Bide/Metal Burst reads: "If the target's ability
is Stall, or the target is holding a Shiny Stone: Score -10 ... If the user's
ability is Stall, or the user is holding a Shiny Stone: No scoring change and
terminate." Shiny Stone is an evolution item with no documented battle effect,
which made this look like a scrape/OCR error. It is not — `ABILITY_STALL` and
`ITEM_SHINY_STONE` are both real constants, and `script.s:1160-1176`
(`Basic_CheckMetalBurst`) contains this exact check, with the decomp's own
authors flagging it:

```asm
// If the target's ability is Stall or they are holding a Shiny Stone, score -10.
// BUG: This should use the command LoadHeldItemEffect to check for the Lagging Tail
// effect.
LoadBattlerAbility AI_BATTLER_DEFENDER
IfLoadedEqualTo ABILITY_STALL, ScoreMinus10
IfHeldItemEqualTo AI_BATTLER_DEFENDER, ITEM_SHINY_STONE, ScoreMinus10
```

So this is a genuine vanilla Platinum AI bug, not a bparkpk transcription
error: the intended check was almost certainly the **Lagging Tail** held-item
effect (Lagging Tail makes the holder always move last, same idea as the Stall
ability — the sensible pairing for a "does the target/user effectively move
last" check ahead of Bide/Metal Burst's speed-order logic at line 1179).
Instead the code checks literally for the item Shiny Stone, which does nothing
in battle, so that branch is realistically unreachable in normal play. Encode
it as scraped — do not "correct" it to Lagging Tail, since bparkpk's job is to
describe what the game actually does, bug included. Worth flagging as a
candidate for `data/ai_changes.csv`-style Kaizo fixes; nothing there yet
mentions it, so treat it as present in Kaizo until shown otherwise.

## Structural facts worth reusing

- `IfTargetIsPartner Terminate` opens every flag — irrelevant in singles.
- `PopOrEnd` is the script's "terminate": it ends **the current flag's script only**,
  confirming the semantics we assumed for "and terminate".
- Setup First Turn gates on `LoadTurnCount` / `IfLoadedNotEqualTo 0`, i.e. turn 0 is
  the first turn of the **whole battle**, matching `Field.turn == 1` in `state.py`.
- Setup First Turn's eligible effects live in the `SetupFirstTurn_SetupEffects`
  table — an explicit `BATTLE_EFFECT_*` list, better than prose. It includes
  `BATTLE_EFFECT_CONVERSION`, which is dead in Kaizo (Conversion no longer exists).
- Baton Pass special-cases Swords Dance / Dragon Dance / Calm Mind / Nasty Plot to a
  shared `BatonPass_SetupAtHighHP` routine, and Protect/Detect to `BatonPass_EvalProtect`
  — which is exactly the 3-way split the dedup found (6 blocks: generic, the +2
  boosters, Protect/Detect, Baton Pass itself, and two others).

## Per-block disambiguation log

Record each block resolved this way as encoding proceeds, so provenance is auditable.

| Flag | Block / moves | Ambiguity | Decomp label used | Resolution |
|---|---|---|---|---|
| `setup_first_turn` | `077f03b8` (91 moves) | "first turn of battle" — first turn of the *battle* or of this Pokémon being out? | `SetupFirstTurn_Main` | Whole battle. Gated on `LoadTurnCount` / `IfLoadedNotEqualTo 0`, a global turn counter — so `Field.turn == 1`. |
| `setup_first_turn` | `077f03b8` | Which side of the 176/256 roll carries the +2? | `SetupFirstTurn_Main` | `IfRandomLessThan 80` jumps to terminate, so +2 is the fall-through at 176/256. Matches bparkpk. |
| `prio_damage` | `7a96e66c` (182 moves) | bparkpk says "Unconditionally", but unconditional given *what*? | `PrioritizeExtremes_Main` | Not truly unconditional: the routine is guarded by `FlagMoveDamageScore` / `IfLoadedNotEqualTo AI_NO_COMPARISON_MADE`, applying only to effects the AI cannot damage-compare. That guard is what selects these 182 moves, so it lives in the move→block mapping, not the script. |
| `prio_damage` | `7a96e66c` | Direction of the 156/256 roll. | `PrioritizeExtremes_Main` | `IfRandomLessThan 100` jumps to terminate → +2 at (256−100)/256 = 156/256. Matches bparkpk. |
| `evaluate_attacks` | `60e2d800` (256) vs `469e0e0f` (7) | Why do 7 moves get +6 on KO instead of +4? | `EvalAttack_ApplyKillBonuses` | `IfCurrentMoveEffectEqualTo BATTLE_EFFECT_PRIORITY_1, EvalAttack_ScorePlus2` falls through (no jump) into the next label's `AddToMoveScore 4` — a deliberate fall-through, not a bug — so the +1-priority-effect moves get +2 then +4 = +6. Confirms bparkpk's two KO-bonus values exactly and confirms priority moves are selected by *effect*, not the numeric priority in `moves.csv` (per decomp's own comment). |
| `evaluate_attacks` | `06dd7390` (Explosion/Focus Punch/Memento/Selfdestruct) | Why no KO branch and no "-1 if outdamaged" branch for these 4, unlike every other move? | `EvalAttack_ApplyKillBonuses`, `EvalAttack_Main` | Partially resolved: the kill branch explicitly special-cases `BATTLE_EFFECT_HALVE_DEFENSE` (Explosion/Selfdestruct, and Memento since Kaizo reassigned it to this effect) straight to `Terminate` with **no** bonus, which fully explains the missing KO branch for those three. Decomp's own comment notes Focus Punch structurally can never reach the kill-check at all, which is consistent with it lacking a KO branch too, but doesn't explain the missing "-1 if outdamaged" branch for any of the four. Encoded exactly as scraped (no KO branch, no -1 branch) since bparkpk describes observed behavior and decomp doesn't contradict it, even where it can't fully explain it. |
| `baton_pass` | `28caf3f3` (159, generic) | Confirm "92% chance +3" is the whole story with no first-turn twist. | `BatonPass_EvalMove` generic tail | Confirmed: `IfRandomLessThan 20, Risky_Terminate; AddToMoveScore 3` with no `LoadTurnCount` check anywhere in this path. |
| `baton_pass` | `5d652fe9` (6 moves) | Where does "(if first turn: +8 instead of +3)" attach — same roll with a different prize, or a separate gate? | *(none — no vanilla equivalent)* | **Not decomp-resolved.** The generic path this block otherwise matches (`28caf3f3`) has no turn-1 logic at all in vanilla, so this parenthetical is Kaizo-specific with nothing to check it against. Encoded as a same-odds substitution (235/256 either way, amount depends on turn) — the most direct reading of "X instead of Y," but a genuine judgment call, not a confirmed fact. |
| `baton_pass` | `054f1363` (6 moves incl. Aqua Ring, Tail Glow) | Confirm the 3-line cascade (+5 / -10 / +1) is linear, not nested. | `BatonPass_SetupAtHighHP` | Confirmed linear: `LoadTurnCount==0 → +5`, else `HP<60% → -10`, else `+1`. Also note: decomp's explicit dispatch list for this routine is only Swords Dance/Dragon Dance/Calm Mind/Nasty Plot — it does not include Aqua Ring or Tail Glow. Kaizo evidently routes those two here as well; decomp can't confirm why, only that the resulting script shape (once reached) matches bparkpk exactly. |
| `baton_pass` | `95347291` (Assist, Toxic) | Whole-block structure: does the ~8% miss on the turn-1 branch fall through to the HP tail, or terminate blank? | *(none — no vanilla equivalent)* | **Not decomp-resolved.** No `MOVE_ASSIST`/`MOVE_TOXIC` special-casing exists in `BatonPass_Main` at all — this is new Kaizo logic. Encoded so the turn-1 miss falls through to the same HP tail as `054f1363`, for consistency with the explicit "continue" wording bparkpk uses on the non-first-turn branch. A judgment call under real uncertainty, not a confirmed fact — worth save-state resampling if this move pair matters to a real calculation. |
| `baton_pass` | `47e2ff4e` (Baton Pass itself) | Are the attack/special-attack boost checks a priority cascade (first match wins) or independent additive checks? | `BatonPass_EvalBatonPass` | Cascade, first match wins. Every `IfStatStageGreaterThan ..., ScorePlusN` jumps to a **shared, globally-reused** `ScorePlusN` label that adds the score and immediately `PopOrEnd`s — so any matching check ends the whole script on the spot. Confirms the natural top-to-bottom reading and rules out the plausible-but-wrong alternative (summing both an attack-boost bonus and a special-attack-boost bonus). |
| `baton_pass` | `3e751284` (Detect, Protect) | None — included for completeness. | `BatonPass_EvalProtect` | Exact match: `LoadBattlerPreviousMove` / `IfLoadedInTable {Protect, Detect}` → −2, else +2. The one block in this flag that genuinely needs last-move-used state. |

| `basic` | all immunity blocks (~330 moves) | Are the ability checks independent, or one dispatch? Does Mold Breaker apply per-clause? | `Basic_CheckForImmunity` | One **dispatch on the defender's single ability** (`IfLoadedEqualTo X, <label>`, first match jumps away), preceded by a *single* Mold Breaker bypass for the whole group. Equivalent to sequential `If`s since a Pokémon has one ability, so encoded that way. Each absorption branch also re-checks the move's type — already implied by which moves share a block, so not repeated. |
| `basic` | `3f5b66c9`, `723d42fb`, sound moves | Soundproof scores −10 while other absorbers score −12 — typo? | `Basic_CheckSoundproof` | Correct as scraped. Soundproof is checked in a *separate* routine after the type-immunity dispatch, and scores −10. Not part of the −12 absorber group. |
| `basic` | `796943c0` (Fling) | Deeply nested; the reading "+3 when the target **can't** be statused" looks backwards. | `Basic_FlingPoison` / `Basic_FlingPoison_AttackerChecks` | **Confirmed exactly as scraped, counterintuitive as it is.** If the target *can* be poisoned → `PopOrEnd`, no score at all. Only if the target *can't* be poisoned does it check the attacker: attacker also unaffected → **+3**, attacker affected → −5. Encoded verbatim. Two fidelity gaps worth noting: the decomp dispatches on held-item *effect* tables (`LoadHeldItemEffect`) whereas bparkpk names four specific items, so other items sharing those effects may be under-matched; and the decomp also has `Fling power < 10 → −10` and `Multitype → −10` checks that bparkpk renders only as "not holding an item → −10". bparkpk kept per the precedence rule. |
| `basic` | `cc03fc27`, `0787d2cb`, `9c3ccefa`, … | Two-stat boost blocks penalise −10 then −8. Deliberate asymmetry or transcription drift? | Bulk Up / Calm Mind / Cosmic Power / Dragon Dance routines | Deliberate: the first stat at its cap scores −10, the second −8. Consistent across every two-stat block, so encoded as a shared helper. |
| `basic` | `31b6163f` (Explosion, Memento, Selfdestruct) | "If the user has other living party members: **no** score change" reads inverted. | Basic Explosion routine | Correct as scraped. Having party left is neutral; being the *last* Pokémon is what's judged — −10 if the target still has party members, −1 if they don't either. |
| `basic` | `077a7f8f` (Bide, Metal Burst) | Stall / Shiny Stone check. | `Basic_CheckMetalBurst` | See the "Confirmed-correct oddities" section above — a real vanilla bug (intended Lagging Tail), encoded verbatim. |

### Unresolved / approximated in `basic`

- **`98bef6c9` (Kinesis)** — bparkpk's block checks the target's *special defence* at −6, but `data/move_changes.csv` describes Kaizo's Kinesis as "Sharply lowers Accuracy". The two sources disagree about which stat the move even touches. Encoded per bparkpk (special defence) under the precedence rule; worth an empirical check.
- **`17698768` vs `b906281e`** — Brine/Clamp/Scald/Surf/Whirlpool check only Water Absorb, while the other Water block checks Water Absorb *or* Dry Skin. Kept verbatim rather than unified, since Kaizo's Dry Skin fix may not cover both groups.
- **`a035f4c0`** — the Flash Fire clause appears **twice** on the source page. Harmless (the first terminates); reproduced for fidelity.
- **`ea5a4dc4` (Natural Gift)** — "not holding a berry" is approximated as `item.endswith("Berry")`; a proper berry list from `data/` would be better.
- **`8f40e077` (Embargo)** — "no item it could Recycle" is read as having no `consumed_item`.

### Architectural consequence

Neither encoded block needs to classify move effects. The decomp selects moves via
`BATTLE_EFFECT_*` tables (`SetupFirstTurn_SetupEffects`) or damage-comparison
guards; we get the same partition for free from the scrape's move→block mapping,
and it is **Kaizo-correct** where the vanilla tables are not — the vanilla setup
table lists `BATTLE_EFFECT_CONVERSION`, and Conversion does not exist in Kaizo.
So flag modules encode only the *conditional logic inside* a block.
