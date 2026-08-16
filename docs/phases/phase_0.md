# Phase 0 — Setup & Scope Lock

---

## What Phase 0 Is and Why It Exists

Phase 0 is not setup in the technical sense. It is the decision-making phase. Every single ambiguity, every "we will figure that out later," every "it depends" that you leave unresolved here will come back as a crisis during Phase 2 or Phase 3 when you are under time pressure and cannot afford to stop and think clearly. Phase 0 exists to make every foundational decision while you are calm, fed, and not debugging anything. You produce no running code in this phase. You produce clarity, locked decisions, and a structure that every later phase plugs into without confusion.

---

## Phase 0 — Step 1: Lock the Single MVP Sentence

**What this step is:**
Before anything else, you write one sentence that describes exactly what must work by the end of the hackathon. Not a paragraph. Not a bullet list. One sentence. This sentence becomes the filter for every decision you make for the rest of the build. If a feature, a design choice, or a technical approach cannot be justified by tracing it back to this sentence, it does not belong in the build.

**The MVP Sentence:**

"A creator seeds their past content catalog, the system learns their unique voice and style from real performance data, recommends what to make next with a rationale tied to their actual best-performing content traits, generates a script and thumbnail in that learned style, scores it against their profile through a quality gate that can reject and regenerate, and presents the full decision log alongside the output before publishing."

**How to use this sentence:**
Every time you are about to build something and you are not sure if it belongs, read this sentence. If the thing you are about to build does not appear anywhere in this sentence, it goes on the cut list. Not later. Immediately.

---

## Phase 0 — Step 2: Define What Is Genuinely Novel About This Project

**What this step is:**
You need to be able to explain in two sentences what makes Creator Twin different from every other AI content tool that already exists. This is not marketing. This is a technical and product clarity exercise. If you cannot explain the differentiation, you will accidentally build the wrong thing — a generic video generator instead of a personalized editorial intelligence engine.

**The differentiation:**

Every comparable tool takes a topic as input and generates generic content as output. Creator Twin takes a specific creator's own catalog and performance history as input, learns what makes that creator distinctive and what has actually worked for them, and uses that learned profile to decide what to make next and whether what it generates actually sounds and looks like that creator — not like a generic AI output.

**The three things no comparable tool does that Creator Twin does:**
- Learns a specific creator's voice, thumbnail style, and title formula from their own catalog — not from a general model of "good content"
- Decides what to make next based on that creator's own performance data — not from a generic trending topics list
- Runs every generated asset through a style-fit quality gate that checks against the learned profile and can reject and regenerate — not just output whatever it first produces

**Why you need this written down:**
When you are building Phase 2 and you are writing prompts for the generation agents, this is what you check every prompt against. If the prompt could produce the same output for any creator, the prompt is wrong. The output must be conditioned on the specific creator's learned profile.

---

## Phase 0 — Step 3: Stack Decisions

**What this step is:**
Every technology choice for the entire project, decided once, with a reason, never revisited during the build unless something genuinely breaks. The reason for each choice is included so that when you are tired and second-guessing yourself at 2am, you can read the reason and remember why you made the choice and keep moving.

---

**Step 3a — Backend**

Choice: Python with FastAPI

Reason: Every library this project needs — the Anthropic SDK, faster-whisper, cairosvg, PIL, edge-tts, sqlite3 — is Python-native. FastAPI gives async support, automatic API documentation, and almost no boilerplate. There is no other backend choice that gives you faster access to all of these libraries simultaneously. Do not use Flask (no async), do not use Node for the backend (the AI and media libraries are not as mature), do not use Django (too much overhead for a hackathon).

---

**Step 3b — Frontend**

Choice: React with Vite

Reason: You are building a dashboard, not a marketing site. Server-side rendering adds zero value for this use case. Vite gives fast hot module replacement and zero configuration overhead. If you already have strong Next.js muscle memory and it is genuinely faster for you personally, use it — but do not pick Next.js because it sounds more professional. For this project, the frontend is a means to an end, not the showcase. Keep it simple and functional.

---

**Step 3c — Database**

Choice: SQLite

Reason: No database server to run. No connection strings to manage. No infrastructure to break during a demo. SQLite runs as a single file on your local machine. Python has a built-in sqlite3 module. You get real queryability — you can query decision logs by pipeline run ID, retrieve creator profiles by creator ID, and filter generated assets by status. JSON files on disk are acceptable only if every single data access pattern is "read the whole object, write the whole object" with no filtering. For this project, decision logs are append-only records you will query by run ID, which means SQLite is the right call.

---

**Step 3d — LLM**

Choice: Claude API, specifically claude-sonnet-4 as the default for all agents

Reason: Sonnet is fast enough for repeated testing, cost-efficient enough that you will not hit credit limits during development, and capable enough for all the structured JSON generation this project requires. You do not need Opus for any of these tasks — if an agent is producing bad output on Sonnet, the problem is the prompt, not the model. Do not switch models to fix a prompt problem. Fix the prompt. Use the Anthropic Python SDK directly with no abstraction layer — no LangChain, no LlamaIndex, no framework that adds a debugging layer between you and the API response.

---

**Step 3e — Video Rendering**

Choice: HyperFrames

Reason: This is locked by the project concept. HyperFrames is the agent-native HTML-to-video renderer the project is built around. It runs via CLI with `npx hyperframes render`. It is deterministic, meaning the same input always produces the same output — which is critical for a demo where you cannot afford unpredictable results. Node.js must be installed alongside Python because HyperFrames runs on Node. De-risk this in Phase 3 before building anything around it.

---

**Step 3f — Thumbnail Generation**

Choice: SVG generation via the LLM, rendered to PNG via cairosvg

Reason: The LLM writes SVG markup directly. cairosvg converts that SVG to a PNG in a single Python function call. No browser dependency, no Puppeteer, no headless Chrome, no Playwright. The entire pipeline from text description to rendered image is pure Python with no external services. resvg-py is the fallback if cairosvg has rendering issues with specific SVG features.

---

**Step 3g — Text to Speech**

Choice: edge-tts as primary, ElevenLabs as an upgrade only if time and credits allow

Reason: edge-tts is free, requires no API key, requires no account, and produces acceptable quality voices. ElevenLabs produces significantly better voice quality and supports voice cloning, but requires an API key, costs money per character, and is a dependency you do not need for the core demo to work. Build with edge-tts. Upgrade to ElevenLabs only after the full pipeline works end to end and you have confirmed you have credits.

---

**Step 3h — Transcription and Captions**

Choice: faster-whisper, running locally

Reason: Runs on your machine with no network call. No API key. The "small" or "base" model is fast enough and accurate enough for caption generation. The "large" model is overkill for a hackathon demo and significantly slower.

---

**Step 3i — Hosting and Deployment**

Choice: Local only. ngrok if a live URL is required.

Reason: No deployment, no Docker, no cloud infrastructure, no environment variable management across machines. You are running this on your machine during the demo. If the hackathon submission requires a live URL, use ngrok to create a tunnel to your local server. Do not spend any time on deployment infrastructure — it is zero value for the demo and high risk for eating time.

---

## Phase 0 — Step 4: Repository Structure

**What this step is:**
The exact folder and file structure of the repository, decided before any files are created. This matters because every agent, every API endpoint, every frontend component, and every rendering script needs to know where to find things and where to put things. Changing the structure midway through the build means updating import paths, file references, and API routes everywhere. Lock it now.

---

**The Complete Repository Structure:**

