# Phase 1 — Backend Foundations & Data Layer

---

## What Phase 1 Is and Why It Comes Before Everything Else

Phase 1 is not about building features. It is about building the surface that every feature plugs into. When Phase 1 is done, every other phase has a stable, agreed-upon foundation to build against simultaneously. The agent logic from Phase 2 knows exactly what shape its output needs to be. The frontend from Phase 5 knows exactly what to expect from every API call. The orchestrator from Phase 4 knows exactly what the database looks like and how to write to it.

If Phase 1 is skipped or done loosely, every later phase will spend time negotiating with every other phase about shapes, field names, and contracts. That negotiation happens at the worst possible time — when you are deep in complex logic and cannot afford the context switch.

The three things Phase 1 produces are the data models, the storage layer, and the API skeleton. None of them contain real logic yet. All of them are stable enough that everything built after this point can treat them as a contract.

---

## Phase 1 — Step 1: Translate All Schemas Into Validated Data Models

**What this step is about:**

In Phase 0, every schema was defined in plain language. In this step, you translate each one into a formal validated data model — meaning every field has a type, every optional field is explicitly marked as optional, and every model can validate incoming data and reject it cleanly if it does not match.

This is the first real code you write, and you write it before touching the database, before touching any endpoint, and before touching any agent. The reason is that the data models are the shared language of the entire system. Every agent, every endpoint, every database table, and every frontend API call speaks in terms of these models. If you write the database schema first and then try to derive the models from it, or write an endpoint first and then try to figure out what shape it should return, you end up with drift — small inconsistencies between layers that compound into hours of debugging later.

**What you are building:**

You are building one central file that contains every data model for the entire project. Not one model per file, not models scattered across different modules — one place. The reason is that when a field changes, you change it in exactly one place and every layer that imports from that place automatically picks up the change.

**The models you are building and what each one needs to enforce:**

---

**Source Video Model**

This is the shape of one past video from the creator's catalog. Every field should reflect what was defined in Phase 0 Schema 1.

The model needs to enforce:
- The id is always a string and always present
- The title and transcript are always strings and always present — no nulls on these because the DNA agent cannot function without them
- Duration is always an integer, never a float — seconds are whole numbers
- Published date is a proper date, not a freeform string, so that the DNA agent can calculate posting frequency correctly
- Platform is constrained to a specific set of allowed values — not any arbitrary string
- The performance block is a nested object where views, likes, and comments are always integers, but CTR and retention are floats that can be null if the platform does not expose them — null means unknown, zero means literally zero, and confusing the two will corrupt the DNA agent's benchmark calculations
- The thumbnail block contains a URL (which can be an empty string for seed data) and a description which must always be a non-empty string because this is how the DNA agent learns visual style
- Tags is a list of strings that can be empty but cannot be null

---

**Creator DNA Profile Model**

This is what the DNA agent produces. It is the most important model in the system because every generation agent conditions on it.

The model needs to enforce:
- All the nested sub-objects are present — voice, title formula, thumbnail style, content patterns, and performance benchmarks must all be present for the profile to be considered valid. A partial profile should never be stored as a complete one
- The voice sub-object contains string fields for tone, pacing, hook pattern, and vocabulary level, and list-of-string fields for signature phrases and what to avoid — all required, none nullable
- The title formula sub-object contains a structure string, average word count as an integer, three booleans for uses caps / uses numbers / uses questions, an emotional hook type string, and a list of example titles — the example titles list must have at least one entry
- The thumbnail style sub-object contains dominant colors as a list of strings with at least one entry, plus string fields for layout pattern, text style, facial expression, and background type, plus two booleans for uses props and uses graphic elements
- The content patterns sub-object contains average duration as an integer, optimal duration range as a nested object with min and max integers, format preferences as a list of strings with at least one entry, posting frequency as a string, and best/worst performing topics as lists of strings
- The performance benchmarks sub-object contains five floats — average views, average CTR, average retention, top quartile views, and bottom quartile views — and none of these should be null because they are calculated mathematically before the DNA agent runs, not inferred by the LLM

