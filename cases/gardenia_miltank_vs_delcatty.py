"""Case: Gardenia's Miltank vs a player Delcatty, turn 1, rain up.

Source: cases/gardenia-miltank-vs-delcatty-turn1.png (HZLA calc screenshot).
Damage answers are hand-supplied from the calc's own damage panel.

Flags on Miltank: Basic, Evaluate Atks, Expert, 1st Turn Setup. Note that the
1st Turn Setup flag contributes nothing to this moveset even on turn 1: its
effect table covers stat stages, screens, Tailwind and status-inducing moves,
and hazards are not in it -- Stealth Rock is not a "setup" move to this AI.

Assumptions not visible in the screenshot:
  * It is turn 1 of the whole battle.
  * Both trainers have living party members besides the active Pokemon.

Run:  python3 -m cases.gardenia_miltank_vs_delcatty   (from the repo root)
"""
from fractions import Fraction

from aicalc.scoring import action_score_distributions, active_flags, flag_distribution
from aicalc.predicates import Context
from aicalc.select import action_probabilities
from aicalc.state import Battle, Field, Pokemon, Side, legal_actions

miltank = Pokemon(
    species="Miltank", level=26, ability="Scrappy", item="Lum Berry",
    types=("Normal",),
    stats={"atk": 64, "def": 67, "spa": 33, "spd": 44, "spe": 65},
    max_hp=93, current_hp=93, gender="F",
    moves=["Stealth Rock", "Milk Drink", "Body Slam", "ThunderPunch"],
)

delcatty = Pokemon(
    species="Delcatty", level=28, ability="Cute Charm", item=None,
    types=("Normal",),
    stats={"atk": 58, "def": 55, "spa": 58, "spd": 55, "spe": 76},
    max_hp=85, current_hp=85, gender="M",
    moves=["Hyper Voice", "Copycat", "Quick Attack"],
)

battle = Battle(
    ai=Side(active=miltank, party_remaining=2),
    player=Side(active=delcatty, party_remaining=1),
    field=Field(weather="rain", turn=1),
    flags={"basic", "evaluate_attacks", "expert", "setup_first_turn"},
)


class CalcPanelBackend:
    """Damage answers from the calculator panel (Miltank -> Delcatty):
    Body Slam 38.8-47%, ThunderPunch 27-32.9%, Stealth Rock / Milk Drink 0%.

    Nothing KOs. The comparable-damage table (see DECOMP_NOTES.md) is
    {Body Slam, ThunderPunch} -- both plain damaging effects -- so Body Slam
    is the AI's highest damaging move.
    """

    def can_ko(self, battle, action):
        return False

    def is_best_damaging_move(self, battle, action):
        return action.move == "Body Slam"

    def effectiveness(self, battle, action):
        return {
            "Body Slam": 1,       # Normal vs Normal
            "ThunderPunch": 1,    # Electric vs Normal
            "Stealth Rock": 1,    # Rock vs Normal (never consulted for 4x)
            "Milk Drink": 1,      # status
        }[action.move]

    def has_super_effective_move(self, battle):
        return False

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