```
creator-twin/
│
├── backend/
│   │
│   ├── main.py
│   │     The FastAPI application entry point. Imports all routers.
│   │     Registers CORS middleware. Starts the uvicorn server.
│   │     Contains nothing except wiring — no business logic lives here.
│   │
│   ├── agents/
│   │   ├── dna_agent.py
│   │   │     Reads the creator's catalog from the database.
│   │   │     Calls the Claude API with the DNA system prompt.
│   │   │     Returns a structured CreatorDNAProfile object.
│   │   │
│   │   ├── opportunity_agent.py
│   │   │     Takes the CreatorDNAProfile as input.
│   │   │     Calls Claude to generate 3 content opportunity recommendations.
│   │   │     Each recommendation includes a rationale tied to the DNA profile.
│   │   │     Returns a list of ContentOpportunity objects.
│   │   │
│   │   ├── script_agent.py
│   │   │     Takes one ContentOpportunity and the CreatorDNAProfile as input.
│   │   │     Writes a full script in the creator's learned voice.
│   │   │     Returns a structured Script object with hook, scenes, and outro.
│   │   │
│   │   ├── thumbnail_agent.py
│   │   │     Takes the ContentOpportunity and the CreatorDNAProfile as input.
│   │   │     Writes 2-3 SVG thumbnail layouts following the learned thumbnail style.
│   │   │     Returns raw SVG markup for each variant.
│   │   │
│   │   ├── metadata_agent.py
│   │   │     Takes the script and the CreatorDNAProfile as input.
│   │   │     Generates title, description, and tags following the creator's title formula.
│   │   │     Returns a structured Metadata object.
│   │   │
│   │   └── scorer_agent.py
│   │         Takes the GeneratedAsset and the CreatorDNAProfile as input.
│   │         Scores the thumbnail and metadata against the learned profile.
│   │         Returns a QualityScore object with pass/fail and rejection reason.
│   │
│   ├── prompts/
│   │   ├── dna_system.txt
│   │   ├── opportunity_system.txt
│   │   ├── script_system.txt
│   │   ├── thumbnail_system.txt
│   │   ├── metadata_system.txt
│   │   └── scorer_system.txt
│   │         One text file per agent. The system prompt lives here, not in code.
│   │         This means you can iterate on prompts without touching Python files.
│   │         Each file is loaded at agent startup. Never hardcode a system prompt
│   │         inside an agent file.
│   │
│   ├── pipeline/
│   │   └── orchestrator.py
│   │         The single state machine that calls every stage in order.
│   │         The only file that knows the sequence of stages.
│   │         No agent file knows about any other agent — only the orchestrator does.
│   │         Writes a DecisionLogEntry at every stage.
│   │         Implements the reject → regenerate loop with a cap of 2 retries.
│   │
│   ├── rendering/
│   │   ├── video.py
│   │   │     Wraps the HyperFrames CLI call.
│   │   │     Takes a script object, converts it to HyperFrames HTML/CSS/JS.
│   │   │     Calls npx hyperframes render via subprocess.
│   │   │     Returns the path to the rendered MP4 file.
│   │   │
│   │   ├── thumbnails.py
│   │   │     Takes raw SVG markup from the thumbnail agent.
│   │   │     Calls cairosvg to convert SVG to PNG.
│   │   │     Saves the PNG to output/thumbnails/.
│   │   │     Returns the local file path.
│   │   │
│   │   └── captions.py
│   │         Takes the rendered video file path.
│   │         Runs faster-whisper transcription on the audio track.
│   │         Burns captions into the video via HyperFrames caption blocks or ffmpeg.
│   │         Returns the path to the captioned video file.
│   │
│   ├── db/
│   │   └── database.py
│   │         SQLite connection setup.
│   │         Table creation on startup (if tables do not exist).
│   │         Basic read/write functions for each data type.
│   │         No ORM — plain SQL queries are faster to write and debug for a hackathon.
│   │
│   ├── models/
│   │   └── schemas.py
│   │         All Pydantic data models for the entire project.
│   │         Every data shape defined in one place.
│   │         Both the API layer and the agent layer import from here.
│   │         Never define a data shape anywhere else.
│   │
│   ├── routers/
│   │   ├── catalog.py       (handles /catalog/* endpoints)
│   │   ├── profile.py       (handles /profile/* endpoints)
│   │   ├── pipeline.py      (handles /pipeline/* endpoints)
│   │   ├── content.py       (handles /content/* endpoints)
│   │   └── output.py        (handles /output/* file serving endpoints)
│   │
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Setup.jsx
│   │   │   │     The entry screen. Creator seeds their catalog here.
│   │   │   │     Uploads or pastes catalog data.
│   │   │   │     Triggers the DNA profile build.
│   │   │   │     Shows the resulting profile summary.
│   │   │   │
│   │   │   ├── Dashboard.jsx
│   │   │   │     The main screen. Shows everything after a pipeline run.
│   │   │   │     Opportunity recommendation with rationale.
│   │   │   │     Script preview.
│   │   │   │     Video preview (or placeholder if rendering is slow).
│   │   │   │     Thumbnail variants with the selected one highlighted.
│   │   │   │     Metadata (title, description, tags).
│   │   │   │     Full decision log panel.
│   │   │   │
│   │   │   └── Publish.jsx
│   │   │         Schedule and publish screen.
│   │   │         Platform selector.
│   │   │         Scheduled time picker.
│   │   │         Publish confirmation.
│   │   │
│   │   ├── components/
│   │   │   ├── DecisionLog.jsx
│   │   │   │     Renders the decision log as a vertical timeline.
│   │   │   │     Each entry shows: stage name, decision, rationale, status badge.
│   │   │   │     Rejected entries show in red. Regenerated entries show in amber.
│   │   │   │     Successful entries show in green.
│   │   │   │     This is the most important UI component in the entire project.
│   │   │   │
│   │   │   ├── ThumbnailPicker.jsx
│   │   │   │     Shows 2-3 thumbnail PNG options side by side.
│   │   │   │     Highlights the one the scorer selected.
│   │   │   │     Shows the scorer's reasoning below the selected one.
│   │   │   │
│   │   │   ├── VideoPreview.jsx
│   │   │   │     An HTML5 video element pointing to the /output/video/ endpoint.
│   │   │   │     Shows a loading spinner while the video is rendering.
│   │   │   │     Shows a placeholder thumbnail if video is not yet ready.
│   │   │   │
│   │   │   └── PipelineProgress.jsx
│   │   │         A step indicator showing which pipeline stage is currently running.
│   │   │         Polls /pipeline/{run_id}/status every 2 seconds during a run.
│   │   │         Each stage lights up as it completes.
│   │   │
│   │   └── api/
│   │       └── client.js
│   │             Every single fetch call to the backend lives in this one file.
│   │             No component makes a fetch call directly.
│   │             This means if the backend URL changes, you change it in one place.
│   │
│   └── package.json
│
├── output/
│   ├── videos/
│   ├── thumbnails/
│   └── captions/
│         All generated files land here in predictable subdirectories.
│         The API serves these files directly.
│         This directory is in .gitignore — generated files are never committed.
│
├── data/
│   └── seed/
│         The 8 sample catalog videos in JSON format.
│         Used for development and for the demo.
│         This is committed to the repo — it is static reference data, not output.
│
├── creator_twin.db
│         The SQLite database file.
│         Created automatically on first backend startup.
│         In .gitignore — never committed.
│
├── .env
│         API keys and configuration values.
│         Never committed. Ever.
│
├── .gitignore
│
└── README.md
      What the project does.
      How to run it.
      What is real vs mocked.
      Be honest about mocked parts — judges respect transparency.
```

---

## Phase 0 — Step 5: Environment Requirements

**What this step is:**
Every piece of software that must be installed on the machine before Phase 1 starts. This is not installation instructions — it is a checklist of what must exist and why each thing is needed.

---

**Step 5a — Python**
Version 3.11 or higher. Required for all backend logic, all agent code, all media processing. Lower versions may have compatibility issues with some libraries.