---

**Content Opportunity Model**

This is what the opportunity agent produces — one recommendation for what to make next.

The model needs to enforce:
- The fit score is a float between 0.0 and 1.0, with validation that rejects anything outside that range
- The confidence field is constrained to exactly three allowed values — high, medium, low — and nothing else
- The status field is constrained to the allowed state transitions — pending, approved, rejected, in production, published
- The rationale is a nested object, not a flat string, because the individual parts of it (DNA fit explanation, performance prediction, trend relevance, risks) are displayed separately in the UI and evaluated separately by the scorer
- The rationale's DNA fit explanation must be present and non-empty — an empty explanation means the opportunity agent's prompt is wrong and produced an unacceptable output
- Recommended duration is an integer in seconds, not a string like "6 minutes"

---

**Script Model**

This is what the script agent produces. It is also what the video rendering layer consumes.

The model needs to enforce:
- The hook, scenes list, and outro are all required — a script with no hook or no outro is incomplete and should not be stored
- Each scene in the scenes list is a nested object with scene number, scene type, voiceover text, visual description, optional on-screen text, and duration in seconds
- Scene type is constrained to a specific set of allowed values that map directly to HyperFrames template types — talking head, text overlay, title card, comparison split, list reveal, b-roll description
- The full voiceover text field is required and must be the concatenated version of all voiceover sections — this is what gets passed to the TTS system
- Estimated duration is an integer and must be present — the rendering layer uses it

---

**Thumbnail Variant Model**

This represents one generated thumbnail option.

The model needs to enforce:
- The SVG source is a string and must be present — this is the raw markup the renderer needs
- The PNG path is a string that can be null before rendering happens but must be a non-null string after the rendering step completes
- Selected is a boolean that defaults to false — only one variant in a set should have selected as true, but this validation happens in the orchestrator logic, not in the model itself
- Selection reason is null when selected is false and must be a non-empty string when selected is true

---

**Metadata Model**

This is what the metadata agent produces — title, description, tags.

The model needs to enforce:
- Title is a required non-empty string
- Title formula match is a required non-empty string — this is the metadata agent's explanation of how the title maps to the creator's formula, and it is displayed in the UI and evaluated by the scorer
- Description is a required non-empty string
- Tags is a list of strings with a minimum of 5 and a maximum of 20 entries — not zero, not unlimited
- Scheduled publish time can be null if not yet scheduled

---

**Quality Score Model**

This is what the scorer agent produces.

The model needs to enforce:
- Overall score, thumbnail fit score, title fit score, and voice fit score are all floats between 0.0 and 1.0
- Passed is a boolean derived from whether overall score is greater than or equal to threshold used — this should be a computed field, not a field the agent sets arbitrarily
- Threshold used is a float that records what threshold was applied — default 0.75 — so the log is honest about the bar that was set
- Rejection reason is null when passed is true and must be a non-empty string when passed is false
- Regeneration count is an integer that starts at 0 and cannot exceed 2

---

**Decision Log Entry Model**

This is the most important model for the demo. Every stage writes at least one of these.

The model needs to enforce:
- Stage is constrained to the known set of pipeline stage names — DNA agent, opportunity agent, script agent, thumbnail agent, metadata agent, scorer, regenerate, publish — nothing else
- Status is constrained to four values — success, rejected, regenerated, failed
- Decision is a required non-empty string — it is what appears as the headline of each log entry in the UI
- Rationale is a required non-empty string — it is the explanation of why
- Score is a float that can be null for stages that do not produce a numeric score

---

**Generated Asset Model**

This is the container for the full production package — script, video, thumbnails, and metadata.

The model needs to enforce:
- The script field starts null and becomes a Script object once the script agent runs
- The video block starts with render status as pending and file path as null, and these update as the rendering pipeline progresses
- The thumbnails field is a list of Thumbnail Variant objects that starts empty and gets populated by the thumbnail agent
- The metadata field starts null and becomes a Metadata object once the metadata agent runs
- The quality score field starts null and becomes a Quality Score object once the scorer runs

