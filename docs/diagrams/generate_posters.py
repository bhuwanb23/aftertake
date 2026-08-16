# -*- coding: utf-8 -*-
"""Generate Creator Twin architecture poster SVGs (ASCII-safe) and convert to PNG."""
from pathlib import Path

DIR = Path(__file__).resolve().parent

COMMON_DEFS = """
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#F2F5F8"/>
      <stop offset="100%" stop-color="#E4EAEF"/>
    </linearGradient>
  </defs>
  <rect width="1920" height="1080" fill="url(#bg)"/>
  <rect width="1920" height="8" fill="#FF5A36"/>
"""

FOOTER = (
    '<text x="96" y="{y}" font-family="Segoe UI, Helvetica, Arial, sans-serif" '
    'font-size="16" fill="#8A96A3">{label}</text>'
)


def wrap(body: str) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080">\n'
        f"{body}\n</svg>\n"
    )


def poster_01() -> str:
    return wrap(
        COMMON_DEFS
        + """
  <text x="96" y="88" font-family="Georgia, 'Times New Roman', serif" font-size="56" font-weight="700" fill="#0B1F33">Creator Twin</text>
  <text x="96" y="132" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="22" fill="#5A6A7A">A personalized, self-improving content decision engine</text>

  <rect x="96" y="176" width="1728" height="120" rx="8" fill="#0B1F33"/>
  <text x="128" y="230" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="18" fill="#FF5A36" font-weight="600" letter-spacing="3">THE PITCH</text>
  <text x="128" y="268" font-family="Georgia, 'Times New Roman', serif" font-size="26" fill="#F7F9FB">Not topic-in / video-out. An editorial brain that learns a creator, decides what to make next, and gates every asset before it ships.</text>

  <g transform="translate(96, 340)">
    <rect width="400" height="420" rx="10" fill="#FFFFFF" stroke="#C5D0DB" stroke-width="1.5"/>
    <rect width="400" height="8" fill="#FF5A36"/>
    <text x="32" y="56" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="14" fill="#FF5A36" font-weight="700" letter-spacing="2">01  LEARN</text>
    <text x="32" y="110" font-family="Georgia, 'Times New Roman', serif" font-size="32" fill="#0B1F33">Creator DNA</text>
    <text x="32" y="165" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="18" fill="#5A6A7A">Ingest titles, transcripts,</text>
    <text x="32" y="193" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="18" fill="#5A6A7A">thumbnails and real</text>
    <text x="32" y="221" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="18" fill="#5A6A7A">performance. Extract voice,</text>
    <text x="32" y="249" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="18" fill="#5A6A7A">hooks, title formula,</text>
    <text x="32" y="277" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="18" fill="#5A6A7A">thumbnail style.</text>
    <circle cx="48" cy="340" r="10" fill="#FF5A36"/>
    <text x="72" y="346" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="15" fill="#0B1F33">Who you already are</text>

    <g transform="translate(440,0)">
      <rect width="400" height="420" rx="10" fill="#FFFFFF" stroke="#C5D0DB" stroke-width="1.5"/>
      <rect width="400" height="8" fill="#2E6B9E"/>
      <text x="32" y="56" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="14" fill="#2E6B9E" font-weight="700" letter-spacing="2">02  DECIDE</text>
      <text x="32" y="110" font-family="Georgia, 'Times New Roman', serif" font-size="32" fill="#0B1F33">Opportunity</text>
      <text x="32" y="165" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="18" fill="#5A6A7A">Cross DNA with niche trends.</text>
      <text x="32" y="193" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="18" fill="#5A6A7A">Recommend next ideas with</text>
      <text x="32" y="221" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="18" fill="#5A6A7A">fit score + rationale tied to</text>
      <text x="32" y="249" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="18" fill="#5A6A7A">the creator's own wins.</text>
      <circle cx="48" cy="340" r="10" fill="#2E6B9E"/>
      <text x="72" y="346" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="15" fill="#0B1F33">What to make next</text>
    </g>

    <g transform="translate(880,0)">
      <rect width="400" height="420" rx="10" fill="#FFFFFF" stroke="#C5D0DB" stroke-width="1.5"/>
      <rect width="400" height="8" fill="#00A86B"/>
      <text x="32" y="56" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="14" fill="#00A86B" font-weight="700" letter-spacing="2">03  GATE</text>
      <text x="32" y="110" font-family="Georgia, 'Times New Roman', serif" font-size="32" fill="#0B1F33">Style-Fit</text>
      <text x="32" y="165" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="18" fill="#5A6A7A">Critic agent checks assets</text>
      <text x="32" y="193" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="18" fill="#5A6A7A">against Creator DNA.</text>
      <text x="32" y="221" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="18" fill="#5A6A7A">Below threshold: reject and</text>
      <text x="32" y="249" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="18" fill="#5A6A7A">regenerate. Judgment.</text>
      <circle cx="48" cy="340" r="10" fill="#00A86B"/>
      <text x="72" y="346" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="15" fill="#0B1F33">Does it actually sound like you?</text>
    </g>

    <g transform="translate(1320,0)">
      <rect width="408" height="420" rx="10" fill="#FFFFFF" stroke="#C5D0DB" stroke-width="1.5"/>
      <rect width="408" height="8" fill="#0B1F33"/>
      <text x="32" y="56" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="14" fill="#0B1F33" font-weight="700" letter-spacing="2">04  IMPROVE</text>
      <text x="32" y="110" font-family="Georgia, 'Times New Roman', serif" font-size="32" fill="#0B1F33">Feedback</text>
      <text x="32" y="165" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="18" fill="#5A6A7A">Real post performance</text>
      <text x="32" y="193" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="18" fill="#5A6A7A">feeds back into DNA.</text>
      <text x="32" y="221" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="18" fill="#5A6A7A">Recommendations get</text>
      <text x="32" y="249" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="18" fill="#5A6A7A">sharper over time.</text>
      <circle cx="48" cy="340" r="10" fill="#0B1F33"/>
      <text x="72" y="346" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="15" fill="#0B1F33">Close the loop</text>
    </g>
  </g>
"""
        + FOOTER.format(
            y=1020,
            label="Architecture poster 01  |  System overview  |  aftertake / Creator Twin",
        )
    )


