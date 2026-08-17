"""Thumbnail agent verification per the Phase 2 Step 4 test plan (5 runs).

    backend/.venv/Scripts/python backend/agents/dev/verify_thumbnail.py

Run 1: full input -> 3 variants, schema-validated, ALL render at 1280x720
Run 2: same inputs -> consistent style across runs (background families,
       palette usage, text treatment)
Run 3: layout descriptions accurately describe the SVG (face, text, bg)
Run 4: text reflects the actual video topic (not generic placeholder text)
Run 5: colors match the profile's dominant_colors, plus the CRITICAL TEST:
       no blurred/abstract/gradient background anywhere (the profile's
       background_type is "solid color"; blurred backgrounds are a known
       low-performance signal for this creator)

Plus two varied-input runs (opp_002, opp_003) for Practice 6's "different
inputs" requirement. Every rendered PNG is saved to output/thumbnails/ so the
variants can be opened and eyeballed.

Hard failures (exit 1): any run != 3 variants, unparseable SVG, unrenderable
SVG, wrong dimensions, forbidden elements (gradients/filters/images/blur),
off-palette colors, missing FACE placeholder, no topic text, description
inaccuracy, or fewer than 2 distinct variants in a run.
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from backend.agents.dev.svgutil import (  # noqa: E402
    ALLOWED_FAMILIES, background_rect, color_family, colors, forbidden_elements,
    png_dimensions, render_svg, texts,
)
from backend.agents.dev.test_opportunity import get_dna_profile  # noqa: E402
from backend.agents.thumbnail_agent import run_thumbnail_agent  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent.parent
OPPS_CACHE = ROOT / "output" / "opportunities.json"
OUT_DIR = ROOT / "output" / "thumbnails"

STOP = {"the", "a", "an", "to", "of", "and", "for", "with", "on", "in", "by",
        "their", "your", "using", "that", "this", "into", "from", "what",
        "how", "why", "are", "is", "it"}


def topic_keywords(opportunity: dict) -> list[str]:
    """Significant tokens from the opportunity's topic AND working title
    (the agent receives both): numbers and words of length >= 3, stopwords
    removed. Any one matching the thumbnail text proves the text reflects
    the actual video."""
    blob = f"{opportunity.get('topic', '')} {opportunity.get('working_title', '')}"
    toks = re.split(r"[^a-z0-9]+", blob.lower())
    return [t for t in toks if (t.isdigit() or len(t) >= 3) and t not in STOP]


def check_variant(variant, keywords: list[str]) -> tuple[list[str], dict]:
    """Return (issues, info) for one variant. Every plan check is either a
    hard issue or recorded in info for the printed report."""
    svg, desc = variant.svg_source, variant.layout_description
    issues: list[str] = []
    info: dict = {}

    try:
        svg_texts = texts(svg)
    except ET.ParseError as exc:  # unclosed tags / unquoted attrs
        return [f"SVG not well-formed XML: {str(exc)[:100]}"], {}
    info["texts"] = svg_texts

    try:
        png = render_svg(svg)
        w, h = png_dimensions(png)
        info["render"] = f"{w}x{h}"
        if (w, h) != (1280, 720):
            issues.append(f"rendered at {w}x{h}, not 1280x720")
    except Exception as exc:  # noqa: BLE001 — render failure is the finding
        issues.append(f"render failed: {type(exc).__name__}: {str(exc)[:90]}")

    fb = forbidden_elements(svg)
    if fb:
        issues.append(f"forbidden elements (gradient/filter/image/blur...): {fb}")

    bg = background_rect(svg)
    info["bg"] = bg
    if bg is None:
        issues.append("no full-canvas solid background rect")
    elif bg[1] not in ("red", "orange", "darkblue", "black"):
        issues.append(f"background family '{bg[1]}' not from the palette")

    fams = sorted({color_family(c) for c in colors(svg)})
    info["color_families"] = fams
    bad = [f for f in fams if f not in ALLOWED_FAMILIES]
    if bad:
        issues.append(f"off-palette colors: {bad}")

    info["has_face"] = any("face" in t.lower() for t in svg_texts)
    if not info["has_face"]:
        issues.append("missing FACE placeholder label")

    raw_blob = " ".join(svg_texts)
    blob = raw_blob.lower()
    hits = [k for k in keywords if k in blob]
    info["topic_hits"] = hits
    if not hits:
        issues.append(f"no topic keyword in text {svg_texts}")

    letters = [ch for ch in raw_blob if ch.isalpha()]  # original case — never lowercase the measurement
    info["upper_ratio"] = round(sum(1 for ch in letters if ch.isupper()) / len(letters), 2) if letters else 0.0
    if info["upper_ratio"] < 0.5:
        issues.append(f"text not mostly all-caps (ratio {info['upper_ratio']})")

    d = desc.lower()
    info["desc_mentions_face"] = "face" in d
    if not info["desc_mentions_face"]:
        issues.append("layout_description does not mention the face placeholder")
    words = [w for w in re.split(r"[^a-z0-9]+", blob) if len(w) >= 3]
    uniq = set(words)
    missing = [w for w in uniq if w not in d]
    info["desc_missing_words"] = missing
    if uniq and len(missing) / len(uniq) > 0.5:
        issues.append(f"description misses {len(missing)}/{len(uniq)} text words: {missing}")
    if bg:
        bg_words = {"red": ["red"], "orange": ["orange"],
                    "darkblue": ["dark blue", "darkblue", "navy", "blue"],
                    "black": ["black"]}
        if not any(w in d for w in bg_words.get(bg[1], [bg[1]])):
            issues.append(f"description does not mention the background color ({bg[0]})")
    return issues, info


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--varied-only", action="store_true",
                        help="Only the varied-input runs (opp_002/opp_003) — cheap "
                             "re-check after a prompt fix")
    parser.add_argument("--main-only", action="store_true",
                        help="Only the 5 same-input runs (opp_001) — the plan's "
                             "done-definition bar")
    args = parser.parse_args()

    profile = get_dna_profile()
    opps = json.loads(OPPS_CACHE.read_text(encoding="utf-8"))
    if args.varied_only:
        runs = [("Varied opp_002", opps[1]), ("Varied opp_003", opps[2])]
    elif args.main_only:
        runs = [(f"Run {i}", opps[0]) for i in range(1, 6)]
    else:
        runs = [(f"Run {i}", opps[0]) for i in range(1, 6)] + \
               [("Varied opp_002", opps[1]), ("Varied opp_003", opps[2])]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    all_issues: list[str] = []
    bg_families: set[str] = set()
    for label, opp in runs:
        result = run_thumbnail_agent(opp, profile, asset_id=f"asset_{profile.creator_id}")
        variants = result.validated
        kws = topic_keywords(opp)
        print(f"\n=== {label} — opportunity: {opp['topic'][:80]} ===")
        if len(variants) != 3:
            all_issues.append(f"{label}: expected 3 variants, got {len(variants)}")
            continue
        fingerprints: list = []
        for i, v in enumerate(variants, 1):
            issues, info = check_variant(v, kws)
            if info.get("bg"):
                bg_families.add(info["bg"][1])
            print(f"  {v.id} | bg={info.get('bg')} | colors={info.get('color_families')} "
                  f"| render={info.get('render')} | upper={info.get('upper_ratio')} "
                  f"| face={'Y' if info.get('has_face') else 'N'} | topic_hits={info.get('topic_hits')}")
            print(f"      texts: {info.get('texts')}")
            print(f"      desc:  {v.layout_description}")
            if info.get("desc_missing_words"):
                print(f"      desc misses words: {info['desc_missing_words']}")
            if issues:
                for it in issues:
                    print(f"      ISSUE: {it}")
                all_issues += [f"{label} {v.id}: {it}" for it in issues]
            png_path = OUT_DIR / f"verify_{label.replace(' ', '_')}_{v.id}.png"
            try:
                png_path.write_bytes(render_svg(v.svg_source))
            except Exception:  # noqa: BLE001 — already reported above
                pass
            fingerprints.append((info.get("bg", (None, None))[1] if info.get("bg") else None,
                                frozenset(info.get("texts", []))))
        uniq = len(set(fingerprints))
        print(f"  distinct variants: {uniq}/3")
        if uniq < 2:
            all_issues.append(f"{label}: variants not meaningfully different ({uniq}/3)")

    print("\n=== SUMMARY ===")
    print(f"variants checked: {len(runs) * 3} ({len(runs)} runs)")
    print(f"background families used: {sorted(bg_families)} (must be within "
          f"red/orange/darkblue/black — solid color only)")
    if all_issues:
        print(f"HARD FAILURES: {len(all_issues)}")
        for it in all_issues:
            print(f"  - {it}")
        return 1
    print("ALL CHECKS PASS — every variant renders, follows the palette, "
          "carries topic text, has an accurate description, and uses a solid "
          "color background (no blurred/abstract/gradient anywhere).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