**Step 5b — Node.js**
Version 18 or higher. Required exclusively for HyperFrames. The Python backend calls the HyperFrames CLI via subprocess. Node does not run any application logic — it only powers the rendering engine.

**Step 5c — Git**
For version control. Initialize the repository before writing any files so that the initial commit captures the clean structure before any logic is added.

**Step 5d — A Python virtual environment**
Either venv or conda. All Python packages install into the virtual environment, not the global Python installation. This prevents dependency conflicts and makes the environment reproducible.

**Step 5e — API keys**
- Anthropic API key: required from day one, no agent works without it
- ElevenLabs API key: optional, only if you upgrade from edge-tts
- YouTube Data API key: required only for the publishing integration, can be stubbed until Phase 4 or later

---

## Phase 0 — Step 6: Python Dependencies

**What this step is:**
Every Python package the project needs, with a one-line explanation of exactly what it does in this project. This becomes the requirements.txt in Phase 1.

---

```
fastapi
  The web framework. Handles all HTTP routing and request/response logic.

uvicorn
  The ASGI server that runs the FastAPI application.

anthropic
  The official Anthropic Python SDK. All Claude API calls go through this.

pydantic
  Data validation and schema definition. All data shapes in schemas.py use Pydantic models.

python-dotenv
  Loads the .env file so API keys are available as environment variables.

cairosvg
  Converts SVG markup to PNG images. Used by the thumbnail rendering pipeline.

pillow
  Image processing library. Used for any image manipulation after cairosvg renders the PNG.

faster-whisper
  Local speech-to-text transcription. Generates captions from the rendered video's audio track.

edge-tts
  Text-to-speech. Converts the script voiceover text to an audio file for the video.

aiofiles
  Async file I/O. Used by FastAPI to serve the generated video and thumbnail files.

httpx
  Async HTTP client. Used for any outbound API calls (YouTube publishing, etc.)
```

---

## Phase 0 — Step 7: The .env File Structure

**What this step is:**
Every environment variable the project uses, defined as named slots, with an explanation of what each one is for. The actual values are filled in as you obtain them. The slots are defined now so nothing is forgotten.

---

```
ANTHROPIC_API_KEY
  Your Anthropic API key. Required from Phase 2 onward.
  Get this from console.anthropic.com before Phase 2 begins.

ELEVENLABS_API_KEY
  Your ElevenLabs API key. Optional. Leave blank if using edge-tts.
  Only needed if you upgrade TTS quality after the core pipeline works.

YOUTUBE_API_KEY
  Your YouTube Data API v3 key. Required only for real publishing.
  Can be left blank until Phase 4. The publishing endpoint can be stubbed without it.

YOUTUBE_CLIENT_ID
  OAuth 2.0 client ID for YouTube. Required if the YouTube integration uses OAuth.
  Can be left blank until Phase 4.

YOUTUBE_CLIENT_SECRET
  OAuth 2.0 client secret for YouTube. Same as above.

DATABASE_PATH
  The file path to the SQLite database.
  Default value: ./creator_twin.db

OUTPUT_DIR
  The directory where all generated files (videos, thumbnails, captions) are saved.
  Default value: ./output

CORS_ORIGINS
  Comma-separated list of allowed frontend origins for CORS.
  Default value: http://localhost:5173 (Vite's default dev port)
```

---

## Phase 0 — Step 8: The .gitignore Contents

**What this step is:**
Everything that must never be committed to the repository. Defined once here so nothing is accidentally pushed.

---

```
Category: Secrets
  .env
  Any file ending in .env (e.g. .env.local, .env.production)

Category: Generated output
  output/
  *.mp4
  *.png (in the output directory — seed thumbnail descriptions are text, not image files)
  *.wav
  *.mp3

Category: Database
  creator_twin.db
  *.db

Category: Python environment
  __pycache__/
  *.pyc
  *.pyo
  .venv/
  venv/
  *.egg-info/

Category: Node
  node_modules/
  .next/
  dist/

Category: OS files
  .DS_Store
  Thumbs.db
```

---

## Phase 0 — Step 9: All Data Schemas

**What this step is:**
Every data object that moves through the system, defined in plain language before any code is written. These are the contracts every part of the system agrees on. Every agent, every API endpoint, and every frontend component depends on these shapes. They are defined here, in full, so they are never ambiguous.

---

### Schema 1 — Source Video

**What it represents:** One past video from the creator's catalog. This is the raw input to the DNA agent.

**Who creates it:** The creator, by uploading or pasting their catalog data, or by it being loaded from the seed data file.

**Who reads it:** The DNA agent.

**Fields:**

```
id
  Type: string
  What it is: A unique identifier for this catalog entry.
  Example: "sv_001"

title
  Type: string
  What it is: The video title exactly as it was published.
  Example: "I Used Notion for 30 Days — Here's What Actually Happened"

description
  Type: string
  What it is: The full video description as published. Can be empty string if unavailable.

transcript
  Type: string
  What it is: The full spoken transcript of the video. 
  Important note: This can be auto-generated by faster-whisper if you have the video file,
  or written manually for seed data. It does not need to be perfect — it needs to be 
  representative enough for the DNA agent to learn tone and phrasing patterns.

duration_seconds
  Type: integer
  What it is: The length of the video in seconds.
  Example: 487 (for an 8 minute 7 second video)

published_at
  Type: date string in ISO format (YYYY-MM-DD)
  What it is: When the video was published.
  Example: "2024-03-15"

platform
  Type: string
  What it is: Which platform this video lives on.
  Allowed values: "youtube", "tiktok", "instagram", "linkedin"
  Example: "youtube"

performance
  Type: object containing the following fields:
  
    views: integer — total view count
    likes: integer — total like count
    comments: integer — total comment count
    shares: integer — total share count (null if platform does not expose this)
    ctr: float — click-through rate as a percentage, 0.0 to 100.0
               (null if unavailable — null means unknown, not zero)
    avg_retention: float — average percentage of the video that viewers watched,
                           0.0 to 100.0
    watch_time_hours: float — total accumulated watch time in hours

thumbnail
  Type: object containing the following fields:
  
    url: string — URL or local file path to the thumbnail image
                  (for seed data, this can be a placeholder URL or left as an empty string)
    description: string — A plain English description of what the thumbnail shows.
                          This is critical. It is how the DNA agent learns visual style
                          without doing image analysis.
                          Example: "Orange background. Creator standing center frame 
                          looking directly at camera with surprised expression. Bold white 
                          text in top left corner reading '30 DAYS'. No logo visible. 
                          Creator is pointing at a laptop screen on their right."

tags
  Type: list of strings
  What it is: The tags or keywords as published with the video.
  Example: ["notion", "productivity", "30 day challenge", "organization"]

category
  Type: string
  What it is: The content category as classified by the platform or the creator.
  Example: "Science & Technology"
```

---

### Schema 2 — Creator DNA Profile

**What it represents:** The learned style and performance profile of a specific creator. This is what the DNA agent produces. It is the single most important object in the entire system — every generation agent conditions on it, every scored asset is evaluated against it.

**Who creates it:** The DNA agent, from a batch of Source Video objects.

**Who reads it:** The opportunity agent, the script agent, the thumbnail agent, the metadata agent, and the scorer agent. Every single agent that generates anything reads this object.

**Who updates it:** The feedback loop agent (stretch goal) after real post-performance data is available.

**Fields:**