def poster_02() -> str:
    stages = [
        (96, "#FF5A36", "STAGE 1", "Creator DNA", "Ingest + extract"),
        (316, "#FF5A36", "STAGE 2", "Opportunity", "Next idea + fit"),
        (536, "#2E6B9E", "STAGE 3", "Script Agent", "Voice + pacing"),
        (756, "#2E6B9E", "STAGE 4", "Video Render", "HyperFrames"),
        (976, "#2E6B9E", "STAGE 5", "Captions", "Whisper + burn-in"),
        (1196, "#2E6B9E", "STAGE 6", "Thumbnails", "SVG to PNG"),
        (1416, "#2E6B9E", "STAGE 7", "Metadata", "Title / SEO"),
    ]
    boxes = []
    for x, color, stage, title, sub in stages:
        boxes.append(
            f"""
    <rect x="{x}" y="210" width="180" height="100" rx="8" fill="#FFFFFF" stroke="{color}" stroke-width="2"/>
    <text x="{x+16}" y="245" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="12" fill="{color}" font-weight="700">{stage}</text>
    <text x="{x+16}" y="275" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="16" fill="#0B1F33" font-weight="600">{title}</text>
    <text x="{x+16}" y="296" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="12" fill="#5A6A7A">{sub}</text>"""
        )
        if x > 96:
            boxes.append(
                f'<line x1="{x-40}" y1="260" x2="{x-8}" y2="260" stroke="#2E6B9E" stroke-width="2"/>'
            )
            boxes.append(
                f'<polygon points="{x-8},254 {x},260 {x-8},266" fill="#2E6B9E"/>'
            )

    return wrap(
        COMMON_DEFS
        + """
  <text x="96" y="88" font-family="Georgia, 'Times New Roman', serif" font-size="48" font-weight="700" fill="#0B1F33">End-to-End Pipeline</text>
  <text x="96" y="128" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="20" fill="#5A6A7A">Eleven stages | one orchestrator | logged decisions at every gate</text>

  <text x="96" y="190" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="13" fill="#FF5A36" font-weight="700" letter-spacing="2">PHASE A - PROFILE</text>
  <text x="536" y="190" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="13" fill="#2E6B9E" font-weight="700" letter-spacing="2">PHASE B - CREATE</text>
  <text x="1636" y="190" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="13" fill="#00A86B" font-weight="700" letter-spacing="2">GATE</text>
"""
        + "\n".join(boxes)
        + """
  <rect x="1636" y="210" width="188" height="100" rx="8" fill="#0B1F33" stroke="#00A86B" stroke-width="3"/>
  <text x="1652" y="245" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="12" fill="#00A86B" font-weight="700">STAGE 8</text>
  <text x="1652" y="275" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="16" fill="#FFFFFF" font-weight="600">Style-Fit Gate</text>
  <text x="1652" y="296" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="12" fill="#A8C5B8">Pass or regenerate</text>
  <line x1="1596" y1="260" x2="1628" y2="260" stroke="#2E6B9E" stroke-width="2"/>
  <polygon points="1628,254 1636,260 1628,266" fill="#2E6B9E"/>

  <path d="M1730,320 L1730,400 L1300,400 L1300,320" fill="none" stroke="#E85D04" stroke-width="2" stroke-dasharray="6 4"/>
  <text x="1340" y="390" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="14" fill="#E85D04" font-weight="700">REJECT -&gt; regenerate thumbnails / metadata</text>

  <rect x="536" y="460" width="240" height="110" rx="8" fill="#FFFFFF" stroke="#0B1F33" stroke-width="2"/>
  <text x="556" y="500" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="12" fill="#0B1F33" font-weight="700">STAGE 9</text>
  <text x="556" y="530" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="18" fill="#0B1F33" font-weight="600">Dashboard</text>
  <text x="556" y="552" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="13" fill="#5A6A7A">Preview + decision log</text>

  <rect x="840" y="460" width="240" height="110" rx="8" fill="#FFFFFF" stroke="#0B1F33" stroke-width="2"/>
  <text x="860" y="500" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="12" fill="#0B1F33" font-weight="700">STAGE 10</text>
  <text x="860" y="530" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="18" fill="#0B1F33" font-weight="600">Schedule / Publish</text>
  <text x="860" y="552" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="13" fill="#5A6A7A">Platform APIs</text>

  <rect x="1144" y="460" width="240" height="110" rx="8" fill="#FFFFFF" stroke="#0B1F33" stroke-width="2" stroke-dasharray="5 3"/>
  <text x="1164" y="500" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="12" fill="#0B1F33" font-weight="700">STAGE 11 - STRETCH</text>
  <text x="1164" y="530" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="18" fill="#0B1F33" font-weight="600">Feedback Loop</text>
  <text x="1164" y="552" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="13" fill="#5A6A7A">Performance -&gt; DNA</text>

  <line x1="1730" y1="310" x2="1730" y2="515" stroke="#2E6B9E" stroke-width="2"/>
  <line x1="1730" y1="515" x2="1384" y2="515" stroke="#2E6B9E" stroke-width="2"/>
  <line x1="776" y1="515" x2="832" y2="515" stroke="#2E6B9E" stroke-width="2"/>
  <line x1="1080" y1="515" x2="1136" y2="515" stroke="#2E6B9E" stroke-width="2"/>

  <rect x="96" y="640" width="1728" height="140" rx="10" fill="#0B1F33"/>
  <text x="128" y="690" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="14" fill="#FF5A36" font-weight="700" letter-spacing="2">ORCHESTRATOR</text>
  <text x="128" y="730" font-family="Georgia, 'Times New Roman', serif" font-size="28" fill="#FFFFFF">Single agent / state machine -- calls each stage as a tool</text>
  <text x="128" y="770" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="16" fill="#A8B0BC">Logs every decision with a short rationale, including reject/regenerate cycles -- best demo moment</text>

  <rect x="96" y="820" width="520" height="80" rx="8" fill="#FFFFFF" stroke="#C5D0DB"/>
  <text x="120" y="855" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="14" fill="#5A6A7A">INPUT</text>
  <text x="120" y="880" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="18" fill="#0B1F33" font-weight="600">Creator connects channel / catalog sample</text>

  <rect x="648" y="820" width="520" height="80" rx="8" fill="#FFFFFF" stroke="#C5D0DB"/>
  <text x="672" y="855" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="14" fill="#5A6A7A">OUTPUT</text>
  <text x="672" y="880" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="18" fill="#0B1F33" font-weight="600">Scheduled post + full decision audit trail</text>

  <rect x="1200" y="820" width="624" height="80" rx="8" fill="#FFFFFF" stroke="#00A86B" stroke-width="2"/>
  <text x="1224" y="855" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="14" fill="#00A86B">DIFFERENTIATOR</text>
  <text x="1224" y="880" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="18" fill="#0B1F33" font-weight="600">Style-fit gate -- judgment, not a fixed script</text>
"""
        + FOOTER.format(
            y=980,
            label="Architecture poster 02  |  End-to-end pipeline  |  aftertake / Creator Twin",
        )
    )