---

**Pipeline Run Model**

This is the container for one complete end-to-end execution.

The model needs to enforce:
- Status is constrained to running, complete, failed, and partial
- Stages completed is a list of strings that is append-only — items are never removed from it
- The total duration field is null while the run is active and must be a float once completed at is set
- Total LLM calls and regeneration count are integers that start at 0

---

**What "done" looks like for Step 1:**

You can create an instance of every model with valid test data and it succeeds. You can create an instance with invalid data — a fit score of 1.5, a null transcript, an unrecognized stage name — and the model rejects it with a clear error message. You do not need to store anything yet. You do not need any endpoints yet. The models exist, they validate correctly, and every field behaves as defined.

---

## Phase 1 — Step 2: Set Up the Database and Storage Layer

**What this step is about:**

Now that the data models exist, you set up the storage layer that persists them. The goal of the storage layer in a hackathon context is simple: make sure data survives a page refresh or a server restart during the demo. A blank screen during a demo because the state was held in memory and the process restarted is an avoidable failure mode. The storage layer prevents it.

You are not building an optimized database. You are building a working one that is simple enough that you never have to debug it under pressure.

**The storage approach:**

SQLite. One file. Python's built-in sqlite3 module. No ORM, no migration framework, no connection pooling. Plain SQL queries for everything. The reason for plain SQL over an ORM is that ORMs add a debugging layer between you and the database that you cannot afford to navigate during a hackathon. When something is wrong with a plain SQL query, you can read the query and fix it. When something is wrong with ORM-generated SQL, you are reading framework internals.

**The tables you need and what lives in each one:**

---

**Table: source videos**

Stores the raw catalog input — one row per video.

What gets stored: all fields from the Source Video model. The performance block and thumbnail block are stored as JSON text in a single column each rather than being normalized into separate tables. The reason is that you never need to query individual performance fields in isolation — you always load the whole video object. Normalizing them adds join complexity with zero query benefit for this use case.

What gets indexed: creator ID, so you can efficiently load all videos for one creator when the DNA agent runs.

---

**Table: creator profiles**

Stores one profile per creator. Gets overwritten each time the DNA agent runs on updated catalog data.

What gets stored: the creator ID as the primary key, and the entire profile object as JSON text in a single column. The reason for storing the whole profile as JSON rather than breaking it into columns is that the profile structure is deeply nested and reading the whole object is always the access pattern — you never query for just the tone field or just the title formula.

What gets indexed: creator ID as primary key, which makes lookup by creator ID instant.

---

**Table: pipeline runs**

Stores one row per pipeline execution. Append-only — runs are never updated except to set their completed timestamp and final status.

What gets stored: run ID, creator ID, started timestamp, completed timestamp (nullable), status, current stage, opportunity ID (nullable until selected), asset ID (nullable until generated), stages completed as a JSON array, stages failed as a JSON array, total duration (nullable until complete), total LLM calls count, and regeneration count.

What gets indexed: run ID as primary key, creator ID for retrieving all runs for a creator.

---

**Table: content opportunities**

Stores one row per recommended opportunity. Multiple opportunities can exist per run — the opportunity agent generates three and the orchestrator selects one.

What gets stored: opportunity ID, creator ID, pipeline run ID, and the full opportunity object as JSON text. Also stores the status field as a separate column rather than buried in the JSON, because you will query opportunities by status (pending, approved, in production) and querying inside JSON text is painful.

What gets indexed: opportunity ID as primary key, creator ID, pipeline run ID, status.

---

**Table: generated assets**

Stores one row per generated content package.

What gets stored: asset ID, creator ID, pipeline run ID, opportunity ID, and the full asset object as JSON text. Also stores render status as a separate column for the same reason status is a separate column on opportunities — you will query it.