```
creator_id
  Type: string
  What it is: Unique identifier for this creator.
  Example: "creator_001"

created_at
  Type: timestamp
  What it is: When this profile was first generated.

updated_at
  Type: timestamp
  What it is: When this profile was last updated (by the feedback loop, if implemented).

source_video_count
  Type: integer
  What it is: How many Source Video objects this profile was built from.
  Example: 8

voice
  Type: object containing the following fields:
  
    tone: string
      What it is: A description of the creator's overall communication style.
      Example: "Conversational and direct. Never formal or academic. 
                Speaks like explaining something to a friend, not presenting to an audience."
    
    pacing: string
      What it is: How the creator structures sentences and controls energy.
      Example: "Short punchy sentences. Rarely more than 15 words per beat. 
                Uses pauses deliberately. Speeds up when excited, slows down for emphasis."
    
    hook_pattern: string
      What it is: How the creator consistently opens their videos.
      Example: "Always opens with either a provocative question directed at the viewer 
                or a bold personal claim, within the first 8 seconds. 
                Never starts with 'Hey guys' or a greeting."
    
    vocabulary_level: string
      What it is: The complexity and character of language the creator uses.
      Example: "Everyday language. Avoids jargon entirely. 
                Occasionally self-deprecating. Uses specific numbers whenever possible 
                rather than vague qualifiers."
    
    signature_phrases: list of strings
      What it is: Recurring phrases, transitions, or verbal habits this creator uses.
      Example: ["Here's the thing", "And I mean that literally", 
                "So I actually tested this", "which surprised me"]
    
    what_to_avoid: list of strings
      What it is: Tone, phrasing, or language patterns that are distinctly NOT this creator.
      This is as important as the positive traits — it tells generation agents 
      what style drift looks like.
      Example: ["Corporate language", "Passive voice", "Hedging without specifics",
                "Inspirational quotes", "Vague calls to action like 'let me know in the comments'"]

title_formula
  Type: object containing the following fields:
  
    structure: string
      What it is: The pattern or template the creator's best titles follow.
      Example: "Number + Noun + Specific Outcome" 
               or "I [did specific thing] for [specific timeframe] — here's what [actually] happened"
    
    avg_word_count: integer
      What it is: The average number of words in their best-performing titles.
      Example: 9
    
    uses_caps: boolean
      What it is: Whether the creator uses ALL CAPS words within titles.
      Example: true (as in "5 Things That ACTUALLY Work")
    
    uses_numbers: boolean
      What it is: Whether the creator's strong titles lead with or prominently feature numbers.
      Example: true
    
    uses_questions: boolean
      What it is: Whether titles frequently end with or are structured as questions.
      Example: false
    
    emotional_hook_type: string
      What it is: The primary psychological mechanism the creator's titles use to earn the click.
      Allowed values: "curiosity gap", "social proof", "fear of missing out", 
                      "personal authority", "specific transformation", "controversy"
      Example: "curiosity gap"
    
    example_titles: list of strings
      What it is: 3 to 5 actual titles from the creator's best-performing videos.
      These are used as references by the metadata agent when generating new titles.
      Example: ["I Used Notion for 30 Days — Here's What Actually Happened",
                "7 Things Productive People Do Before 9 AM",
                "Obsidian vs Notion — Which One Actually Wins?"]

thumbnail_style
  Type: object containing the following fields:
  
    dominant_colors: list of strings
      What it is: The colors that appear most consistently in this creator's thumbnails.
      Example: ["red", "white", "black", "orange"]
    
    layout_pattern: string
      What it is: The recurring spatial arrangement of elements in the thumbnail.
      Example: "Creator face occupies left two-thirds of frame. 
                Bold text stacked on the right third. Solid color background.
                Subject always looking directly into camera or at the text."
    
    text_style: string
      What it is: How text appears on the thumbnail — size, weight, capitalization, outline.
      Example: "2 to 4 words maximum. All caps. Very thick font weight. 
                White text with thick black outline for readability on any background."
    
    facial_expression: string
      What it is: The emotional register the creator's face communicates in thumbnails.
      Example: "Surprised or excited. Eyebrows raised. Mouth slightly open. 
                Never neutral or smiling politely. Always a strong emotion."
    
    uses_props: boolean
      What it is: Whether the creator typically holds something, points at something, 
                  or has an object as a focal point in thumbnails.
      Example: true
    
    background_type: string
      What it is: What kind of background appears in thumbnails.
      Allowed values: "solid color", "gradient", "blurred real location", 
                      "illustrated/graphic", "product or app screenshot"
      Example: "solid color"
    
    uses_graphic_elements: boolean
      What it is: Whether the creator uses arrows, circles, highlight boxes, 
                  or other graphic elements to direct viewer attention.
      Example: false

content_patterns
  Type: object containing the following fields:
  
    avg_duration_seconds: integer
      What it is: The average video length across the catalog.
      Example: 342
    
    optimal_duration_range: object with min (integer) and max (integer)
      What it is: The duration range that correlates with the creator's highest retention.
      Example: min 240, max 420 (4 to 7 minutes)
    
    format_preferences: list of strings
      What it is: The content formats that appear most in their catalog and 
                  correlate with strong performance.
      Example: ["listicle", "30-day-challenge", "head-to-head-comparison", "tool-review"]
    
    posting_frequency: string
      What it is: How often the creator publishes, inferred from the published_at dates 
                  across the catalog.
      Example: "2 to 3 times per week, most commonly Tuesday and Friday"
    
    best_performing_topics: list of strings
      What it is: Topic categories that consistently appear in high-view-count and 
                  high-CTR videos.
      Example: ["productivity apps", "30-day challenges", "tool comparisons", 
                "morning routines"]
    
    worst_performing_topics: list of strings
      What it is: Topic categories that consistently appear in low-view-count or 
                  low-CTR videos.
      Example: ["setup tours", "vague habit advice", "gear reviews without challenge format"]

performance_benchmarks
  Type: object containing the following fields:
  
    avg_views: float
      What it is: The mean view count across all catalog videos.
    
    avg_ctr: float
      What it is: The mean click-through rate across all catalog videos.
    
    avg_retention: float
      What it is: The mean average retention percentage across all catalog videos.
    
    top_quartile_views: float
      What it is: The view count threshold that separates the top 25% of 
                  this creator's videos from the rest. 
                  This is what "a hit" means for this specific creator.
    
    bottom_quartile_views: float
      What it is: The view count threshold below which a video is considered 
                  underperforming for this creator.
    
    Note: These five values are calculated mathematically from the catalog data —
          they are not generated by the LLM. The LLM does not do arithmetic 
          on numbers reliably. Calculate these in Python before passing the 
          catalog to the DNA agent, and include the calculated results in 
          the prompt context.
```

---

### Schema 3 — Content Opportunity

**What it represents:** One recommendation for what the creator should make next. This is what the opportunity agent produces.

**Who creates it:** The opportunity agent.

**Who reads it:** The creator (via the dashboard), the script agent, the thumbnail agent, and the metadata agent.

**Fields:**

