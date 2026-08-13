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

### Architectural consequence

Neither encoded block needs to classify move effects. The decomp selects moves via
`BATTLE_EFFECT_*` tables (`SetupFirstTurn_SetupEffects`) or damage-comparison
guards; we get the same partition for free from the scrape's move→block mapping,
and it is **Kaizo-correct** where the vanilla tables are not — the vanilla setup
table lists `BATTLE_EFFECT_CONVERSION`, and Conversion does not exist in Kaizo.
So flag modules encode only the *conditional logic inside* a block.