What gets indexed: asset ID as primary key, pipeline run ID, opportunity ID.

---

**Table: decision log entries**

Stores one row per decision log entry. Strictly append-only — entries are never updated or deleted.

What gets stored: entry ID, pipeline run ID, creator ID, timestamp, stage, status, decision text, rationale text, input summary, output summary, and score (nullable float). The reason these fields are stored as individual columns rather than as a single JSON blob is that the decision log panel in the UI needs to render each field separately, and you will query this table filtered by pipeline run ID and ordered by timestamp — both of which are indexed column queries, not JSON extraction.

What gets indexed: entry ID as primary key, pipeline run ID (you always load all entries for one run), creator ID, timestamp (for ordering).

---

**The initialization sequence:**

When the backend starts, before it accepts any requests, it runs the database initialization routine. This routine checks whether each table exists and creates it if it does not. It never drops and recreates tables — that would destroy data on every restart. It only creates tables that do not already exist. This means you can restart the backend during development without losing your seed data or your test runs.

**What "done" looks like for Step 2:**

You can start the backend and the database file is created automatically. You can write a record to each table using direct function calls (not through the API yet). You can read it back. You can restart the backend and the data is still there. Every table exists with the right columns. No data is lost on restart.

---

## Phase 1 — Step 3: Create the API Skeleton With Stub Responses

**What this step is about:**

Now you wire up every endpoint the system needs, but none of them contain real logic yet. Every endpoint returns hardcoded fake data that matches the exact shape of the real data it will eventually return. The purpose is twofold: first, you prove that the routing, CORS configuration, and request/response plumbing all work correctly before any complex logic is involved. Second, you give the frontend a surface to build against immediately — the frontend does not have to wait for Phase 2 or Phase 3 to start working.

The stub responses are not throwaway work. They are the specification of what each endpoint will eventually return, written in concrete form. Every field in a stub response should be a realistic example, not a trivial placeholder. If a field will eventually be a quality score float between 0 and 1, the stub should return 0.84, not 1 or 0 or null. If a field will eventually be a three-sentence rationale, the stub should return a three-sentence rationale about the fake creator, not the string "rationale goes here."

The reason for realistic stubs is that the frontend developer — who is also you — needs to build real UI against this data. A frontend built against a stub that says "text here" will need to be rebuilt when the real data arrives. A frontend built against a stub that looks exactly like real data will work correctly when the real data arrives.

---

**The endpoints you are building and what each stub should return:**

---

**POST /catalog/ingest**

What it will eventually do: accept a batch of Source Video objects and store them.

What the stub does: accepts whatever JSON body is sent, ignores it, and returns a hardcoded success response saying 8 videos were ingested for creator_001.

Why the stub matters: the frontend Setup page needs to show a success confirmation after catalog upload. The stub lets that be built and tested immediately.

---

**POST /profile/build**

What it will eventually do: run the DNA agent and return a CreatorDNAProfile.

What the stub does: accepts a creator ID in the request body and returns a hardcoded CreatorDNAProfile for that creator — a complete, realistic profile for the fake productivity creator from the seed data. Every field filled in with realistic content, not placeholders.

Why the stub matters: the frontend needs to display the creator profile summary. The stub gives it real-looking data to render against.

---

**GET /profile/{creator_id}**

What it will eventually do: retrieve the stored profile for a creator.

What the stub does: for creator_001, returns the same hardcoded profile as the profile build endpoint. For any other creator ID, returns a 404 with a clear message.

---

**POST /content/recommend**

What it will eventually do: run the opportunity agent and return three content recommendations.

What the stub does: returns a hardcoded list of three ContentOpportunity objects for the fake creator, each with realistic topics, working titles, rationales, and fit scores. The fit scores should be different — for example 0.87, 0.71, and 0.58 — so the UI can show that they are ranked.

Why the stub matters: the dashboard's opportunity selection UI needs realistic recommendation cards to render against.

---

**POST /content/generate**

