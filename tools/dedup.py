"""Group scraped per-move flag text into distinct scoring blocks and write a
review-friendly summary.
"""
import json
import re
from collections import defaultdict
from pathlib import Path

REPO = Path("/Users/tylerli/Desktop/Projects/PK-AI/kaizo-ai-calc")
OUT_DIR = REPO / "aicalc" / "flags" / "_scraped"

FLAG_ORDER = ["basic", "evaluate_attacks", "expert", "prio_damage",
              "baton_pass", "setup_first_turn", "risky",
              "tag_opponent", "tag_ally", "check_hp", "weather", "harassment"]


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def main():
    per_move = json.loads((OUT_DIR / "per_move.json").read_text())

    lines = ["# Scraped & deduplicated AI scoring text\n"]
    lines.append(f"Source: https://bparkpk.github.io/PKMoveScoring/ ({len(per_move)} moves scraped)\n")
    lines.append("Not yet encoded into flags/*.py — extraction and dedup only.\n")

    counts = {}
    for flag in FLAG_ORDER:
        groups = defaultdict(list)   # normalized text -> [(display_text, [moves])]
        display_for_key = {}
        for move_name, sections in per_move.items():
            text = sections.get(flag, "(MISSING SECTION)")
            key = normalize(text)
            groups[key].append(move_name)
            display_for_key[key] = text

        empty_key = normalize("(No applicable AI procedures)")
        distinct_nonempty = [k for k in groups if k != empty_key]
        counts[flag] = {
            "distinct_scoring_blocks": len(distinct_nonempty),
            "moves_with_no_procedure": len(groups.get(empty_key, [])),
            "total_moves": len(per_move),
        }

        lines.append(f"\n## {flag}\n")
        lines.append(
            f"- {len(distinct_nonempty)} distinct scoring blocks "
            f"(+ {len(groups.get(empty_key, []))} moves with no applicable procedure) "
            f"out of {len(per_move)} moves\n"
        )

        # sort groups by group size descending, empty-procedure group last
        sorted_keys = sorted(
            (k for k in groups if k != empty_key),
            key=lambda k: -len(groups[k]),
        )
        for key in sorted_keys:
            moves = sorted(groups[key])
            lines.append(f"\n### Shared by {len(moves)} move(s): {', '.join(moves)}\n")
            lines.append("```\n" + display_for_key[key] + "\n```\n")

        if empty_key in groups:
            lines.append(f"\n### No applicable AI procedure ({len(groups[empty_key])} moves)\n")
            lines.append(", ".join(sorted(groups[empty_key])) + "\n")

    summary_lines = ["# Dedup counts per flag\n"]
    for flag in FLAG_ORDER:
        c = counts[flag]
        summary_lines.append(
            f"- **{flag}**: {c['distinct_scoring_blocks']} distinct scoring blocks to encode "
            f"({c['moves_with_no_procedure']}/{c['total_moves']} moves have no procedure for this flag)"
        )

    (OUT_DIR / "dedup.md").write_text("\n".join(summary_lines) + "\n\n---\n" + "\n".join(lines))
    (OUT_DIR / "dedup_counts.json").write_text(json.dumps(counts, indent=2))
    print("\n".join(summary_lines))


if __name__ == "__main__":
    main()
