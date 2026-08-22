"""Case: Roark's Bonsly vs a player Machop, turn 1.

Source: cases/roark-bonsly-vs-machop-turn1.png (HZLA calc screenshot).
Damage answers are hand-supplied from the calc's own damage panel, since the
damage calculator port (calc/) does not exist yet.

Assumptions not visible in the screenshot:
  * It is turn 1 of the whole battle (stated by the user).
  * Both trainers have living party members besides the active Pokemon
    (Roark is a gym leader mid-fight; the player is assumed not to be on
    their last Pokemon). This matters for Selfdestruct's and Stealth Rock's
    Basic checks.
  * Neither Pokemon has used a move yet (turn 1), so no last-move state.

Run:  python3 -m cases.roark_bonsly_vs_machop   (from the repo root)
"""
from fractions import Fraction

from aicalc.scoring import action_score_distributions, active_flags, flag_distribution
from aicalc.predicates import Context
from aicalc.select import action_probabilities
from aicalc.state import Battle, Field, Pokemon, Side, legal_actions

bonsly = Pokemon(
    species="Bonsly", level=15, ability="Rock Head", item="Focus Sash",
    types=("Rock",),
    stats={"atk": 33, "def": 41, "spa": 10, "spd": 23, "spe": 12},
    max_hp=44, current_hp=44, gender="M",
    moves=["Stealth Rock", "Selfdestruct", "Brick Break", "Accelerock"],
)

machop = Pokemon(
    species="Machop", level=16, ability="Guts", item=None,
    types=("Fighting",),
    stats={"atk": 33, "def": 25, "spa": 21, "spd": 21, "spe": 21},
    max_hp=53, current_hp=53, gender="M",
    moves=["Karate Chop", "Seismic Toss", "Rock Smash"],
)

battle = Battle(
    ai=Side(active=bonsly, party_remaining=2),
    player=Side(active=machop, party_remaining=1),
    field=Field(weather="sand", turn=1),
    flags={"basic", "evaluate_attacks", "expert", "risky"},
)


class CalcPanelBackend:
    """Damage answers read straight off the calculator's right-hand panel.

    Selfdestruct: 143.3-169.8% -> KOs on every roll (so certainly on the
    AI's max-roll check). Brick Break 26.4-32%, Accelerock 11.3-13.2%,
    Stealth Rock 0%.

    is_best_damaging_move answers over the AI's *comparable* damage table,
    not raw damage: TrainerAI_CalcAllDamage zeroes out any move whose effect
    is in sNoDamageCalcMoveEffects -- and Selfdestruct's HALVE_DEFENSE effect
    is the first entry -- so the comparison sees {Brick Break ~30%,
    Accelerock ~13%, everything else 0}. Brick Break is the AI's highest
    damaging move; Selfdestruct's own block never consults the comparison
    (NO_COMPARISON_MADE short-circuit, which is why its scraped block has no
    "-1 if outdamaged" branch). See DECOMP_NOTES.md.
    """

    def can_ko(self, battle, action):
        return action.move == "Selfdestruct"

    def is_best_damaging_move(self, battle, action):
        return action.move == "Brick Break"

    def effectiveness(self, battle, action):
        return {
            "Selfdestruct": 1,     # Normal vs Fighting
            "Brick Break": 0.5,    # Fighting vs Fighting
            "Accelerock": 0.5,     # Rock vs Fighting
            "Stealth Rock": 0.5,   # Rock vs Fighting (never consulted for 4x)
        }[action.move]

    # Expert-only questions; none should fire for these four moves, but the
    # answers are supplied so nothing can silently default.
    def has_super_effective_move(self, battle):
        return False               # best is 1x Selfdestruct

    def party_member_outdamages(self, battle):
        return False

    def target_last_move_outdamages(self, battle):
        return False


def main():
    backend = CalcPanelBackend()
    print(f"active flags: {active_flags(battle)}\n")

    for action in legal_actions(battle):
        ctx = Context(battle=battle, action=action, damage=backend)
        parts = {f: flag_distribution(f, ctx) for f in active_flags(battle)}
        print(f"{action.move}:")
        for f, dist in parts.items():
            if dist.table != {0: Fraction(1)}:
                print(f"    {f:18} {dist}")
        print()

    dists = action_score_distributions(battle, backend)
    print("final score distributions (base 100):")
    for action, dist in dists.items():
        print(f"    {action.move:14} {dist}")

    print("\npick probabilities:")
    for action, p in sorted(action_probabilities(dists).items(),
                            key=lambda kv: -kv[1]):
        print(f"    {action.move:14} {float(p) * 100:7.3f}%   ({p})")


if __name__ == "__main__":
    main()
