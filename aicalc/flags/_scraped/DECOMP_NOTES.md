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

### The damage comparison excludes suicide/charge/etc. moves — `is_best_damaging_move` semantics

Caught via the Roark/Bonsly case (the first hand-supplied backend answered this
wrong). "A different move the user knows would do more damage" is computed by
`AICmd_FlagMoveDamageScore` → `TrainerAI_CalcAllDamage` (`trainer_ai.c:2799`),
which fills a per-move damage table where a move counts as **0** unless it has
power > 1 and its effect is *not* in `sNoDamageCalcMoveEffects`:

> HALVE_DEFENSE (Selfdestruct/Explosion), RECOVER_DAMAGE_SLEEP (Dream Eater),
> the charge-turn effects (Razor Wind/Sky Attack/Fly-likes, SolarBeam),
> RECHARGE_AFTER (Hyper Beam-likes), SPIT_UP, HIT_LAST_WHIFF_IF_HIT (Focus
> Punch), LOWER_OWN_ATK_AND_DEF (Superpower), DECREASE_POWER_WITH_LESS_USER_HP
> (Eruption/Water Spout), HIT_FIRST_IF_TARGET_ATTACKING (Sucker Punch),
> RECOIL_HALF.

Consequences:

- A Selfdestruct that out-damages everything **does not** cause other moves to
  take Evaluate Attacks' "-1 if outdamaged" — the comparison never sees it.
- When the *current* move is one of these effects (or is a status move), the
  command short-circuits to `AI_NO_COMPARISON_MADE` — which is exactly why the
  scraped suicide block has no "-1 if outdamaged" branch, and what gates
  `prio_damage`/`baton_pass`.
- `sAltPowerMoveEffects` moves get substitute powers instead — and this maps
  one-to-one onto bparkpk's own eval-block notes (Bulldoze "uses Magnitude
  calculations", Triple Axel "uses Psywave calculations", Return "seen as
  102BP"), strong evidence the mechanism is intact in Kaizo. Per-move
  membership must follow the move's **Kaizo** effect from `data/moves.csv`,
  not its vanilla one.

Any hand-supplied `DamageBackend.is_best_damaging_move` must answer over this
comparable table, not over raw damage output.

## Damage-calc port notes (aicalc/calc/)

Findings from porting TrainerAI_CalcDamage / BattleSystem_CalcMoveDamage /
BattleSystem_ApplyTypeChart, beyond what the sections above already cover:

- **Two variance orderings.** The battle engine applies the 85–100 roll to
  base damage *before* the type chart (screenshot roll lists like Karate
  Chop's `18,18,18,20,...,24` reproduce only under that order), while
  `TrainerAI_CalcDamage` applies variance *after* `ApplyTypeChart`
  (`damage * variance / 100`, trainer_ai.c:3105). At the AI's max roll
  (variance 100) the orders coincide, which is why the panels' max values
  are valid oracles for the AI path.
- **The AI's effectiveness buckets have blind spots, ported faithfully.**
  `AICmd_IfMoveEffectivenessEquals` starts damage at 40, lets the chart (and
  STAB) scale it, remaps only {120→80, 240→160, 30→20, 15→10}, and compares
  for exact equality. Plain STAB-neutral lands on 60 → multiplier 1.5 →
  matches no block's check; Scrappy/Foresight bypassing a Ghost immunity
  *skips* the immunity rows (neutral), it does not create super-effectiveness;
  Filter/Expert Belt/Tinted Lens distort damage off the buckets so the AI
  sees "nothing". `effectiveness_bucket` returns these off-bucket values
  (1.5, …) so equality checks fail exactly as in-game.
- **Random power inside the AI calc.** Magnitude (Kaizo Bulldoze) and Psywave
  (Kaizo Triple Axel) roll on every `TrainerAI_CalcDamage` call with a fresh
  `BattleSystem_RandNext` — per consultation, not per turn. Facts that the
  tiers disagree on raise `AmbiguousRandomDamage`; the exact model is a
  Bernoulli per consultation (a `Chance`-valued predicate), a documented
  follow-up. Torterra case numbers: Bulldoze AI-side tier damage
  {7,18,28,39,48,58,79} vs Seed Bomb 43 — 35% of rolls out-damage it.
- **`BattleSystem_Divide` clamps.** Nonzero dividends never divide to 0 —
  they clamp to ±1 (battle_lib.c:3599). Ported as `game_divide`.
- **The self-defender quirk** in `AICmd_IfBattlerDealsMoreDamage`
  (trainer_ai.c:2188): the target's last move is evaluated with the target as
  attacker *and* defender (TrainerAI_CalcDamage always defends with
  `AI_CONTEXT.defender`), and with the AI's own IVs. Ported verbatim.
- **Vanilla-slot dispatch.** The special-power switch keys on move IDs, so the
  port dispatches on moves.csv's "ID Number" (the vanilla slot a Kaizo move
  occupies): 222 Magnitude→Bulldoze, 149 Psywave→Triple Axel, 216 Return
  (friendship 255 → the "seen as 102BP" note), 218 Frustration (power 0 at
  255 friendship → falls back to the CSV's 121), 49/69/82/101 fixed damage,
  360 Gyro Ball, 67/447 weight moves (need `Pokemon.weight_hg`).
- **Comparable set = `prio_damage` scrape membership.** Kaizo-correct with no
  effect-index engineering; the tripwire test cross-checks it against
  moves.csv every run (status ⇒ excluded; comparable at power≤1 ⇒ must have a
  special dispatch).

## Cascade termination convention (found via the Ludicolo case)

Three decomp routines (`Expert_HighCritical`, `Expert_StatusParalyze`,
`Expert_Encore`) establish the convention for prose like "If C: p% chance of
±N **and terminate**" inside an if/elif cascade: **once the branch is entered,
both sides of the roll terminate** — a missed roll goes to the End label, it
never falls back into the remaining cascade conditions. (Paralyze: a slower
attacker whose 92.2% roll misses scores 0; the HP≤70% −1 check is never
reached.) `Expert_HighCritical` also shows the compiler-golf form: the
"otherwise" path chains **two** 128/256 rolls through the shared TryScorePlus1
label to make 25%.

Two engine bugs fixed accordingly (both caught by the Ludicolo case, whose
STAB attacks produce the off-bucket 1.5): `Context.super_effective()` /
`resisted()` now use exact bucket membership (`in (2, 4)` / `in (0, 0.25,
0.5)`) instead of ordering comparisons, matching `IfMoveEffectivenessEquals`;
and expert block `b28ff4b6` no longer lets a missed SE roll fall through into
the otherwise-roll.

**Open audit**: other expert.py cascades encoded as
`Seq(If(C, Chance(n, d, _stop(x))), <more>)` let the miss fall through. Where
the later conditions are mutually exclusive with C (e.g. the Selfdestruct
block's HP bands, verified pin-safe) the outcome is identical; where they
overlap, the encoding is wrong. A systematic block-by-block pass against the
scraped texts is pending — ~40 candidate sites.

### Priority kills: +6 needs the PRIORITY_1 *effect*, not data priority

Challenged via a UI scenario (Bonsly vs a 2-HP Grotle: Brick Break and
Accelerock both KO, engine says 50/50, intuition says "priority kill wins").
The engine is right. `EvalAttack_ApplyKillBonuses`' +2-then-+4 fall-through
fires on `IfCurrentMoveEffectEqualTo BATTLE_EFFECT_PRIORITY_1` — and the
decomp's own comment warns "this checks the move's _effect_, not the priority
score in its data". The vendored Kaizo effect indices (`data/move_effects.csv`)
confirm: bparkpk's seven +6 moves are exactly the seven with effect
PRIORITY_1, while **Accelerock, ExtremeSpeed and Sucker Punch carry priority
via the data field with effect HIT** — the AI gives their kills the ordinary
+4. Third member of the effect-index blind-spot family (with Bulldoze's
invisible speed drop and Selfdestruct's damage-comparison exclusion). A
tripwire test pins the +6 block to the PRIORITY_1 effect set. Empirical check
if ever doubted: a 2-HP save-state — real Bonsly picking ~50/50 between two
killing moves confirms; ~100% Accelerock refutes.

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

### Notes on `expert` (114 blocks)

Expert is the only flag that mixes "and continue" with "and terminate"
throughout, so later clauses frequently compound onto earlier ones. Two
consequences worth knowing:

- **Ladders cascade.** Power Swap / Guard Swap's tiered checks each terminate
  on success but fall through on failure into the next-lower tier, which is
  also satisfied. A target at +4/+4 therefore spreads across every tier
  (½ at +5, ¼ at +4, ⅛ at +3, …) rather than being one coin flip on +5.
  Both also bail out entirely if the target's second stat is *exactly* one
  stage higher than the user's — a quirk that makes +1/+1 score nothing even
  though it sums to 2.
- **Counter / Mirror Coat are mirror images** and are encoded from one shared
  builder: each rewards the opposite damage class, treats the other as a
  partner-move bonus, and shares the same type-immunity bail-out list.

`expert` is also the first flag needing the **move table** (`aicalc/movedata.py`,
backed by `data/moves.csv`), since it asks about moves other than the one being
scored — "was the foe's last move special?", "does the user have a damaging
move?", "does the foe know a high-crit move?". Names are joined through
`data/move_aliases.json`.

Three new damage-backend questions were added for it, on the same
hand-supplied contract as `can_ko`: `has_super_effective_move`,
`party_member_outdamages`, and `target_last_move_outdamages` (U-turn, Copycat,
Me First).

**Taunt.** Several blocks (Counter, Mirror Coat, Bide, Metal Burst) test
whether the foe is Taunted. Taunt does not exist in Kaizo — the slot became
HP Dark — so `"taunt"` is a valid volatile name that can never become true.
Encoded faithfully rather than stripped, so the scripts still match the source
if Kaizo ever restores it.

**Encore's trigger list** is flagged on the source page as a vanilla list, and
it shows: it contains Conversion, Splash, Nightmare, Trick, Switcheroo, Heal
Block, Healing Wish, Mud/Water Sport and Spit Up, none of which exist in Kaizo.
Kept verbatim; those entries simply never match.

### Unresolved / approximated in `basic`

- **`98bef6c9` (Kinesis)** — **flagged as likely wrong; awaiting an in-game test.**
  bparkpk's block checks the target's *special defence* at −6, but every other
  signal points at accuracy:
    - `data/moves.csv` and `move_changes.csv` both give Kaizo's Kinesis as
      "Sharply lowers Accuracy" (the Kaizo change is only 80→100 acc and
      targeting, not the stat it drops).
    - **Vanilla Platinum Kinesis also lowers accuracy**, so there is no
      version in which special defence is the natural reading.
  The decomp cannot break the tie: it has *no* scoring-relevant reference to
  Kinesis at all (the only hits repo-wide are its battle animation, e.g.
  `KinesisSpoon` / `SPRITE_FUNC_KINESIS`). That is expected, since `Basic_Main`
  dispatches on the move's **effect constant**, never on move name — and the
  per-move effect assignment lives in a binary data table the decomp doesn't
  expose in source, so there's no indirect path either.
  Currently encoded per bparkpk (special defence) to honour the precedence
  rule, but unlike the other entries in this section this one has two
  independent sources against it and zero for it beyond the scrape itself.
  If the in-game test confirms accuracy, change the stat key in
  `flags/basic.py` block `98bef6c9` from `"spd"` to `"acc"` — note that
  accuracy-drop moves elsewhere in this flag use the `_accuracy_drop` shape
  (which also checks No Guard / Keen Eye), so check whether Kinesis should
  move to that helper rather than just swapping the stat.
- **`17698768` vs `b906281e`** — Brine/Clamp/Scald/Surf/Whirlpool check only Water Absorb, while the other Water block checks Water Absorb *or* Dry Skin. Kept verbatim rather than unified, since Kaizo's Dry Skin fix may not cover both groups.
- **`a035f4c0`** — the Flash Fire clause appears **twice** on the source page. Harmless (the first terminates); reproduced for fidelity.
- **`ea5a4dc4` (Natural Gift)** — "not holding a berry" is approximated as `item.endswith("Berry")`; a proper berry list from `data/` would be better.
- **`8f40e077` (Embargo)** — "no item it could Recycle" is read as having no `consumed_item`.

| `risky` | `d4faa70a` (61 moves) | Same "Unconditionally" question as `prio_damage`. | `Risky_Main` | Gated on the `Risky_RiskyEffects` effect table (sleep, halve-defense, copy-move, OHKO, high-crit, confusion, call-random-move, Psywave-like) — the gate lives in the move→block mapping. `IfRandomLessThan 128` jumps to terminate → +2 at 128/256 = 50%, matching bparkpk. Kaizo-consistency check: Sheer Cold (no longer OHKO in Kaizo) is correctly absent from the scraped move list, while Triple Axel and Fury Cutter (Risky per `ai_changes.csv`) are correctly present. |

| `expert` | Bulldoze (vs `Expert_SpeedDownOnHit`) | Bulldoze lowers Speed in battle and the attacker-slower bonus (72.7% +2) exists for Icy Wind/Rock Tomb/Mud Shot — why does Bulldoze's page say "(No applicable AI procedures)"? | `Expert_Main` dispatch (`script.s:1681`) | Principled, not an omission. Expert dispatches on effect index: `BATTLE_EFFECT_LOWER_SPEED_HIT → Expert_SpeedDownOnHit`, and Magnitude's effect has **no** Expert handler (its only AI mention is doubles-only TagStrategy). Kaizo's Bulldoze occupies Magnitude's slot and keeps Magnitude's effect index for AI purposes — bparkpk's own eval-page testing note says "Bulldoze uses Magnitude calculations for scoring purposes", and the sibling speed-lower moves' pages all carry the block, so the site knew the routine and excluded Bulldoze deliberately. Net effect: **the AI cannot see Bulldoze's speed drop.** High-stakes (flips the Torterra/Mr. Mime case from Seed Bomb 100% to Bulldoze ~72.7% if wrong) — good save-state resampling candidate. |

### Architectural consequence

Neither encoded block needs to classify move effects. The decomp selects moves via
`BATTLE_EFFECT_*` tables (`SetupFirstTurn_SetupEffects`) or damage-comparison
guards; we get the same partition for free from the scrape's move→block mapping,
and it is **Kaizo-correct** where the vanilla tables are not — the vanilla setup
table lists `BATTLE_EFFECT_CONVERSION`, and Conversion does not exist in Kaizo.
So flag modules encode only the *conditional logic inside* a block.
