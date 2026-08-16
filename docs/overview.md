# Creator Twin — A Personalized, Self-Improving Content Decision Engine

## 1. The Pitch (30-second version)

**Creator Twin** doesn't generate generic AI content — it learns a specific creator's actual voice, thumbnail style, and title formula from their existing catalog and real performance data, then acts as their editorial brain: deciding **what to make next** (not just "how"), generating it in their established style, and gating every asset through a style-fit check before it can ship. After publishing, it closes the loop — real performance feeds back into the profile, so recommendations get sharper over time.

## 1a. Why not just "topic in, video out, auto-posted"? (repositioning note)

We researched this space before locking the idea (see section 7 for the full list). The "generate a video from a topic and auto-publish it" pattern is **already solved and public** — multiple open-source repos do this end to end today, including ones already built on Claude Code + HyperFrames. Building that exact loop risks looking like a re-skin of existing work.

What none of those repos do:
- Learn a **specific creator's** established voice/style from their own catalog (they generate generic content from a topic)
- Decide **what to make next** based on the creator's own performance data (they assume the human already picked the topic)
- **Close the loop** — use real post-performance to improve future decisions (they stop at "publish")

Creator Twin reuses the same execution mechanics as the original plan (HyperFrames for video, SVG→PNG for thumbnails, an orchestrator) but repositions the actual innovation around the **decision layer**, not the generation mechanics.

---

## 2. Problem

Creators lose hours per video to repetitive, non-creative work: writing/structuring the script, editing, generating thumbnail variants, writing titles/descriptions/tags, deciding when to post, and cross-posting to multiple platforms. Existing automation tools solve the *mechanics* of this — but they produce generic output and give no real judgment about whether it fits the creator's own brand, or whether it's even the right thing to make next.

---

## 3. End-to-End Flow

```
[Creator connects their channel / uploads a catalog sample]
        │
        ▼
STAGE 1 — CREATOR DNA AGENT
  Ingests past videos: titles, transcripts, thumbnails, and real
  performance (views, CTR, retention). Extracts tone, hook patterns,
  title formula, thumbnail style, and which traits correlate with
  strong vs. weak performance.
        │
        ▼
STAGE 2 — OPPORTUNITY AGENT
  Cross-references the Creator DNA against current trends in their
  niche. Recommends next-video ideas with a fit score and a rationale
  tied to the creator's own best-performing traits — not generic
  trend-chasing.
        │
        ▼
STAGE 3 — SCRIPT AGENT
  Writes the script (hook, scenes, voiceover lines) in the creator's
  learned voice/pacing, for the chosen opportunity.
        │
        ▼
STAGE 4 — VIDEO RENDER (HyperFrames)
  Agent converts each scene into HyperFrames HTML/CSS/JS. TTS generates
  voiceover audio. `npx hyperframes render` produces the MP4,
  frame-by-frame, deterministic.
        │
        ▼
STAGE 5 — CAPTIONS & POLISH
  Whisper (faster-whisper) transcribes the rendered audio for sync
  accuracy. Captions burned in via HyperFrames caption blocks or ffmpeg.
        │
        ▼
STAGE 6 — THUMBNAIL AGENT (SVG → PNG)
  LLM writes 2-3 SVG thumbnail layouts following the creator's learned
  thumbnail_style. Rendered to PNG via cairosvg/resvg. A second LLM
  pass picks the strongest variant.
        │
        ▼
STAGE 7 — METADATA / SEO AGENT
  Title/description/tags generated following the creator's own
  title_formula, not generic SEO templates.
        │
        ▼
STAGE 8 — STYLE-FIT SCORER (quality gate)
  A critic agent checks the chosen thumbnail + metadata against the
  Creator DNA. Below threshold → REJECTED, triggers a regenerate pass.
  This is the piece none of the comparable repos have.
        │
        ▼
STAGE 9 — DASHBOARD
  Shows: recommended opportunity + rationale, video preview, thumbnail
  options, metadata, connected accounts, schedule picker, and the full
  decision log (including any reject → regenerate cycles).
        │
        ▼
STAGE 10 — SCHEDULE / PUBLISH
  Queues the post; pushes to 1-2 real connected platform APIs
  (others can be stubbed/mocked for the demo).
        │
        ▼
STAGE 11 — FEEDBACK LOOP (stretch)
  Pulls real post performance after publish, compares to the
  Opportunity Agent's predicted fit, and feeds it back into the next
  Creator DNA pass so future recommendations improve.
```

The **orchestrator** is a single agent/state machine that calls each stage as a tool, makes the decision-point calls, and logs each decision with a short rationale — including any reject → regenerate cycles from the style-fit gate. This log is your best demo moment: it's proof the system has actual judgment, not just a fixed script.

---

## 4. Suggested Stack

| Layer | Choice | Why |
|---|---|---|
| Orchestrator / agents | Claude API (tool use / function calling) | Central decision-making layer |
| Video rendering | HyperFrames (`hyperframes/hyperframes`) | Agent-native HTML→video, deterministic |
| Transcription | faster-whisper | Fast, local, accurate captions |
| TTS | Any (ElevenLabs / edge-tts / local) | Voiceover for script |
| Thumbnails | SVG generation + resvg/sharp/cairosvg | Fast, deterministic, LLM-writable |
| Backend | Python (FastAPI) | Glue code, easiest for AI/video libs |
| Frontend/dashboard | Next.js (or Streamlit/Gradio if time-tight) | Fast to build, good demo polish |
| Storage | SQLite / local disk | No infra overhead for a hackathon |
| Scheduling/posting | Direct platform APIs (YouTube Data API easiest) | Real working demo without OAuth sprawl |