```
id
  Type: string
  Example: "opp_001"

creator_id
  Type: string
  Links this opportunity to a specific creator.

created_at
  Type: timestamp

topic
  Type: string
  What it is: The core subject or premise of the recommended video.
  Example: "Testing 5 AI writing tools side by side for one month and 
            measuring actual output quality"

working_title
  Type: string
  What it is: A draft title for this opportunity, written in the creator's 
              learned title formula. This is a starting point, not the final title.
  Example: "I Tested 5 AI Writing Tools for 30 Days — Here's the Honest Ranking"

rationale
  Type: object containing the following fields:
  
    dna_fit_explanation: string
      What it is: Why this topic fits this specific creator, with explicit references 
                  to their DNA profile. Must cite specific profile attributes.
                  If it says "this fits your style" without citing what style 
                  and why, the prompt that produced it is wrong.
      Example: "This maps directly to your highest-performing format (30-day challenge)
                and your best-performing topic category (productivity app comparisons).
                The title follows your established formula of 'I tested X for Y days.'
                The specific ranking element satisfies your audience's expectation 
                for definitive answers, which aligns with your curiosity-gap hook type."
    
    performance_prediction: string
      What it is: What aspects of the creator's past top-performing content this mirrors,
                  and what that predicts about performance.
      Example: "Your top 3 videos by CTR are all app comparisons with a 30-day structure.
                This topic combines both. Your 30-day challenge videos average 
                420k views vs 71k for non-challenge formats."
    
    trend_relevance: string
      What it is: Why this topic is relevant right now in the creator's niche.
      Note: For the hackathon, this is populated from a static seed list of 
            current trends in the niche — not a live API call.
      Example: "AI writing tools are the most searched productivity topic in this 
                niche over the last 60 days. Three major new releases happened 
                in the last 30 days, giving a natural news hook."
    
    risks: string
      What it is: What could cause this video to underperform despite the good fit.
      Example: "If the creator cannot access all 5 tools, the comparison loses 
                specificity. Tool comparison videos also have a shorter shelf life 
                than general productivity advice videos."

fit_score
  Type: float, 0.0 to 1.0
  What it is: A numeric representation of how well this opportunity matches 
              the creator's DNA profile.
  Thresholds: 
    0.8 and above — strong fit, recommend
    0.6 to 0.79 — viable fit, proceed with awareness of gaps
    Below 0.6 — weak fit, regenerate

confidence
  Type: string
  Allowed values: "high", "medium", "low"
  What it is: The agent's confidence in the fit score and rationale.

recommended_format
  Type: string
  What it is: Which of the creator's preferred formats this opportunity should use.
  Example: "30-day-challenge"

recommended_duration_seconds
  Type: integer
  What it is: Suggested video length, derived from the creator's optimal duration range 
              and the complexity of the topic.
  Example: 360

target_hook
  Type: string
  What it is: What the opening hook should accomplish for this specific video.
  Example: "Open with the total cost of all 5 tools and ask 'is any of it worth it' 
            — creates immediate stakes and curiosity."

status
  Type: string
  Allowed values: "pending", "approved", "rejected", "in_production", "published"
```

---

### Schema 4 — Script

**What it represents:** The complete script for one video, written in the creator's learned voice.

**Who creates it:** The script agent.

**Who reads it:** The video rendering layer (which converts scenes to HyperFrames HTML), the TTS system (which reads the voiceover text aloud), and the captions system.

**Fields:**

```
id
  Type: string

opportunity_id
  Type: string
  Links this script to the opportunity that generated it.

creator_id
  Type: string

hook
  Type: object containing:
  
    voiceover_text: string
      What it is: The exact words spoken in the first 5 to 15 seconds.
    
    visual_description: string
      What it is: What appears on screen during the hook.
    
    duration_seconds: integer
      What it is: How long the hook section runs.

scenes
  Type: list of objects, each containing:
  
    scene_number: integer
      What it is: The order of this scene in the video. Starts at 1.
    
    scene_type: string
      Allowed values: "talking_head", "text_overlay", "title_card", 
                      "comparison_split", "list_reveal", "b_roll_description"
      What it is: What kind of visual treatment this scene gets. 
                  This maps directly to HyperFrames template types.
    
    voiceover_text: string
      What it is: The exact words spoken during this scene.
    
    visual_description: string
      What it is: What appears on screen — text overlays, graphics, layout.
                  This is what the HyperFrames template renders.
    
    on_screen_text: string or null
      What it is: If there is text displayed on screen during this scene, 
                  what it says. Separate from the voiceover.
    
    duration_seconds: integer
      What it is: How long this scene runs.

outro
  Type: object containing:
  
    voiceover_text: string
    visual_description: string
    call_to_action: string
      What it is: The specific action the creator asks the viewer to take.
      Example: "Subscribe if you want the 60-day follow-up"
    duration_seconds: integer

full_voiceover_text
  Type: string
  What it is: The complete spoken script as one unbroken block of text.
              This is what gets passed to the TTS system.
              It is the concatenation of hook voiceover + all scene voiceovers + outro voiceover,
              in order.

estimated_duration_seconds
  Type: integer
  What it is: The sum of all scene durations including hook and outro.
              This should fall within the creator's optimal_duration_range.

word_count
  Type: integer
  What it is: Total word count of the full_voiceover_text.
```

---

### Schema 5 — Thumbnail Variant

**What it represents:** One generated thumbnail option. Multiple variants are generated and then the scorer picks one.

**Who creates it:** The thumbnail agent (SVG markup) and the thumbnail renderer (PNG file).

**Who reads it:** The scorer agent (to evaluate and select), and the dashboard (to display).

**Fields:**

```
id
  Type: string

asset_id
  Type: string
  Links this thumbnail to the GeneratedAsset it belongs to.

variant_number
  Type: integer
  What it is: 1, 2, or 3. The position in the set of generated variants.

svg_source
  Type: string
  What it is: The raw SVG markup generated by the thumbnail agent.
              This is the source file — cairosvg converts this to a PNG.

png_path
  Type: string
  What it is: The local file path to the rendered PNG.
              Example: "./output/thumbnails/thumb_001_v1.png"

layout_description
  Type: string
  What it is: A plain English description of what this thumbnail shows.
              Written by the thumbnail agent alongside the SVG.
              Example: "Dark blue background. Creator face left half of frame, 
                        looking surprised. Five app icons arranged in a grid on the right.
                        White bold text 'HONEST RANKING' in the top right corner."

selected
  Type: boolean
  What it is: Whether this variant was chosen by the scorer agent.
              Only one variant in a set has selected: true.

selection_reason
  Type: string or null
  What it is: If selected is true, why the scorer chose this variant over the others.
              Example: "This variant most closely matches the creator's established 
                        layout_pattern of 'creator face left, bold text right' and 
                        uses the dominant_colors (dark blue, white) from their profile."
```

---

### Schema 6 — Metadata

**What it represents:** The publishing metadata for one piece of content — title, description, tags.

**Who creates it:** The metadata agent.

**Who reads it:** The scorer agent (to check title formula fit), the publisher (to post to the platform), and the dashboard.

**Fields:**

```
id
  Type: string

asset_id
  Type: string

title
  Type: string
  What it is: The final chosen title, written following the creator's title_formula.
  Example: "I Tested 5 AI Writing Tools for 30 Days — Here's the Honest Ranking"

title_formula_match
  Type: string
  What it is: A note from the metadata agent explaining how this title maps 
              to the creator's title_formula.
  Example: "Follows the 'I [did specific thing] for [specific timeframe] — 
            here's what [actually] happened' structure. 
            Contains specific number (5), specific timeframe (30 days), 
            and definitive framing (Honest Ranking)."

description
  Type: string
  What it is: The full video description as it will be published.
              Includes the main body, timestamps if applicable, and links.

tags
  Type: list of strings
  What it is: Keywords for platform search and discovery.
  Count: 10 to 15 tags for YouTube.

category
  Type: string
  What it is: Platform content category.
  Example: "Science & Technology"

scheduled_publish_time
  Type: timestamp or null
  What it is: When the content is scheduled to go live.
              Null if not yet scheduled.

platform_targets
  Type: list of strings
  What it is: Which platforms this content is being published to.
  Example: ["youtube"]
```

---

### Schema 7 — Quality Score

**What it represents:** The output of the scorer agent's evaluation of a generated asset against the creator's DNA profile.

**Who creates it:** The scorer agent.

**Who reads it:** The orchestrator (to decide whether to accept or regenerate), and the dashboard (to show in the decision log).

**Fields:**