What it will eventually do: run the script agent, thumbnail agent, and metadata agent in sequence.

What the stub does: accepts an opportunity ID and returns a hardcoded GeneratedAsset object with a complete script (hook, three scenes, outro), three thumbnail variant descriptions (SVG source can be a short valid SVG string, PNG path can point to a placeholder image), and complete metadata with a realistic title, description, and tags. Video block shows render status as pending.

---

**POST /content/score**

What it will eventually do: run the scorer agent and return a quality score.

What the stub does: this is the most important stub to make realistic. Return two different responses based on a flag in the request or just alternate between runs. First response: passed is false, overall score is 0.62, rejection reason is a specific explanation citing the thumbnail's background type not matching the creator profile. Second response: passed is true, overall score is 0.81, all dimension scores are realistic. This lets the frontend DecisionLog component be built to show both rejection and success states.

---

**GET /pipeline/{run_id}/status**

What it will eventually do: return the current status of a running pipeline for the progress indicator to poll.

What the stub does: for a hardcoded run ID, returns a status of running with current stage as script agent, stages completed as DNA agent and opportunity agent, and a progress percentage of 40. For any other run ID, returns a status of complete with all stages listed in stages completed and 100 percent.

---

**POST /pipeline/run**

What it will eventually do: run the entire pipeline end to end and return everything.

What the stub does: this is the most important endpoint to stub carefully. It returns a complete PipelineRun object that includes the selected opportunity, the full generated asset, and a complete decision log with at least eight entries. The decision log entries must include at minimum: one DNA agent entry, one opportunity agent entry showing three candidates and the selected one with rationale, one script agent entry, one thumbnail agent entry, one metadata agent entry, one scorer entry showing a rejection with reason, one regenerate entry, and one final scorer entry showing a pass. This full set of fake entries is what the frontend builds the decision log timeline against.

---

**POST /content/publish**

What it will eventually do: push the asset to YouTube or another platform.

What the stub does: accepts an asset ID and platform and returns a hardcoded platform post ID, a fake YouTube URL, and a status of scheduled.

---

**GET /output/video/{filename}**

What it will eventually do: serve the rendered MP4 file.

What the stub does: returns a 404 for now with a message that video rendering is not yet implemented. The frontend VideoPreview component should handle a 404 from this endpoint gracefully by showing a placeholder.

---

**GET /output/thumbnail/{filename}**

What it will eventually do: serve a rendered PNG thumbnail.

What the stub does: returns a simple placeholder PNG — either a 1x1 pixel PNG or a small colored square — so the frontend ThumbnailPicker component has something to render and the image tag does not break.

---

## Phase 1 — Step 4: Configure CORS and Error Handling

**What this step is about:**

CORS and error handling are not exciting but skipping them guarantees specific, painful failures at specific moments. CORS breaks the moment you open the frontend on a different port than the backend — which is always, because Vite runs on 5173 and FastAPI runs on 8000. Error handling determines whether a failed agent call during Phase 2 produces a readable error message in the frontend or a generic 500 that tells you nothing.

**CORS configuration:**

The backend needs to explicitly allow requests from the frontend's development origin. For Vite, that origin is http://localhost:5173. The configuration needs to allow all the HTTP methods the frontend uses (GET, POST, OPTIONS), allow the Content-Type header, and allow credentials if you end up using any session-based authentication (unlikely for this project, but set it permissively now to avoid fighting it later).

The CORS configuration should be wide open for the local development environment. This is a hackathon — security hardening is not in scope. If someone asks about it, you acknowledge it and explain it would be tightened for production.

**Error handling approach:**

Every endpoint needs consistent error handling that follows the same shape. The shape is: status (either "success" or "error"), message (a human-readable description of what went wrong), and optionally a detail field for technical information useful during debugging.

The error handling needs to cover four specific cases:

The first case is a validation error — the request body does not match what the endpoint expects. This should return a 422 status code with a message that says exactly which field failed validation and why. The data models from Step 1 handle most of this automatically if the framework validates incoming request bodies against the models.

