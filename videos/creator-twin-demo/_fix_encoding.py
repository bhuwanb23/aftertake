from pathlib import Path
import re

repls = [
    ("Â·", " · "),
    ("â€”", " - "),
    ("â€“", "-"),
    ("â†’", " -> "),
    ("âœ“", "OK"),
]

for p in Path("compositions/frames").glob("*.html"):
    t = p.read_text(encoding="utf-8")
    orig = t
    for a, b in repls:
        t = t.replace(a, b)
    t = re.sub(r"Stages 06.+?07", "Stages 06-07", t)
    if t != orig:
        p.write_text(t, encoding="utf-8")
        print("fixed", p.name)
    else:
        print("ok", p.name)

# Show any remaining non-ascii in visible text lines
for p in Path("compositions/frames").glob("*.html"):
    for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        if any(ord(ch) > 127 for ch in line) and ("<" in line or "div" in line or "label" in line):
            if "font" in line or "linear" in line or "radial" in line or "url(" in line or "rgba" in line:
                continue
            bad = "".join(ch for ch in line if ord(ch) > 127)
            if bad:
                print(f"{p.name}:{i}: {bad!r} :: {line.strip()[:100]}")
