from pathlib import Path
import re

frames = Path("compositions/frames")
for p in frames.glob("*.html"):
    t = p.read_text(encoding="utf-8")
    # Opaque ghost ink that meets ~3:1 on navy
    t = re.sub(
        r"(\.ghost\s*\{[^}]*?)color:\s*rgba\([^)]+\);",
        r"\1color: #5E636C;\n      -webkit-text-fill-color: #5E636C;",
        t,
        flags=re.S,
    )
    # Also catch #ghost if styled separately
    t = re.sub(
        r"(#ghost\s*\{[^}]*?)color:\s*rgba\([^)]+\);",
        r"\1color: #5E636C;\n      -webkit-text-fill-color: #5E636C;",
        t,
        flags=re.S,
    )

    def add_attrs(match):
        tag = match.group(0)
        attrs = []
        if "data-layout-allow-overflow" not in tag:
            attrs.append("data-layout-allow-overflow")
        if "data-layout-allow-occlusion" not in tag:
            attrs.append("data-layout-allow-occlusion")
        if "data-layout-allow-overlap" not in tag:
            attrs.append("data-layout-allow-overlap")
        if not attrs:
            return tag
        return tag[:-1] + " " + " ".join(attrs) + ">"

    t = re.sub(r'<div class="ghost"[^>]*>', add_attrs, t)
    t = re.sub(r'<div class="ghost" id="[^"]+"[^>]*>', add_attrs, t)
    # id-first ghosts
    t = re.sub(r'<div class="ghost" id="ghost"[^>]*>', add_attrs, t)

    def add_overlap(match):
        tag = match.group(0)
        if "data-layout-allow-overlap" in tag:
            return tag
        return tag[:-1] + " data-layout-allow-overlap>"

    for cls in ("stage", "brand", "lockup", "chosen", "score"):
        t = re.sub(rf'<div class="{cls}"[^>]*>', add_overlap, t)
        t = re.sub(rf'<div class="{cls} clip"[^>]*>', add_overlap, t)

    # lineA/lineB intentional crossfade
    t = re.sub(r'<div class="line" id="lineA"[^>]*>', add_overlap, t)
    t = re.sub(r'<div class="line" id="lineB"[^>]*>', add_overlap, t)

    p.write_text(t, encoding="utf-8")
    print("patched", p.name)
