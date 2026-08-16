---
version: alpha
name: Aftertake Cinema Ã¢â‚¬â€ Frame
description: >
  Deep navy cinema canvas for Aftertake product film. Warm off-white ink, coral
  accent, teal system/pass. Montserrat display + Montserrat body + JetBrains Mono chrome.
  Video-scale type and dense atmosphere (grain, ghost brand, grid, radials).
unit: the frame Ã¢â‚¬â€ 1920Ãƒâ€”1080
principle: atoms are sacred Ã‚Â· composition is free Ã‚Â· density over empty slides

colors:
  canvas: "#0B1220"
  bg: "#0B1220"
  ink: "#F3EEE6"
  text: "#F3EEE6"
  text-muted: "#A8A296"
  accent: "#FF4D2E"
  primary: "#FF4D2E"
  teal: "#2EC4B6"
  positive: "#2EC4B6"
  negative: "#FF7A45"
  panel: "#121A2B"
  panel-elev: "#182234"
  border: "rgba(243, 238, 230, 0.14)"
  grain: "rgba(243, 238, 230, 0.04)"

typography:
  display: { fontFamily: "Montserrat", weight: 700 }
  body: { fontFamily: "Montserrat", weight: 400 }
  ui: { fontFamily: "Montserrat", weight: 500 }
  mono: { fontFamily: "JetBrains Mono", weight: 500 }

spacing:
  pad-x: "6cqw"
  pad-y-top: "5cqw"

components:
  panel:
    backgroundColor: "{colors.panel}"
    border: "2px solid {colors.border}"
    rounded: "18px"
  pill:
    backgroundColor: "{colors.accent}"
    color: "{colors.ink}"
    rounded: "100px"

do:
  - Keep navy canvas across every scene
  - Use coral at full saturation on focal hits
  - Layer grain + ghost AFTERTAKE + grid on every frame
  - Video-scale headlines 64Ã¢â‚¬â€œ120px
don't:
  - Flat single-color empty slides
  - Dim full-bleed architecture posters as backgrounds
  - Purple neon AI glow
  - Cream/terracotta default look
  - Web-thin 1px borders as the only structure
---

# Aftertake Cinema

Product-film design system. Atmosphere is mandatory: each scene carries
background treatment, midground product UI, and foreground accents.
