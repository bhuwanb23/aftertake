from pathlib import Path
import re

for p in Path("compositions/frames").glob("*.html"):
    t = p.read_text(encoding="utf-8")
    nt = t.replace("\u00b7", "|")
    nt = re.sub(r"\s+\|\s+", " | ", nt)
    if nt != t:
        p.write_text(nt, encoding="utf-8")
        print("cleaned", p.name)
    else:
        print("same", p.name)

keys = ("class=\"label\"", "id=\"l1\"", "id=\"l2\"", "id=\"l3\"", "class=\"tag\"", "class=\"formula\"", "class=\"loop\"", "class=\"r\"", "class=\"mark\"")
for p in Path("compositions/frames").glob("*.html"):
    for line in p.read_text(encoding="utf-8").splitlines():
        if any(k in line for k in keys) and "<div" in line:
            print(f"{p.name}: {line.strip()[:120]}")