def poster_03() -> str:
    return wrap(
        COMMON_DEFS
        + """
  <text x="96" y="88" font-family="Georgia, 'Times New Roman', serif" font-size="48" font-weight="700" fill="#0B1F33">The Decision Layer</text>
  <text x="96" y="128" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="20" fill="#5A6A7A">Why Creator Twin is not another topic -&gt; video -&gt; auto-post tool</text>

  <rect x="96" y="180" width="800" height="720" rx="12" fill="#FFFFFF" stroke="#C5D0DB" stroke-width="1.5"/>
  <rect x="96" y="180" width="800" height="64" rx="12" fill="#8A96A3"/>
  <rect x="96" y="220" width="800" height="24" fill="#8A96A3"/>
  <text x="128" y="222" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="22" fill="#FFFFFF" font-weight="700">Comparable tools today</text>

  <rect x="140" y="280" width="700" height="70" rx="8" fill="#F2F5F8"/>
  <text x="490" y="324" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="20" fill="#5A6A7A" font-weight="600">Human picks a topic</text>
  <text x="490" y="390" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="28" fill="#8A96A3">v</text>
  <rect x="140" y="410" width="700" height="70" rx="8" fill="#F2F5F8"/>
  <text x="490" y="454" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="20" fill="#5A6A7A" font-weight="600">Generic script + video generation</text>
  <text x="490" y="520" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="28" fill="#8A96A3">v</text>
  <rect x="140" y="540" width="700" height="70" rx="8" fill="#F2F5F8"/>
  <text x="490" y="584" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="20" fill="#5A6A7A" font-weight="600">Thumbnail / metadata templates</text>
  <text x="490" y="650" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="28" fill="#8A96A3">v</text>
  <rect x="140" y="670" width="700" height="70" rx="8" fill="#F2F5F8"/>
  <text x="490" y="714" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="20" fill="#5A6A7A" font-weight="600">Auto-publish - stop</text>
  <text x="490" y="800" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="16" fill="#8A96A3">Automates making content -- no personalization, no judgment, no loop</text>

  <rect x="1024" y="180" width="800" height="720" rx="12" fill="#0B1F33"/>
  <rect x="1024" y="180" width="800" height="64" rx="12" fill="#FF5A36"/>
  <rect x="1024" y="220" width="800" height="24" fill="#FF5A36"/>
  <text x="1056" y="222" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="22" fill="#FFFFFF" font-weight="700">Creator Twin</text>

  <rect x="1068" y="280" width="700" height="70" rx="8" fill="#163A5F"/>
  <text x="1418" y="324" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="20" fill="#FFFFFF" font-weight="600">Learn Creator DNA from their catalog</text>
  <text x="1418" y="390" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="28" fill="#FF5A36">v</text>
  <rect x="1068" y="410" width="700" height="70" rx="8" fill="#163A5F" stroke="#FF5A36" stroke-width="2"/>
  <text x="1418" y="454" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="20" fill="#FFFFFF" font-weight="600">Decide what to make next (fit + rationale)</text>
  <text x="1418" y="520" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="28" fill="#FF5A36">v</text>
  <rect x="1068" y="540" width="700" height="70" rx="8" fill="#163A5F"/>
  <text x="1418" y="584" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="20" fill="#FFFFFF" font-weight="600">Generate in their established style</text>
  <text x="1418" y="650" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="28" fill="#FF5A36">v</text>
  <rect x="1068" y="670" width="700" height="70" rx="8" fill="#00A86B"/>
  <text x="1418" y="714" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="20" fill="#FFFFFF" font-weight="700">Style-fit gate - reject / regenerate</text>
  <text x="1418" y="800" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="16" fill="#A8C5B8">Automates deciding what to make -- and whether it is actually you</text>

  <circle cx="960" cy="540" r="36" fill="#FFFFFF" stroke="#0B1F33" stroke-width="3"/>
  <text x="960" y="548" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="20" font-weight="700" fill="#0B1F33">VS</text>
"""
        + FOOTER.format(
            y=980,
            label="Architecture poster 03  |  Competitive differentiation  |  aftertake / Creator Twin",
        )
    )