---

## 5. Repos/Projects to Fork or Reference (don't build from scratch)

**Execution-layer building blocks (safe to reuse — nobody will fault you for this):**
- **`hyperframes/hyperframes`** — core rendering engine, CLI, templates, agent skills
- **`coleam00/hyperframes-ai-video-generation`** — reference pattern for URL/topic → script → video agent workflow
- **`elixiumlabs/hyperframes-videos`** — additional HyperFrames packages/examples (studio, player, shader transitions)
- **`faster-whisper`** — transcription
- **`unitary/toxic-bert`** (HuggingFace) — if you keep a comment-moderation stretch goal

**Comparable/competing projects — worth knowing so you don't accidentally rebuild them, and worth citing in your pitch to show you did the research:**
- **`hassanrauf1/Generate-AI-Viral-Videos-with-Seedance...`** — n8n agent, GPT-4 + Seedance + Blotato, full script→video→multi-platform-upload. One-shot, generic, no personalization or feedback loop.
- **`khaoss85/youtube-autopilot`** — trend detection → multi-agent editorial → Veo video gen → scheduled YouTube publishing. Closest in spirit but still topic-in/generic-out, no creator-specific learning.
- **`anthonyonazure/social-agent`** — state-machine content agent (Postgres + n8n + Next.js dashboard), human-in-the-loop → autonomous. Good dashboard/audit-log pattern reference, but no style personalization.
- **VidPipe** (`htek.dev`) — 8-agent pipeline built on HyperFrames + GitHub Copilot SDK, post-production only (drop a video, get shorts/captions/social posts). Different entry point (existing footage, not idea-to-video) but same "no personalization, no feedback loop" gap.
- **`JuneYaooo/awesome-ai-media`** — curated list of 150+ tools in this space; includes at least one repo doing idea→script→voice→visuals via a 9-stage DAG pipeline with self-evolving scoring, built on Claude Code + HyperFrames. Worth a skim before finalizing scope so you know exactly what's already out there.

**Takeaway for the pitch:** every comparable repo automates *making* content. Creator Twin automates *deciding what to make and whether it's actually you* — lead with that distinction.

---

## 6. Hackathon-Scoped MVP (what must work by deadline)

Cut ruthlessly to this linear happy path first, polish only after it works end-to-end once:

1. Sample/seed catalog in (5-10 past videos, real or realistic fake data) → Creator DNA agent produces a profile
2. Opportunity agent recommends a next topic with a rationale tied to the DNA
3. Script agent writes the script in that voice
4. Script → HyperFrames renders one short video (even a single simple template scene is fine)
5. Auto-captions burned in
6. 2-3 SVG thumbnails generated → agent picks one, following the learned thumbnail_style
7. Title/description/tags generated, following the learned title_formula
8. Style-fit scorer checks the chosen thumbnail + metadata — **show a live reject → regenerate cycle**, this is your strongest demo beat
9. Dashboard shows all of the above with a full decision log
10. One real platform connection (e.g. YouTube) with an actual (or sandbox/test) post — everything else can be a convincing mock in the UI

**Stretch, only after the above works:** real feedback loop (pull actual post performance, feed back into Creator DNA), multi-platform scheduling, analytics dashboard, comment moderation.

> A working scaffold implementing stages 1-3, 6, 7, and 8 already exists — see the accompanying `creator-twin.zip`. It includes a tested, working SVG→PNG thumbnail renderer, all five core agents, the orchestrator with the reject/regenerate loop, and a FastAPI layer to build the dashboard against.

---

## 7. Suggested Team Split (scales 1-4)

- **Person A — Video pipeline:** script agent + HyperFrames scene generation + TTS + captions
- **Person B — Visual assets:** SVG thumbnail agent + renderer + metadata/SEO agent
- **Person C — Orchestrator:** the agent/state machine tying stages together + decision logging
- **Person D — Dashboard & publishing:** frontend, account connections, scheduler, analytics stub

If solo or 2-person, cut to A+C combined and B+D combined.

---

## 8. Demo Script (for judges)

1. Type in one topic live.
2. Show the script the agent writes.
3. Show the video rendering (or a pre-rendered one if render time is long — be upfront about that).
4. Show the 3 thumbnail variants and the agent explaining why it picked one.
5. Show the metadata generated.
6. Show the dashboard with the decision log — this is the "wow, it's not just a script" moment.
7. Show (or simulate) the scheduled/published post.

---

## 9. Immediate Next Steps

1. `npx hyperframes init` a test project, get one scene rendering to MP4 — de-risk this first, it's your riskiest dependency.
2. Stand up the FastAPI skeleton with stub endpoints for each stage.
3. Get the orchestrator calling stages in order with dummy data before wiring real logic into each.
4. Build the dashboard against the stubbed API so frontend/backend can work in parallel.