```
asset_id
  Type: string

overall_score
  Type: float, 0.0 to 1.0
  What it is: A weighted composite of the individual dimension scores below.

thumbnail_fit_score
  Type: float, 0.0 to 1.0
  What it is: How well the selected thumbnail matches the creator's thumbnail_style.

title_fit_score
  Type: float, 0.0 to 1.0
  What it is: How well the generated title matches the creator's title_formula.

voice_fit_score
  Type: float, 0.0 to 1.0
  What it is: How well the script matches the creator's voice profile.

passed
  Type: boolean
  What it is: Whether the asset passed the quality gate.
  Rule: passed is true if overall_score is greater than or equal to threshold_used.

threshold_used
  Type: float
  What it is: The minimum overall_score required to pass.
  Default: 0.75
  This can be adjusted per creator if 0.75 is too strict or too lenient 
  for the seed data being used.

rejection_reason
  Type: string or null
  What it is: If passed is false, a plain English explanation of why it failed 
              and what specifically does not match the creator's profile.
              Example: "Thumbnail uses a blurred background (background_type: blurred) 
                        but this creator's profile specifies solid color backgrounds. 
                        Title does not include a specific number or timeframe, 
                        which is required by the title_formula."
  Null if passed is true.

regeneration_count
  Type: integer
  What it is: How many times this asset was regenerated before either passing 
              or hitting the retry cap.
  Starts at 0. Maximum value: 2 (the retry cap).
```

---

### Schema 8 — Decision Log Entry

**What it represents:** One recorded decision made by the orchestrator at any stage in the pipeline. The full set of these entries for one pipeline run is the decision log — the most important output for the demo.

**Who creates it:** The orchestrator, at every stage, including successful stages, rejection events, and regeneration events.

**Who reads it:** The dashboard (to render the decision log timeline).

**Fields:**

```
id
  Type: string

pipeline_run_id
  Type: string
  What it is: Groups all log entries from one end-to-end run together.

creator_id
  Type: string

timestamp
  Type: timestamp

stage
  Type: string
  What it is: Which pipeline stage this entry is from.
  Allowed values: "dna_agent", "opportunity_agent", "script_agent", 
                  "thumbnail_agent", "metadata_agent", "scorer", 
                  "regenerate", "publish"

decision
  Type: string
  What it is: What was decided, in plain language. One to two sentences.
  Examples:
    "Selected opportunity 'AI Writing Tool 30-Day Test' with fit score 0.87."
    "Thumbnail variant 2 REJECTED — does not match creator's layout_pattern or background_type."
    "Regenerating thumbnail set. Attempt 2 of 2."
    "Asset passed quality gate with overall score 0.81."

rationale
  Type: string
  What it is: Why this decision was made, in plain language. 
              Must reference the creator's DNA profile where relevant.
              This is not a technical log — it is a readable explanation 
              of the agent's reasoning.
  Example: "Fit score of 0.87 exceeds the 0.8 threshold for a strong recommendation. 
            Rationale cites creator's two best-performing formats (30-day challenge 
            and app comparison) and maps directly to their top-performing topic category."

input_summary
  Type: string
  What it is: A brief summary of what went into this decision.
  Example: "CreatorDNAProfile for creator_001. 3 ContentOpportunity candidates 
            with fit scores 0.87, 0.71, 0.63."

output_summary
  Type: string
  What it is: A brief summary of what came out of this decision.
  Example: "ContentOpportunity opp_003 selected and passed to script agent."

score
  Type: float or null
  What it is: If this stage produced a numeric score, include it here.
              Null for stages that do not produce a score.

status
  Type: string
  Allowed values: "success", "rejected", "regenerated", "failed"
  What it is: The outcome of this stage.
```

---

### Schema 9 — Generated Asset

**What it represents:** The complete production package for one piece of content — script, video, thumbnails, and metadata — as one unified object.

**Who creates it:** The orchestrator assembles this as each generation stage completes.

**Who reads it:** The scorer agent, the publisher, and the dashboard.

**Fields:**

```
id
  Type: string

opportunity_id
  Type: string

creator_id
  Type: string

created_at
  Type: timestamp

script
  Type: Script object (Schema 4 above)

video
  Type: object containing:
  
    file_path: string or null
      The local path to the rendered MP4. Null until rendering is complete.
    
    duration_seconds: integer or null
      Actual rendered duration. Null until rendering is complete.
    
    resolution: string
      Example: "1920x1080"
    
    has_captions: boolean
    
    render_status: string
      Allowed values: "pending", "rendering", "complete", "failed"

thumbnails
  Type: list of ThumbnailVariant objects (Schema 5 above)

metadata
  Type: Metadata object (Schema 6 above)

quality_score
  Type: QualityScore object (Schema 7 above) or null
  Null until the scorer agent has run.

pipeline_run_id
  Type: string
  Links this asset to the PipelineRun that produced it.
```

---

### Schema 10 — Pipeline Run

**What it represents:** One complete end-to-end execution of the pipeline. The container that links all other objects from one run together.

**Who creates it:** The orchestrator when a run starts.

**Who reads it:** The dashboard (for run status and history), and the `/pipeline/{run_id}/status` polling endpoint.

**Fields:**

```
id
  Type: string

creator_id
  Type: string

started_at
  Type: timestamp

completed_at
  Type: timestamp or null
  Null while the run is still in progress.

status
  Type: string
  Allowed values: "running", "complete", "failed", "partial"
  Partial means some stages completed but the run did not finish successfully.

current_stage
  Type: string
  What it is: The name of the stage that is currently executing.
  Updated in real time as the pipeline progresses.
  Used by the PipelineProgress frontend component for live stage indicators.

opportunity_id
  Type: string or null
  The ContentOpportunity selected for this run. Null until the opportunity 
  agent has run and selected one.

asset_id
  Type: string or null
  The GeneratedAsset produced by this run. Null until generation is complete.

stages_completed
  Type: list of strings
  What it is: Ordered list of stage names that finished successfully.
  Example: ["dna_agent", "opportunity_agent", "script_agent", "thumbnail_agent"]

stages_failed
  Type: list of strings
  What it is: Stages that encountered an error.

total_duration_seconds
  Type: float or null
  What it is: Total wall-clock time for the full run, from started_at to completed_at.
  Null until the run completes.

total_llm_calls
  Type: integer
  What it is: How many Claude API calls were made during this run.
  Useful for understanding cost per run.

regeneration_count
  Type: integer
  What it is: Total number of regeneration cycles triggered across all stages in this run.
```

---

## Phase 0 — Step 10: API Contract

**What this step is:**
Every endpoint the backend will expose, defined in full before any code is written. The frontend and backend agree on these contracts in Phase 0 so they can be built in parallel without waiting on each other.

---

### Catalog and Profile Endpoints

```
POST /catalog/ingest

  Purpose:
    Accepts a batch of Source Video objects and stores them in the database.
    Does not run any agent logic. Storage only.
  
  Receives:
    A JSON body containing:
      creator_id: string
      videos: list of SourceVideo objects
  
  Returns:
    creator_id: string
    videos_ingested: integer (how many were stored)
    status: "success" or "error"
    message: string (error detail if status is "error")


POST /profile/build

  Purpose:
    Triggers the DNA agent to build a CreatorDNAProfile from the 
    stored catalog for a given creator.
    Stores the resulting profile in the database.
    Returns the profile.
  
  Receives:
    creator_id: string
  
  Returns:
    The full CreatorDNAProfile object


GET /profile/{creator_id}

  Purpose:
    Retrieves the stored CreatorDNAProfile for a creator.
  
  Returns:
    The full CreatorDNAProfile object, or a 404 if no profile exists.
```

---

### Pipeline Endpoints