The second case is a not-found error — a request references a creator ID, run ID, or asset ID that does not exist in the database. This should return a 404 with a message that names specifically what was not found.

The third case is an internal error — an agent call fails, the database throws an exception, a file operation fails. This should return a 500 with a message that describes what failed, not a generic "internal server error." During a hackathon demo, if something breaks you need to know from the frontend response what broke, not have to go read server logs.

The fourth case is a timeout — agent calls take real time and if they exceed a limit, the request should fail cleanly rather than hang indefinitely. Set a generous timeout (60 seconds per agent call) so normal operation is never affected, but cap it so a stalled call does not freeze the demo.

**What "done" looks like for Steps 3 and 4:**

You open a REST client. You hit every endpoint listed above. Every one returns a sensible response — either a realistic fake success response or, for the not-found cases, a clear 404. You open the frontend (even if it is just a blank page at this point) and make a fetch call to one of the endpoints. It succeeds without a CORS error. You send a malformed request body to the catalog ingest endpoint. It returns a 422 with a readable explanation of what was wrong, not a 500.

---

## Phase 1 — Step 5: Verify the Seed Data Loads Correctly

**What this step is about:**

The 8 seed videos from Phase 0 Step 11 exist in plain text. In this step you convert them into proper structured data and verify that they pass validation through the Source Video model and load cleanly into the database. This is the first time the models, the storage layer, and real data interact with each other. Any mismatch between what the seed data provides and what the models require shows up here, where it is cheap to fix.

**What you are doing:**

You take the 8 seed video descriptions from Phase 0 and write them out as properly structured Source Video objects — with every field populated, every nested object present, every field type correct. You then run these through the catalog ingest endpoint (which is still a stub, so you are actually calling the storage layer directly in a test script) and verify that all 8 are stored successfully.

After storing them, you read them back and verify that what you get back matches what you put in. No fields dropped, no types coerced incorrectly, no nulls appearing where you put real values.

Then you run the mathematical calculations for the performance benchmarks: average views, average CTR, average retention, top quartile threshold, and bottom quartile threshold. You calculate these from the seed data numbers and record the results. These calculated values will be passed to the DNA agent as part of its input context in Phase 2, not generated by the LLM.

**Why this step matters:**

The seed data is what every agent is tested against during Phase 2. If the seed data has any structural problems — a null where a string is required, a float where an integer is required, a missing nested object — the DNA agent will fail or produce degraded output, and the failure will look like an agent problem when it is actually a data problem. Verifying the seed data against the models now, before any agent exists, means agent failures in Phase 2 are actually agent failures.

**What "done" looks like for Step 5:**

All 8 seed videos are stored in the database. You can retrieve them all by creator ID with a single query. Every model validation passes on load. The five performance benchmark calculations are written down and ready to be included in the DNA agent's prompt context.

---

## Phase 1 — Step 6: The Done Definition for Phase 1

Phase 1 is complete when all of the following are true simultaneously.

Every data model validates correctly — valid data passes, invalid data fails with a readable message, for every model.

Every database table exists and persists across backend restarts. You can write and read every object type. No data is lost on restart.

Every endpoint returns a sensible response from a REST client. The pipeline/run endpoint returns a complete fake response including a full decision log with rejection and regeneration entries visible.

CORS is configured and a fetch call from the frontend's port to the backend's port succeeds without a browser CORS error.

Error responses follow a consistent shape and the four error cases return the right status codes with readable messages.

All 8 seed videos are stored in the database and pass model validation. The five performance benchmark numbers are calculated and recorded.

The frontend can begin building against the stub API responses immediately without waiting for any Phase 2 or Phase 3 work to complete.

---

*Phase 1 produces no AI logic, no rendered media, and no real intelligence. It produces a stable, tested, contract-complete foundation that every later phase builds on without negotiating with any other phase about shapes, fields, or behavior.*