def poster_04() -> str:
    return wrap(
        COMMON_DEFS
        + """
  <text x="96" y="88" font-family="Georgia, 'Times New Roman', serif" font-size="48" font-weight="700" fill="#0B1F33">Tech Stack Architecture</text>
  <text x="96" y="128" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="20" fill="#5A6A7A">Suggested layers for hackathon MVP -- glue light, agents heavy</text>

  <rect x="96" y="180" width="1728" height="100" rx="10" fill="#FFFFFF" stroke="#C5D0DB" stroke-width="1.5"/>
  <rect x="96" y="180" width="12" height="100" fill="#FF5A36"/>
  <text x="140" y="225" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="14" fill="#FF5A36" font-weight="700" letter-spacing="2">PRESENTATION</text>
  <text x="140" y="258" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="22" fill="#0B1F33" font-weight="600">Next.js dashboard -- opportunity, preview, thumbnails, decision log, schedule</text>

  <rect x="96" y="300" width="1728" height="100" rx="10" fill="#FFFFFF" stroke="#C5D0DB" stroke-width="1.5"/>
  <rect x="96" y="300" width="12" height="100" fill="#2E6B9E"/>
  <text x="140" y="345" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="14" fill="#2E6B9E" font-weight="700" letter-spacing="2">API / GLUE</text>
  <text x="140" y="378" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="22" fill="#0B1F33" font-weight="600">Python FastAPI -- stage endpoints, orchestrator runner, SQLite / local disk</text>

  <rect x="96" y="420" width="1728" height="220" rx="10" fill="#0B1F33"/>
  <text x="140" y="465" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="14" fill="#FF5A36" font-weight="700" letter-spacing="2">DECISION + AGENT LAYER</text>
  <text x="140" y="500" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="22" fill="#FFFFFF" font-weight="600">Claude API (tool use / function calling) as the orchestrator brain</text>

  <rect x="140" y="530" width="240" height="70" rx="8" fill="#163A5F"/>
  <text x="260" y="572" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="16" fill="#FFFFFF">Creator DNA</text>
  <rect x="400" y="530" width="240" height="70" rx="8" fill="#163A5F"/>
  <text x="520" y="572" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="16" fill="#FFFFFF">Opportunity</text>
  <rect x="660" y="530" width="240" height="70" rx="8" fill="#163A5F"/>
  <text x="780" y="572" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="16" fill="#FFFFFF">Script</text>
  <rect x="920" y="530" width="240" height="70" rx="8" fill="#163A5F"/>
  <text x="1040" y="572" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="16" fill="#FFFFFF">Thumbnail + SEO</text>
  <rect x="1180" y="530" width="280" height="70" rx="8" fill="#00A86B"/>
  <text x="1320" y="572" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="16" fill="#FFFFFF" font-weight="700">Style-Fit Scorer</text>
  <rect x="1480" y="530" width="300" height="70" rx="8" fill="#163A5F" stroke="#FF5A36" stroke-width="2"/>
  <text x="1630" y="572" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="16" fill="#FFFFFF">Decision Logger</text>

  <rect x="96" y="660" width="1728" height="160" rx="10" fill="#FFFFFF" stroke="#C5D0DB" stroke-width="1.5"/>
  <rect x="96" y="660" width="12" height="160" fill="#00A86B"/>
  <text x="140" y="705" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="14" fill="#00A86B" font-weight="700" letter-spacing="2">EXECUTION LAYER - REUSE EXISTING</text>

  <rect x="140" y="730" width="300" height="60" rx="8" fill="#F2F5F8" stroke="#C5D0DB"/>
  <text x="290" y="766" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="15" fill="#0B1F33" font-weight="600">HyperFrames - video</text>
  <rect x="460" y="730" width="300" height="60" rx="8" fill="#F2F5F8" stroke="#C5D0DB"/>
  <text x="610" y="766" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="15" fill="#0B1F33" font-weight="600">faster-whisper - captions</text>
  <rect x="780" y="730" width="300" height="60" rx="8" fill="#F2F5F8" stroke="#C5D0DB"/>
  <text x="930" y="766" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="15" fill="#0B1F33" font-weight="600">TTS - ElevenLabs / edge</text>
  <rect x="1100" y="730" width="300" height="60" rx="8" fill="#F2F5F8" stroke="#C5D0DB"/>
  <text x="1250" y="766" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="15" fill="#0B1F33" font-weight="600">SVG to PNG - resvg</text>
  <rect x="1420" y="730" width="360" height="60" rx="8" fill="#F2F5F8" stroke="#C5D0DB"/>
  <text x="1600" y="766" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="15" fill="#0B1F33" font-weight="600">YouTube Data API - publish</text>

  <rect x="96" y="860" width="1728" height="80" rx="8" fill="#FFFFFF" stroke="#FF5A36" stroke-width="1.5"/>
  <text x="128" y="910" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="18" fill="#0B1F33"><tspan font-weight="700" fill="#FF5A36">Principle: </tspan>Reuse execution mechanics (HyperFrames, SVG to PNG). Own the decision layer (DNA, opportunity, style-fit, feedback).</text>
"""
        + FOOTER.format(
            y=1020,
            label="Architecture poster 04  |  Tech stack  |  aftertake / Creator Twin",
        )
    )