```
POST /pipeline/run

  Purpose:
    The single end-to-end endpoint. Runs all pipeline stages in sequence.
    This is what gets called during the live demo.
    Runs synchronously for the hackathon (the frontend waits for the response).
    Returns everything when complete.
  
  Receives:
    creator_id: string
    topic_hint: string (optional — a loose topic suggestion the opportunity 
                agent can use as a nudge, or ignore entirely)
  
  Returns:
    The full PipelineRun object, with embedded:
      selected ContentOpportunity
      GeneratedAsset (script, thumbnails, metadata, quality_score)
      Full list of DecisionLogEntry objects for this run
  
  Note on async vs sync:
    For the hackathon, run this synchronously. The frontend shows a loading 
    state. If render time is very long (more than 30 seconds), consider 
    running async and polling — but do not build async until the sync 
    version works end to end.


GET /pipeline/{run_id}/status

  Purpose:
    Returns the current status of a running pipeline.
    The PipelineProgress frontend component polls this every 2 seconds.
  
  Returns:
    run_id: string
    status: string
    current_stage: string
    stages_completed: list of strings
    stages_failed: list of strings
    progress_percentage: integer (0 to 100, calculated from stages completed)


GET /pipeline/{run_id}/log

  Purpose:
    Returns the full decision log for one pipeline run.
  
  Returns:
    run_id: string
    entries: list of DecisionLogEntry objects, ordered by timestamp ascending
```

---

### Content Endpoints

```
POST /content/recommend

  Purpose:
    Runs just the opportunity agent in isolation.
    Useful for testing the agent independently of the full pipeline.
  
  Receives:
    creator_id: string
    topic_hint: string (optional)
    count: integer (how many recommendations to return, default 3)
  
  Returns:
    list of ContentOpportunity objects


POST /content/generate

  Purpose:
    Runs the script agent, thumbnail agent, and metadata agent in sequence 
    for a given opportunity.
    Does not run the scorer. Does not render the video.
    Returns the GeneratedAsset with script, thumbnails, and metadata populated
    but video and quality_score null.
  
  Receives:
    opportunity_id: string
  
  Returns:
    GeneratedAsset object (partial — video and quality_score are null)


POST /content/score

  Purpose:
    Runs the scorer agent on an existing GeneratedAsset.
    Updates the asset's quality_score in the database.
    Writes DecisionLogEntry objects for the scoring decision.
    If the asset fails, returns the rejection reason for the regenerate loop.
  
  Receives:
    asset_id: string
  
  Returns:
    asset_id: string
    quality_score: QualityScore object
    passed: boolean
    decision_log_entries: list of DecisionLogEntry objects written during scoring


POST /content/publish

  Purpose:
    Pushes a completed, scored, passed asset to the target platform.
  
  Receives:
    asset_id: string
    platform: string (e.g. "youtube")
    scheduled_time: timestamp or null
  
  Returns:
    platform_post_id: string (the ID assigned by the platform)
    url: string (the public URL of the published content)
    status: "published" or "scheduled"
    published_at: timestamp
```

---

### File Serving Endpoints

```
GET /output/video/{filename}

  Purpose:
    Serves the rendered MP4 file to the frontend video player.
  
  Returns:
    The MP4 file as a streaming response.
    Content-Type: video/mp4


GET /output/thumbnail/{filename}

  Purpose:
    Serves a rendered PNG thumbnail to the frontend.
  
  Returns:
    The PNG file.
    Content-Type: image/png
```

---

## Phase 0 — Step 11: Seed Data Plan

**What this step is:**
The 8 fake-but-realistic catalog videos you will build and test against for the entire hackathon. You are not connecting to a real creator's channel. This seed data must be rich enough for the DNA agent to learn meaningful patterns — specifically, it needs enough variation between high and low performers that the profile reflects real signal, not just averages.

---

**The Fake Creator Concept:**
A tech and productivity YouTuber. 50,000 subscribers. Posts short educational videos (4 to 8 minutes) about productivity tools, software comparisons, and personal experiment challenges. Uploads 2 to 3 times per week. The channel has a clear pattern of high performance on structured formats (numbered lists, 30-day challenges, direct comparisons) and weak performance on vague or format-free content.

---

**The 8 Videos:**

```
Video 1 — High Performer
Title: "I Used Notion for 30 Days — Here's What Actually Happened"
Duration: 487 seconds (8 minutes 7 seconds)
Published: 2024-01-15
Views: 420,000 | Likes: 18,400 | Comments: 1,240 | CTR: 9.2% | Retention: 58%
Thumbnail description:
  Orange solid background. Creator standing center-left, looking directly 
  into camera with a surprised expression, mouth slightly open, eyebrows raised.
  Bold white text in the top right corner reading "30 DAYS" in very large letters.
  Smaller white text below reading "WAS IT WORTH IT?" Creator is holding a laptop 
  with the Notion logo visible on screen.
Transcript sample:
  "So I gave Notion an honest 30 days. Not a weekend, not a quick test — 
   30 full days of actually using it for everything. And here is what nobody 
   tells you..."
Tags: notion, productivity, 30 day challenge, note taking app, organization, 
      notion review, productivity tools 2024, notion tutorial
Lesson for DNA agent:
  30-day challenge format + specific timeframe in title + creator face 
  with strong expression + solid background = high performance

---

Video 2 — High Performer
Title: "5 Chrome Extensions That Saved Me 3 Hours a Week"
Duration: 324 seconds (5 minutes 24 seconds)
Published: 2024-01-29
Views: 380,000 | Likes: 16,200 | Comments: 890 | CTR: 8.7% | Retention: 61%
Thumbnail description:
  Dark blue solid background. Five Chrome extension icons arranged in a 
  clean grid on the right half of the frame. Creator face on the left half, 
  looking excited with eyebrows raised. Bold white text at the top center 
  reading "5 TOOLS" in all caps. No props, no graphic elements, clean layout.
Transcript sample:
  "I tracked my time for 3 weeks. These 5 extensions came out of that. 
   I am not guessing — I measured the actual time saved."
Tags: chrome extensions, productivity, browser tools, time saving, 
      productivity hacks, work smarter, chrome tips
Lesson for DNA agent:
  Number in title + specific outcome ("3 hours a week") + grid layout 
  of product icons + creator face = high performance. 
  Shorter video (5 min) = better retention.

---

Video 3 — Medium Performer
Title: "Why I Stopped Using Todoist (And What I Use Instead)"
Duration: 412 seconds (6 minutes 52 seconds)
Published: 2024-02-12
Views: 95,000 | Likes: 3,800 | Comments: 420 | CTR: 5.1% | Retention: 44%
Thumbnail description:
  White background. Todoist logo on the left with a large red X over it.
  Arrow pointing right to a different app logo on the right. Creator face 
  small at the bottom center, neutral expression. Text overlay at top 
  reading "why I switched" in mixed case, not bold.
Lesson for DNA agent:
  Comparison format is good but neutral expression + mixed case text 
  + small creator face + white background = weaker performance than 
  the high performers.

---

Video 4 — High Performer
Title: "7 Things Productive People Do Before 9 AM"
Duration: 398 seconds (6 minutes 38 seconds)
Published: 2024-02-26
Views: 510,000 | Likes: 22,100 | Comments: 1,890 | CTR: 10.3% | Retention: 63%
Thumbnail description:
  Red solid background. Alarm clock graphic on the left side. Creator on 
  the right side, smiling broadly with eyes wide. Bold white text in the 
  top left reading "7 THINGS" in very large all-caps letters. Clean, simple, 
  high contrast.
Lesson for DNA agent:
  Number + list format + red background + creator face with strong positive 
  expression + bold all-caps text = highest performance. Listicle format 
  performs as well as challenge format.

---

Video 5 — Low Performer
Title: "My Full Productivity Setup Tour 2024"
Duration: 721 seconds (12 minutes 1 second)
Published: 2024-03-11
Views: 28,000 | Likes: 890 | Comments: 143 | CTR: 3.2% | Retention: 38%
Thumbnail description:
  Photo of a desk setup, slightly blurred background. Small text overlay 
  at the bottom reading "My Setup Tour 2024" in regular weight font. 
  No creator face visible. No bold colors. No graphic elements.
Lesson for DNA agent:
  No creator face + blurred background + no bold text + no number 
  + vague title format + long duration (12 min) = clear low performer.
  Tour format does not match the creator's audience expectations.

---

Video 6 — Medium Performer
Title: "I Tried the Pomodoro Technique for a Month"
Duration: 356 seconds (5 minutes 56 seconds)
Published: 2024-03-25
Views: 71,000 | Likes: 2,900 | Comments: 310 | CTR: 4.8% | Retention: 47%
Thumbnail description:
  Red solid background. Timer graphic in the center. White bold text 
  reading "POMODORO" at the top. Creator face not visible — timer is 
  the only focal point.
Lesson for DNA agent:
  Challenge format is right. Title formula is close (I tried X for a month).
  But no creator face = consistently lower performance than videos with 
  the creator's face prominent.

---

Video 7 — High Performer
Title: "Obsidian vs Notion — Which One Actually Wins?"
Duration: 445 seconds (7 minutes 25 seconds)
Published: 2024-04-08
Views: 290,000 | Likes: 12,400 | Comments: 1,650 | CTR: 7.9% | Retention: 55%
Thumbnail description:
  Black solid background. Obsidian logo on the left. Notion logo on the right.
  Creator face in the center between the two logos, looking intensely at the 
  camera with a slight smirk, arms crossed. Bold white text at the top 
  reading "VS" in very large letters. Clean battle-style layout.
Lesson for DNA agent:
  Direct comparison format + creator face prominent + bold minimal text 
  + black background (dark solid = works well) + "vs" framing = 
  strong performance. Comparison format is the second best format 
  after challenge.

---

Video 8 — Low Performer
Title: "How I Organize My Digital Life"
Duration: 634 seconds (10 minutes 34 seconds)
Published: 2024-04-22
Views: 19,000 | Likes: 610 | Comments: 87 | CTR: 2.9% | Retention: 35%
Thumbnail description:
  Abstract geometric graphic with blue and grey shapes. No creator face. 
  No text overlay. No recognizable focal point. Looks like a stock image.
Lesson for DNA agent:
  Abstract thumbnail with no creator face + no text + vague title 
  (no number, no specific outcome, no timeframe) + long duration = 
  worst performer in the catalog. Confirms that vague format 
  and no creator presence consistently underperforms.
```

