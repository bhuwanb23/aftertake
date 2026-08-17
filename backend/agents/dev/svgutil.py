"""Shared SVG render/analyze helpers for the thumbnail agent dev scripts
(Phase 2 Step 4). Phase 3's rendering/thumbnails.py will own the production
render path; these helpers exist so the isolation scripts can prove the
SVGs actually render and follow the creator's style.

Renderer note: resvg-py is used because cairosvg needs a system cairo
library that is not present on this machine (Phase 0 Step 3f named resvg-py
as the fallback for exactly this situation). resvg_py.svg_to_bytes() takes
the raw SVG string and returns PNG bytes.
"""
import xml.etree.ElementTree as ET

import resvg_py

SVG_NS = "http://www.w3.org/2000/svg"


def render_svg(svg: str) -> bytes:
    """Render an SVG string to PNG bytes. Raises on unrenderable SVG."""
    return resvg_py.svg_to_bytes(svg_string=svg)


def png_dimensions(png: bytes) -> tuple[int, int]:
    """Width/height from a PNG's IHDR chunk (bytes 16-24, big-endian)."""
    return int.from_bytes(png[16:20], "big"), int.from_bytes(png[20:24], "big")


def parse_svg(svg: str) -> ET.Element:
    """Parse SVG as XML. Raises ET.ParseError when not well-formed (unclosed
    tags, unquoted attributes) — which is itself a renderability failure."""
    return ET.fromstring(svg)


def elements(svg: str) -> list[str]:
    """Tag names in document order (no namespace prefix)."""
    root = parse_svg(svg)
    return [t.tag.split("}")[-1].lower() for t in root.iter()]


def texts(svg: str) -> list[str]:
    """The visible text content of every <text> element, in order."""
    root = parse_svg(svg)
    return [t.text.strip() for t in root.iter(f"{{{SVG_NS}}}text") if (t.text or "").strip()]


def colors(svg: str) -> list[str]:
    """Every fill/stroke value used, lowercased, excluding 'none'."""
    root = parse_svg(svg)
    out: list[str] = []
    for el in root.iter():
        for attr in ("fill", "stroke"):
            v = el.get(attr)
            if v and v.lower() != "none":
                out.append(v.lower())
    return out


# Elements that violate the prompt's technical spec (no gradients, no
# filters, no images, no external references, no blur).
FORBIDDEN = {
    "defs", "lineargradient", "radialgradient", "pattern", "filter",
    "image", "clippath", "mask", "foreignobject", "style", "script",
    "fegaussianblur", "feimage", "use",
}


def forbidden_elements(svg: str) -> list[str]:
    return [tag for tag in elements(svg) if tag in FORBIDDEN]


def background_rect(svg: str) -> tuple[str, str] | None:
    """(fill, family) of the full-canvas background rect, or None."""
    root = parse_svg(svg)
    for el in root.iter(f"{{{SVG_NS}}}rect"):
        w = float(el.get("width", "0") or 0)
        h = float(el.get("height", "0") or 0)
        if w >= 1200 and h >= 650:  # covers the 1280x720 canvas
            fill = (el.get("fill") or "").lower()
            if fill and fill != "none":
                return fill, color_family(fill)
    return None


def _hex_to_rgb(c: str) -> tuple[int, int, int]:
    c = c.lstrip("#")
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


NAMED = {
    "red": "red", "crimson": "red", "darkred": "red", "firebrick": "red", "tomato": "red",
    "orange": "orange", "darkorange": "orange", "orangered": "orange",
    "navy": "darkblue", "darkblue": "darkblue", "midnightblue": "darkblue",
    "blue": "darkblue", "royalblue": "darkblue", "steelblue": "darkblue",
    "black": "black",
    "white": "white", "whitesmoke": "white",
    "gray": "neutral", "grey": "neutral", "darkgray": "neutral", "dimgray": "neutral",
    "silver": "neutral", "lightgray": "neutral", "lightgrey": "neutral",
}


def color_family(color: str) -> str:
    """Classify an SVG color into the profile's palette families (red, orange,
    darkblue, black), plus white (bold text), neutral (face placeholder /
    props), or 'other' (off-palette — a violation)."""
    c = color.lower().strip()
    if c.startswith("#"):
        try:
            r, g, b = _hex_to_rgb(c)
        except ValueError:
            return "other"
        if r > 200 and g < 110 and b < 110:
            return "red"
        if r > 200 and 90 <= g <= 190 and b < 110:
            return "orange"
        if b > 120 and r < 110 and g < 150:
            return "darkblue"
        if max(r, g, b) < 70:
            return "black"
        if min(r, g, b) > 220:
            return "white"
        if max(r, g, b) - min(r, g, b) < 40:
            return "neutral"
        return "other"
    return NAMED.get(c, "other")


ALLOWED_FAMILIES = {"red", "orange", "darkblue", "black", "white", "neutral"}