def poster_05() -> str:
    return wrap(
        COMMON_DEFS
        + """
  <text x="96" y="88" font-family="Georgia, 'Times New Roman', serif" font-size="48" font-weight="700" fill="#0B1F33">Orchestrator and Feedback Loop</text>
  <text x="96" y="128" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="20" fill="#5A6A7A">State machine with a quality gate -- and a stretch loop that makes it self-improving</text>

  <rect x="720" y="180" width="480" height="100" rx="12" fill="#0B1F33"/>
  <text x="960" y="225" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="14" fill="#FF5A36" font-weight="700" letter-spacing="2">ORCHESTRATOR</text>
  <text x="960" y="255" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="22" fill="#FFFFFF" font-weight="600">Calls stages | logs rationale</text>

  <rect x="160" y="360" width="200" height="90" rx="8" fill="#FFFFFF" stroke="#2E6B9E" stroke-width="2"/>
  <text x="260" y="400" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="13" fill="#2E6B9E" font-weight="700">STAGES 1-2</text>
  <text x="260" y="428" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="16" fill="#0B1F33" font-weight="600">DNA + Opportunity</text>

  <rect x="420" y="360" width="200" height="90" rx="8" fill="#FFFFFF" stroke="#2E6B9E" stroke-width="2"/>
  <text x="520" y="400" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="13" fill="#2E6B9E" font-weight="700">STAGES 3-5</text>
  <text x="520" y="428" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="16" fill="#0B1F33" font-weight="600">Script to Video</text>

  <rect x="680" y="360" width="200" height="90" rx="8" fill="#FFFFFF" stroke="#2E6B9E" stroke-width="2"/>
  <text x="780" y="400" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="13" fill="#2E6B9E" font-weight="700">STAGES 6-7</text>
  <text x="780" y="428" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="16" fill="#0B1F33" font-weight="600">Thumb + Meta</text>

  <rect x="960" y="350" width="240" height="110" rx="10" fill="#0B1F33" stroke="#00A86B" stroke-width="3"/>
  <text x="1080" y="395" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="13" fill="#00A86B" font-weight="700">STAGE 8 - GATE</text>
  <text x="1080" y="425" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="20" fill="#FFFFFF" font-weight="700">Style-Fit Scorer</text>
  <text x="1080" y="450" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="13" fill="#A8C5B8">threshold check</text>

  <rect x="1280" y="360" width="200" height="90" rx="8" fill="#FFFFFF" stroke="#0B1F33" stroke-width="2"/>
  <text x="1380" y="400" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="13" fill="#0B1F33" font-weight="700">STAGES 9-10</text>
  <text x="1380" y="428" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="16" fill="#0B1F33" font-weight="600">Dash + Publish</text>

  <rect x="1540" y="360" width="220" height="90" rx="8" fill="#FFFFFF" stroke="#0B1F33" stroke-width="2" stroke-dasharray="5 3"/>
  <text x="1650" y="400" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="13" fill="#0B1F33" font-weight="700">STAGE 11</text>
  <text x="1650" y="428" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="16" fill="#0B1F33" font-weight="600">Feedback (stretch)</text>

  <line x1="360" y1="405" x2="412" y2="405" stroke="#2E6B9E" stroke-width="2"/>
  <line x1="620" y1="405" x2="672" y2="405" stroke="#2E6B9E" stroke-width="2"/>
  <line x1="880" y1="405" x2="952" y2="405" stroke="#2E6B9E" stroke-width="2"/>
  <line x1="1200" y1="405" x2="1272" y2="405" stroke="#00A86B" stroke-width="2"/>
  <line x1="1480" y1="405" x2="1532" y2="405" stroke="#2E6B9E" stroke-width="2"/>
  <text x="1235" y="335" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="13" fill="#00A86B" font-weight="700">PASS -&gt;</text>

  <path d="M1080,460 L1080,560 L780,560 L780,460" fill="none" stroke="#E85D04" stroke-width="2.5" stroke-dasharray="8 5"/>
  <rect x="820" y="530" width="280" height="40" rx="6" fill="#FFF4ED" stroke="#E85D04"/>
  <text x="960" y="556" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="14" fill="#E85D04" font-weight="700">REJECT -&gt; regenerate 6-7</text>

  <rect x="160" y="620" width="780" height="280" rx="12" fill="#FFFFFF" stroke="#C5D0DB"/>
  <text x="192" y="670" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="14" fill="#FF5A36" font-weight="700" letter-spacing="2">DECISION LOG - DEMO MOMENT</text>
  <text x="192" y="720" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="16" fill="#0B1F33">* Opportunity picked because DNA trait X correlated with CTR</text>
  <text x="192" y="760" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="16" fill="#0B1F33">* Thumbnail B chosen -- matches learned contrast / face crop</text>
  <text x="192" y="800" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="16" fill="#0B1F33">* Style-fit: 0.62 -&gt; REJECTED (title formula mismatch)</text>
  <text x="192" y="840" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="16" fill="#0B1F33">* Regenerated title, re-scored 0.84 -&gt; PASSED</text>
  <text x="192" y="880" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="16" fill="#5A6A7A">Proof of judgment -- not a fixed script</text>

  <rect x="980" y="620" width="780" height="280" rx="12" fill="#0B1F33"/>
  <text x="1012" y="670" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="14" fill="#00A86B" font-weight="700" letter-spacing="2">FEEDBACK LOOP - STRETCH</text>
  <text x="1012" y="730" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="17" fill="#FFFFFF">1. Pull real post performance after publish</text>
  <text x="1012" y="775" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="17" fill="#FFFFFF">2. Compare vs Opportunity Agent predicted fit</text>
  <text x="1012" y="820" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="17" fill="#FFFFFF">3. Feed deltas back into next Creator DNA pass</text>
  <text x="1012" y="865" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="17" fill="#A8C5B8">Recommendations get sharper over time</text>
"""
        + FOOTER.format(
            y=980,
            label="Architecture poster 05  |  Orchestrator + gate + feedback  |  aftertake / Creator Twin",
        )
    )