---

**What the DNA Agent Should Learn From This Seed Data:**

```
High-performance signals:
  - Numbers in the title (5, 7, 30 days, 3 hours)
  - Specific formats: 30-day challenge, numbered list, direct comparison
  - Creator face prominent, occupying at least half the thumbnail
  - Strong facial expression (surprised, excited, intense) — never neutral
  - Solid color backgrounds (red, dark blue, orange, black)
  - Bold all-caps white text, 2 to 4 words
  - Video duration between 5 and 8 minutes (324 to 487 seconds)
  - First-person framing in titles ("I Used", "I Tried", "I Tested")

Low-performance signals:
  - No creator face in thumbnail
  - Blurred or abstract backgrounds
  - Mixed case or low-weight text
  - Vague titles without numbers or specific outcomes
  - Videos longer than 10 minutes
  - Tour or general overview formats without a specific challenge framing

Performance benchmarks calculable from this data:
  Average views: (420k + 380k + 95k + 510k + 28k + 71k + 290k + 19k) / 8 = 226,625
  Average CTR: (9.2 + 8.7 + 5.1 + 10.3 + 3.2 + 4.8 + 7.9 + 2.9) / 8 = 6.5%
  Average retention: (58 + 61 + 44 + 63 + 38 + 47 + 55 + 35) / 8 = 50.1%
  Top quartile threshold (top 2 of 8): approximately 400,000 views
  Bottom quartile threshold (bottom 2 of 8): approximately 24,000 views
```

---

## Phase 0 — Step 12: The Cut List

**What this step is:**
The decisions made now, while calm, about what gets dropped first if time runs out. At the halfway point of the hackathon, review this list and execute cuts immediately rather than letting every phase slip a little.

---

**Cut First — Drop Without Hesitation**

Multi-platform publishing:
YouTube only. TikTok, Instagram, and LinkedIn show as convincing UI buttons that display a "scheduled" confirmation without a real API call. Nobody expects every platform to be wired in a hackathon.

Real analytics and feedback loop:
The stretch goal of pulling actual post-performance and feeding it back into the DNA profile. Show it as a UI stub — a "Performance Sync" button that displays placeholder data. Do not build it.

User authentication:
No login system. No accounts. No sessions. The demo runs as creator_001. Authentication is zero value for a hackathon demo.

Live trend data API:
The opportunity agent does not call a live trending topics API. Use a static JSON file with 10 to 15 current topics in the productivity and tech niche. Hardcode it in the seed data directory.

---

**Cut Second — Drop If Behind by More Than 20%**

Video rendering:
If HyperFrames proves unreliable, show a pre-rendered example video for the demo and narrate that the generation pipeline produced it offline. The decision layer is the innovation, not the video render. The demo still works without live rendering.

TTS audio:
If voice generation is causing problems, narrate the demo yourself over a silent video or script display. Audio is polish, not the core value proposition.

Three thumbnail variants:
If generating three SVG thumbnails is slow or unstable, generate one and still run the scorer on it. The reject/regenerate loop is what matters. One variant is enough to demonstrate the gate.

---

**Cut Third — Emergency Only**

Video entirely:
If the render is completely broken, demo script plus thumbnail plus metadata plus decision log. The live reject/regenerate cycle on the scorer is still compelling without a video.

Frontend:
If the frontend is unfinished, demo from the API directly using a REST client like Insomnia. Ugly but functional. Every other component still works.

Real platform publishing:
Show a publish confirmation screen in the UI that does not make a real API call. The content of the decision log and the generated assets are the demo — not whether a real YouTube video appears.

---

**Never Cut**

The DNA agent producing a real, specific CreatorDNAProfile from the seed catalog.
The opportunity recommendation with a rationale explicitly tied to the profile.
The scorer running a live reject/regenerate cycle, visible in the decision log.
The decision log being displayed in the UI with stage-by-stage reasoning.

---

## Phase 0 — Step 13: The Done Definition

Phase 0 is complete when every item on this checklist is true. Not mostly true. Every item.

```
Scope
  [ ] The MVP sentence is written, memorized, and visible somewhere during the build
  [ ] The differentiation (what no other tool does) is written in two sentences
  [ ] The cut list is written and saved somewhere you will check at the halfway point

Stack
  [ ] Every stack decision is made and you can give a one-sentence reason for each
  [ ] No decisions will be relitigated during the build

Repository
  [ ] Git initialized with the folder structure from Step 4 in place (empty but created)
  [ ] .env file created with all key slots defined (values can be filled in later)
  [ ] .gitignore created and verified (.env is in it, checked before first push)
  [ ] README.md exists with at minimum: project name, one-paragraph description, 
      and a placeholder for run instructions

Data
  [ ] All 8 seed videos are drafted in plain text (Step 11)
  [ ] The performance benchmarks for the seed data are calculated (Step 11 bottom section)
  [ ] Every schema from Step 9 is understood and you can describe each field's purpose
      without looking at notes

API
  [ ] Every endpoint from Step 10 is understood
  [ ] You know what the frontend will display and what API call produces it

Environment
  [ ] Python 3.11+ is installed and confirmed
  [ ] Node.js 18+ is installed and confirmed
  [ ] Virtual environment is created (not activated — just created)
  [ ] Anthropic API key is in hand (or you know exactly when it will arrive)

Mental
  [ ] You can run the full demo in your head, start to finish, without gaps
  [ ] You know what the "wow moment" is (the live reject/regenerate cycle in the scorer)
      and you can explain in one sentence why it matters
```

---

*Phase 0 produces no running code. Its output is a fully resolved decision set that makes every subsequent phase faster, cleaner, and less likely to stall on a question that should have been answered before the clock started.*