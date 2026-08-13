"""One-off scraper for PKMoveScoring: fetch every move page, extract the six
scaffolded flags' sections, save raw HTML, and dedupe per flag.
"""
import html
import json
import re
import time
import urllib.parse
from pathlib import Path

import requests

BASE = "https://bparkpk.github.io/PKMoveScoring/"
REPO = Path("/Users/tylerli/Desktop/Projects/PK-AI/kaizo-ai-calc")
RAW_DIR = REPO / "scrape_raw"
OUT_DIR = REPO / "aicalc" / "flags" / "_scraped"
INDEX_PATH = RAW_DIR / "index.html"

FLAGS = {
    "Basic": "basic",
    "Eval Att": "evaluate_attacks",
    "Expert": "expert",
    "Prio Damage": "prio_damage",
    "Baton Pass": "baton_pass",
    "Setup First Turn": "setup_first_turn",
}

UA = "Mozilla/5.0 (research scrape for kaizo-ai-calc; contact: tjli@mit.edu)"

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": UA})


def fetch(url: str) -> str:
    resp = SESSION.get(url, timeout=(5, 15))
    resp.raise_for_status()
    return resp.text


def get_move_links() -> list[tuple[str, str]]:
    """Returns list of (display_name, href) pairs from the dropdown nav."""
    text = INDEX_PATH.read_text() if INDEX_PATH.exists() else fetch(BASE)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(text)
    return re.findall(r'<a href="(move[^"]+\.html)">([^<]+)</a>', text)


def clean_section_text(raw: str) -> str:
    text = raw.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    lines = [line.strip() for line in text.split("\n")]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    collapsed = []
    for line in lines:
        if line == "" and collapsed and collapsed[-1] == "":
            continue
        collapsed.append(line)
    return "\n".join(collapsed)


def extract_flags(page_html: str) -> dict[str, str]:
    out = {}
    for site_label, key in FLAGS.items():
        pattern = (
            r'<h2 style="color:black;">\s*'
            + re.escape(site_label)
            + r'\s*</h2>\s*<p style="color:black;">(.*?)</p>'
        )
        m = re.search(pattern, page_html, re.DOTALL)
        out[key] = clean_section_text(m.group(1)) if m else "(MISSING SECTION)"
    return out


def main():
    links = get_move_links()
    print(f"Found {len(links)} move links")

    per_move = {}
    failures = []
    for i, (href, display_name) in enumerate(links, 1):
        move_id = href[len("move"):-len(".html")]
        raw_path = RAW_DIR / f"{move_id}.html"
        try:
            if raw_path.exists():
                page_html = raw_path.read_text()
            else:
                url = BASE + urllib.parse.quote(href, safe="/.-")
                try:
                    page_html = fetch(url)
                except Exception:
                    time.sleep(2.0)
                    page_html = fetch(url)
                raw_path.write_text(page_html)
                time.sleep(0.3)
        except Exception as e:
            failures.append((display_name, href, str(e)))
            print(f"[{i}/{len(links)}] FAILED {display_name}: {e}")
            continue

        per_move[display_name] = extract_flags(page_html)
        if i % 50 == 0:
            print(f"[{i}/{len(links)}] ...")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "per_move.json").write_text(json.dumps(per_move, indent=2))
    (OUT_DIR / "failures.json").write_text(json.dumps(failures, indent=2))
    print(f"Done. {len(per_move)} moves scraped, {len(failures)} failures.")


if __name__ == "__main__":
    main()