def poster_06() -> str:
    steps = [
        (280, "#00A86B", "1", "Seed catalog (5-10 videos) -> Creator DNA profile"),
        (340, "#00A86B", "2", "Opportunity agent: next topic + DNA-tied rationale"),
        (400, "#00A86B", "3", "Script agent writes in learned voice"),
        (460, "#00A86B", "4", "HyperFrames renders one short video (simple template OK)"),
        (520, "#00A86B", "5", "Auto-captions burned in"),
        (580, "#00A86B", "6", "2-3 SVG thumbnails -> agent picks via thumbnail_style"),
        (640, "#00A86B", "7", "Title / description / tags via title_formula"),
        (700, "#FF5A36", "8", "Style-fit scorer -- live reject -> regenerate (strongest demo beat)"),
        (760, "#00A86B", "9", "Dashboard with full decision log"),
        (820, "#00A86B", "10", "One real platform post (YouTube) -- others can be mocked"),
    ]
    step_svg = []
    for y, color, n, text in steps:
        step_svg.append(
            f"""
    <circle cx="160" cy="{y}" r="18" fill="{color}"/>
    <text x="160" y="{y+6}" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="14" fill="#FFFFFF" font-weight="700">{n}</text>
    <text x="200" y="{y+6}" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="17" fill="#0B1F33">{text}</text>"""
        )

    return wrap(
        COMMON_DEFS
        + """
  <text x="96" y="88" font-family="Georgia, 'Times New Roman', serif" font-size="48" font-weight="700" fill="#0B1F33">Hackathon MVP Path</text>
  <text x="96" y="128" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="20" fill="#5A6A7A">Cut ruthlessly to one linear happy path -- polish only after it works end-to-end once</text>

  <rect x="96" y="170" width="1100" height="740" rx="12" fill="#FFFFFF" stroke="#C5D0DB"/>
  <rect x="96" y="170" width="1100" height="56" rx="12" fill="#00A86B"/>
  <rect x="96" y="202" width="1100" height="24" fill="#00A86B"/>
  <text x="128" y="210" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="20" fill="#FFFFFF" font-weight="700">MUST SHIP - 10-step happy path</text>
"""
        + "\n".join(step_svg)
        + """
  <rect x="1240" y="170" width="584" height="340" rx="12" fill="#FFFFFF" stroke="#C5D0DB"/>
  <rect x="1240" y="170" width="584" height="56" rx="12" fill="#8A96A3"/>
  <rect x="1240" y="202" width="584" height="24" fill="#8A96A3"/>
  <text x="1272" y="210" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="18" fill="#FFFFFF" font-weight="700">STRETCH - only after E2E works</text>
  <text x="1272" y="280" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="16" fill="#5A6A7A">* Real feedback loop into DNA</text>
  <text x="1272" y="320" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="16" fill="#5A6A7A">* Multi-platform scheduling</text>
  <text x="1272" y="360" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="16" fill="#5A6A7A">* Analytics dashboard</text>
  <text x="1272" y="400" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="16" fill="#5A6A7A">* Comment moderation</text>

  <rect x="1240" y="540" width="584" height="370" rx="12" fill="#0B1F33"/>
  <text x="1272" y="590" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="14" fill="#FF5A36" font-weight="700" letter-spacing="2">TEAM SPLIT</text>
  <text x="1272" y="640" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="16" fill="#FFFFFF"><tspan fill="#FF5A36" font-weight="700">A</tspan>  Video pipeline (script + HyperFrames + TTS)</text>
  <text x="1272" y="685" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="16" fill="#FFFFFF"><tspan fill="#FF5A36" font-weight="700">B</tspan>  Visuals (SVG thumbs + metadata/SEO)</text>
  <text x="1272" y="730" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="16" fill="#FFFFFF"><tspan fill="#FF5A36" font-weight="700">C</tspan>  Orchestrator + decision logging</text>
  <text x="1272" y="775" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="16" fill="#FFFFFF"><tspan fill="#FF5A36" font-weight="700">D</tspan>  Dashboard + publish</text>
  <text x="1272" y="840" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="14" fill="#A8B0BC">Solo/2: combine A+C and B+D</text>
"""
        + FOOTER.format(
            y=980,
            label="Architecture poster 06  |  MVP scope  |  aftertake / Creator Twin",
        )
    )


POSTERS = {
    "01-system-overview.svg": poster_01,
    "02-end-to-end-pipeline.svg": poster_02,
    "03-decision-layer.svg": poster_03,
    "04-tech-stack.svg": poster_04,
    "05-orchestrator-feedback.svg": poster_05,
    "06-mvp-path.svg": poster_06,
}


def main() -> None:
    for name, fn in POSTERS.items():
        path = DIR / name
        path.write_text(fn(), encoding="utf-8", newline="\n")
        print(f"wrote {name}")


if __name__ == "__main__":
    main()
