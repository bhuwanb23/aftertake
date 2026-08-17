# Phase 2 — AI Agent Layer

---

## What Phase 2 Is and Why It Is the Core of the Entire Project

Phase 2 is where the actual differentiation of Creator Twin gets built. Everything in Phase 1 was infrastructure. Everything in Phase 3 onwards is execution. Phase 2 is the intelligence — the part that makes this project meaningfully different from every comparable tool that already exists.

The goal of Phase 2 is narrow and specific: each agent works correctly in complete isolation, tested with real inputs, producing correctly shaped and genuinely personalized output, before any agent is connected to any other agent. You do not chain agents together in this phase. You do not wire agents into the API in this phase. You build one agent, you test it thoroughly until it is reliable, and only then do you move to the next one.

The reason for strict isolation is that when agents are chained and something produces wrong output, you cannot tell which agent is responsible. When each agent is tested alone with known inputs, a wrong output has exactly one possible source — the agent you are currently working on.

There are five agents to build in this phase, in this order, and the order is not arbitrary. Each agent depends on the output of the previous one being correct, so you get the foundational one right first before building anything that depends on it.

---

## Phase 2 — Step 1: Establish the Agent Development Environment and Discipline

**What this step is about:**

Before writing any agent, you establish the practices that every agent in this phase follows. These are not optional refinements — they are the practices that determine whether you spend your time building or debugging. Establishing them once here means every agent benefits from them automatically.

---

**Practice 1: Every Agent Is Tested in Isolation Using a Standalone Test Script**

You do not test agents through the API. You do not test agents by running the full pipeline. For each agent, you write a small standalone script — not a formal test suite, just a script you can run directly — that calls the agent with real input data and prints the output. This script is how you develop the agent. You run it repeatedly, read the output, adjust the prompt, run it again. The API integration happens in Phase 4. Right now, isolation is the entire point.

The test script for each agent follows the same pattern: load the input data (from the seed data files or from the output of a previously tested agent), call the agent function, print the raw response, validate the response against the Phase 1 schema, print the validation result. If validation fails, print exactly which fields failed and why.

---

**Practice 2: Force Structured JSON Output From Every Agent**

Every agent receives a system prompt that instructs it to respond only with a valid JSON object and nothing else. No preamble, no explanation, no "here is the JSON you requested," no markdown code fences around the JSON — just the raw JSON object. The reason is that any text outside the JSON object requires parsing logic that can fail, and parsing failures produce errors that look like agent failures when they are actually prompt failures.

The system prompt for every agent ends with an instruction in this form: "Respond with only a valid JSON object. Do not include any text before or after the JSON. Do not wrap the JSON in markdown code fences. Do not include any explanation of your response."

After every agent call, before doing anything else with the response, you parse the response as JSON. If it does not parse, you log the raw response and surface the error. You do not try to extract JSON from surrounding text — if the output is not parseable JSON, the prompt needs to be fixed.

---

**Practice 3: Validate Every Response Against the Phase 1 Schema Immediately**

After JSON parsing succeeds, you immediately validate the parsed object against the corresponding Phase 1 Pydantic model. This catches shape drift — the situation where the JSON parses correctly but the fields are named differently than expected, or a required field is missing, or a field has the wrong type. Shape drift caught here costs you one prompt iteration. Shape drift caught in Phase 4 when you are trying to wire agents together costs you an hour of tracing which layer broke things.

---

**Practice 4: Log Every Raw LLM Response During Development**

Every agent call during Phase 2 logs the raw response text to a local log file before doing anything else with it. The log entry includes the timestamp, the agent name, the model used, the input summary, and the full raw response. The reason is that LLM calls cost money and take time. If an agent produces a bad output and you do not have the raw response logged, you have to run it again to see what went wrong. With the log, you can debug the previous run without spending another API call.

The log does not need to be sophisticated — a plain text file with appended entries is sufficient. The important thing is that it exists and that you consult it before re-running when something looks wrong.

---

**Practice 5: One System Prompt Per Agent, in Its Own Dedicated File**

The system prompt for each agent lives in a text file and is loaded at runtime. It is never hardcoded as a string inside the agent's logic. The reason is that you will iterate on prompts many times in this phase. If the prompt is hardcoded, every iteration requires touching the agent code, which risks accidentally breaking something else. If the prompt is in a file, you edit the file, rerun the test script, and nothing else is touched.

Every system prompt file follows the same structure: a role definition that tells the model exactly what it is and what it does, a detailed description of the task it must perform, a specification of every field it must include in its output and what each field means, explicit instructions about what to avoid, and the JSON-only output instruction at the end.

---

**Practice 6: Run Each Agent 5 to 10 Times Before Declaring It Done**

LLMs are non-deterministic. An agent that produces correct output once may produce a malformed output on the third run. Before declaring any agent done and moving to the next, you run it at least 5 times with the same input and at least 3 times with different inputs. If any run produces invalid JSON or a schema validation failure, the agent is not done. If every run produces correctly shaped output but some runs produce noticeably worse quality than others, the prompt needs tightening before you move on.

The threshold for "done" is not "it worked once." It is "I have run it enough times with varied inputs that I am confident it will not fail in unexpected ways during Phase 4 integration."

---

## Phase 2 — Step 2: Build the DNA Agent (Creator Style Learning Agent)

**What this agent does:**

The DNA agent is the foundational agent of the entire system. It takes the batch of Source Video objects from the seed catalog and produces a CreatorDNAProfile. This profile is the input to every other agent in the system. If this agent produces a wrong, weak, or vague profile, every downstream agent produces wrong, weak, or vague output — and the failure is hard to diagnose because it looks like the downstream agent's fault.

Get this agent right before touching anything else. Test it more thoroughly than any other agent. Its output shape and output quality are the foundation everything else stands on.

---

**What the DNA agent receives as input:**

The agent receives two things. First, the list of 8 Source Video objects from the seed catalog — the full structured data including titles, transcripts, thumbnail descriptions, and performance numbers. Second, the pre-calculated performance benchmarks: average views, average CTR, average retention, top quartile threshold, and bottom quartile threshold. These benchmarks are calculated in Python from the performance numbers before the prompt is sent — the LLM does not calculate them, it receives them as facts.

The reason the benchmarks are calculated outside the LLM is that LLMs are unreliable at arithmetic on specific numbers. If you ask the model to calculate the average of 8 view counts, it may get it wrong. The average of those same 8 view counts calculated in Python is always correct. By the time the model sees the input, it sees "average views across catalog: 226,625" as a fact, and it reasons about that fact rather than deriving it.

---

**What the DNA agent must produce:**

A complete CreatorDNAProfile object as defined in Phase 0 Schema 2 and validated by the Phase 1 model. Every field populated. No nulls in required fields. The quality of the content in each field matters as much as the structure.

The specific quality bar for each section:

The voice section must describe this specific creator's patterns — not generic content creator advice. "Conversational and direct" is acceptable only if it is followed by specific evidence from the transcripts that demonstrates it. "Uses short punchy sentences, typically 10-15 words per beat, frequently uses pauses after bold claims before elaborating" is the level of specificity required. Vague voice descriptions produce vague scripts in Phase 2 Step 5.

The title formula section must identify the actual pattern from the specific titles in the catalog, not a generic YouTube title formula. The structure field should describe the template that the high-performing titles in this specific catalog follow — "Number + Specific Timeframe + Honest Qualifier (Actually, Honest)" not just "Number + Topic + Outcome."

The thumbnail style section must reference what is actually visible in the thumbnail descriptions in the catalog. "Solid color backgrounds (red, dark blue, orange, black) — never blurred or abstract" is derived from the actual data. "Bold white all-caps text, 2-4 words, with black outline" comes from reading the descriptions. The model must synthesize these descriptions into a pattern, not hallucinate a generic style.

The content patterns section must reflect the actual formats present in the catalog and the actual correlation between format and performance. The model should observe that 30-day challenge format and listicle format consistently appear in high performers, while tour format and vague-topic format appear in low performers — and say so explicitly.

The performance benchmarks section must contain the exact numbers that were passed in as pre-calculated facts. If you passed in average views of 226,625 and the model returns 220,000, the prompt needs to instruct it more explicitly to use the provided numbers verbatim.

---

**How to write the DNA agent system prompt:**

The system prompt needs to accomplish several things in sequence.

First, it establishes the role: the model is a content analytics expert whose job is to study a specific creator's catalog and extract a detailed, evidence-based profile of their style, patterns, and performance correlations.

Second, it describes the task precisely: analyze the provided catalog of videos, including their performance data, titles, transcript samples, and thumbnail descriptions. Identify patterns that distinguish high-performing content from low-performing content for this specific creator. Extract the creator's consistent voice patterns, title formula, thumbnail style, and content format preferences.

Third, it provides explicit instructions for what makes a good profile output — specifically, that every observation must be traceable to the catalog data. If the model claims the creator uses a specific hook pattern, there should be evidence of it in the transcripts. If the model claims a certain thumbnail style correlates with high performance, there should be evidence of it in the performance data. The model should not insert generic "best practices" — it should only report what is actually present in this creator's catalog.

Fourth, it specifies the output format field by field, with the expected content type and any constraints for each field.

Fifth, it ends with the JSON-only output instruction.

---

**How to test the DNA agent:**

Run 1: Full catalog input, all 8 videos. Verify the output JSON parses. Verify it passes schema validation. Read the voice section — does it describe patterns you can actually see in the seed data transcripts? Read the thumbnail style section — does it accurately reflect what the thumbnail descriptions say? Read the content patterns section — does it correctly identify that challenge and listicle formats outperform tour and vague-topic formats?

Run 2: Same input. Compare to Run 1. Are the same patterns identified? The specific wording will differ but the substance should be consistent — the same voice patterns, the same title formula structure, the same thumbnail elements.

Run 3: Input only the 4 high performers. Does the profile shift to emphasize the patterns that characterize those videos more strongly? It should.

Run 4: Input only the 4 low performers. Does the profile change significantly? It should — it should describe a creator who uses vague titles, abstract thumbnails, and long format videos.

Run 5: Full catalog again. Does the output look more like Run 1/2 than Run 3/4? It should, because the high performers are a stronger signal when the full context is available.

If Runs 1 and 2 produce inconsistent assessments of the same creator, the prompt is not specific enough about what to look for and the model is making different judgment calls each time. Tighten the prompt to be more directive about which signals to prioritize.

---

**What "done" looks like for the DNA agent:**

Five runs on the full seed catalog all produce correctly shaped JSON that passes schema validation. The voice section in each run consistently identifies the same core patterns (first-person framing, specific numbers, short punchy sentences). The title formula consistently identifies the "I [did X] for [Y timeframe]" structure and the number-led list format. The thumbnail style consistently identifies solid color backgrounds, bold all-caps white text, and prominent creator face with strong emotion. The content patterns section consistently identifies challenge and comparison formats as high performers and tour/vague formats as low performers. The performance benchmarks match the pre-calculated numbers exactly.

---

## Phase 2 — Step 3: Build the Opportunity Agent (What to Make Next Agent)

**What this agent does:**

The opportunity agent takes the CreatorDNAProfile produced by the DNA agent and a static list of current trends in the creator's niche, and recommends three next-video opportunities. Each opportunity includes a topic, a working title written in the creator's title formula, a detailed rationale, a fit score, and a recommended format and duration.

The critical requirement for this agent — the one that makes Creator Twin different from every comparable tool — is that the rationale must explicitly reference the creator's specific profile attributes. If the rationale says "this is a trending topic in the productivity space" without connecting that trend to anything specific about this creator's established style and performance history, the agent has failed its core purpose.

---

**What the opportunity agent receives as input:**

The CreatorDNAProfile from the DNA agent. A static trends list — for the hackathon, this is a hardcoded JSON file containing 10 to 15 current topic areas in the productivity and tech niche. Examples of what goes in this list: AI tools for productivity is heavily searched in the last 60 days, Notion AI features have had three major updates in the past month, remote work tool comparisons are performing strongly on the platform, morning routine experiments are spiking in search volume. This list does not require a live API — it is research you do once and encode as seed data.

---

**What the opportunity agent must produce:**

Three ContentOpportunity objects. Not one, not five — exactly three, so the dashboard can show a ranked set of options and the orchestrator can select the strongest one. Each opportunity must be a complete ContentOpportunity object as defined in Phase 0 Schema 3.

The quality bar for the rationale is the most important quality bar in this entire phase. The rationale's DNA fit explanation must cite specific fields from the profile. Not "this fits your style" — that is unacceptable. The acceptable form is: "This maps directly to your highest-performing format (your content_patterns.format_preferences ranks 30-day-challenge first) and your best-performing topic category (your content_patterns.best_performing_topics includes productivity app comparisons). The working title follows your established title_formula.structure of first-person specific-timeframe framing. The comparison element satisfies what your profile identifies as your audience's expectation for definitive answers."

This level of specificity is the proof of concept that the system has learned from the creator's data, not just generated generic content advice. If a judge reads this rationale, they should be able to trace every claim back to a field in the creator profile.

The fit score must be meaningful and differentiated across the three opportunities. If all three opportunities return a fit score of 0.85, the scoring is not calibrated and the model is treating the score as a formality. The three scores should reflect real differences — perhaps 0.87, 0.71, and 0.58 — where the differences are explained by how well each opportunity matches the profile.

The working title for each opportunity must be generated following the creator's title formula, not just a generic YouTube title. If the creator's formula is first-person + specific timeframe + honest qualifier, the working title should follow that formula. The metadata agent will refine this later, but the working title should already demonstrate the formula.

---

**How to write the opportunity agent system prompt:**

The system prompt provides the full CreatorDNAProfile as context. It instructs the model to use this profile as the primary filter for evaluating whether a topic is right for this creator — not whether the topic is generally popular, but whether it fits this specific creator's established patterns and performance history.

It instructs the model to generate exactly three opportunities, ranked by fit score in descending order. It provides the trends list as additional context that the model can use as raw material but is not required to use — the profile is the primary filter.

It specifies the quality standard for rationales explicitly: every rationale must cite the specific profile fields that support the recommendation. The model should not make claims about the creator's style that are not supported by the profile it received.

It specifies the fit score calibration: a score of 0.9 means the topic matches nearly every relevant attribute in the creator's profile and mirrors their best-performing content almost exactly. A score of 0.7 means the topic fits some core attributes but has gaps. A score of 0.5 means the topic has some relevance but meaningful mismatches. The model should not cluster scores near 0.8 to avoid commitment — differentiated scores are required.

---

**How to test the opportunity agent:**

Run 1: Full DNA profile as input, full trends list. Verify JSON parses and schema validates. Read the rationale of the highest-scoring opportunity — count how many specific profile fields it references. If the answer is zero, the prompt needs to instruct more explicitly that profile fields must be cited by name.

Run 2: Same inputs. Are the same three topics recommended, or significantly different ones? Some variation is expected but the top recommendation should be similar across runs if the profile clearly points in one direction.

Run 3: Manually modify the DNA profile to describe a very different creator — one who does comedy content with bright colors and no educational value. Does the opportunity agent recommend dramatically different topics? It should. If the agent recommends productivity tools for a comedy creator, it is not actually conditioning on the profile.

Run 4: Remove the trends list from the input. Does the agent still produce sensible recommendations based purely on the profile? It should — the trends list is supplementary, not required.

Run 5: Read every rationale carefully. Does any rationale contain advice that would be equally applicable to any content creator? If yes, that rationale has failed and the prompt needs to be more directive about specificity.

---

**What "done" looks like for the opportunity agent:**

Five runs all produce exactly three opportunities with correctly shaped JSON passing schema validation. The fit scores are differentiated — the range between highest and lowest should be at least 0.2. The rationale for the top opportunity in every run explicitly cites at least three specific fields from the creator profile. Modifying the creator profile produces meaningfully different recommendations. The working titles follow the creator's title formula.

---

## Phase 2 — Step 4: Build the Thumbnail Agent (Visual Asset Generation Agent)

**What this step is about:**

The thumbnail agent is built before the script agent because it has no dependency on the script — it only needs the opportunity and the creator profile. Building it here, before the script agent, means you have something to show visually early, and the thumbnail rendering pipeline (which is part of Phase 3) can be tested in parallel once this agent is producing SVG output.

**What the thumbnail agent does:**

The thumbnail agent takes one ContentOpportunity and the CreatorDNAProfile and generates 2 to 3 SVG thumbnail layouts. Each SVG follows the creator's learned thumbnail style — the colors, layout pattern, text style, and compositional elements from the profile. Alongside each SVG, the agent writes a plain English description of what the thumbnail shows.

---

**What the thumbnail agent must produce:**

A list of 2 to 3 ThumbnailVariant objects. Each variant contains the SVG source markup and a layout description. The PNG path is null at this stage — the rendering step in Phase 3 fills that in.

The SVG markup must be genuinely renderable. This is the most specific technical constraint in this agent. The SVG must use only standard SVG elements — rect, text, circle, line, path, image (for placeholders), g for grouping. It must have explicit width and height attributes (1280x720 for a standard YouTube thumbnail ratio). All colors must be valid SVG color values — hex codes, RGB, or named colors. All text elements must have explicit x, y, and font-size attributes. The SVG must close all tags properly.

The reason for this specificity in the prompt is that LLMs generating SVG often produce markup that looks correct but fails to render — unclosed tags, invalid color values, missing required attributes. The system prompt needs to be explicit about every one of these constraints to minimize rendering failures in Phase 3.

The creator's thumbnail style from the DNA profile must be directly reflected in the SVG output:
- If the profile specifies solid color backgrounds, the SVG background must be a solid color rect, not a gradient or pattern
- If the profile specifies bold all-caps white text with black outline, the SVG text elements must use a large font size, uppercase transform, white fill, and a black stroke
- If the profile specifies creator face on the left half with text on the right, the layout must follow that spatial arrangement — even if the creator face is represented as a placeholder rectangle, the spatial relationship must be correct
- If the profile specifies dominant colors of red, white, and black, those colors must appear in the SVG — not a random palette

Each variant should explore a different interpretation of the style, not be three nearly identical thumbnails. Variant 1 might use the creator's highest-frequency layout exactly. Variant 2 might try a different color from the dominant palette. Variant 3 might emphasize the text differently. They should be recognizably from the same visual style family but meaningfully different from each other.

---

**How to write the thumbnail agent system prompt:**

The system prompt provides the thumbnail_style section of the CreatorDNAProfile explicitly and instructs the model to treat it as the design brief. Every design decision in the SVG should trace back to a field in the thumbnail style.

It provides the topic and working title from the ContentOpportunity so the thumbnail text reflects the actual content.

It specifies the technical SVG requirements with the same level of detail described above — dimensions, required attributes, valid color formats, proper tag closure.

It instructs the model to generate exactly 3 variants and to make each one a meaningfully different interpretation of the style, not three copies of the same layout.

It reminds the model that the creator's face is represented as a placeholder rectangle in the SVG — the actual creator image is inserted at publish time. The placeholder rectangle should be positioned and sized according to the layout_pattern from the profile.

---

**How to test the thumbnail agent:**

Run 1: Full DNA profile and the top opportunity from the opportunity agent as input. Verify JSON parses and schema validates. Take the SVG source from the first variant and paste it into an online SVG viewer (svgviewer.dev or similar). Does it render without errors? Does it look like it follows the creator's thumbnail style?

Run 2: Attempt to render all 3 variants. Do all three render? Do they look visually distinct from each other?

Run 3: Read the layout descriptions. Does each description accurately describe what the SVG actually renders? The scorer agent in Step 6 will evaluate thumbnails partly by reading these descriptions, so they need to be accurate.

Run 4: Check that the text in each thumbnail reflects the actual video topic — not generic placeholder text.

Run 5: Verify that the colors in the SVGs match the creator's dominant_colors from the profile. If the profile says red, white, and black and the SVG is using green and purple, the prompt is not conditioning on the style correctly.

Critical test — run this deliberately: Generate thumbnails and check whether any of them use a blurred or abstract background. The seed creator's profile explicitly identifies these as low-performance signals. If the thumbnail agent generates blurred backgrounds, it is not reading the profile correctly and the prompt needs to be more explicit about what the background_type constraint means.

---

**What "done" looks like for the thumbnail agent:**

Five runs all produce 3 thumbnail variants with correctly shaped JSON passing schema validation. All SVG markup renders without errors in an SVG viewer. The rendered thumbnails visually follow the creator's thumbnail style — solid color backgrounds, bold all-caps text, placeholder creator face in the correct position. Each variant is meaningfully different from the others. The layout descriptions accurately describe what is in the SVG.

---

## Phase 2 — Step 5: Build the Script Agent (Content Generation Agent)

**What the script agent does:**

The script agent takes one ContentOpportunity and the CreatorDNAProfile and writes a complete video script in the creator's learned voice. The script includes a hook, a set of scenes, and an outro. Every section is written as if the creator themselves wrote it — using their vocabulary, their pacing, their hook pattern, and their structural preferences.

This is the agent where the voice learning from the DNA agent produces its most visible output. A judge reading the script should be able to see that it sounds like the specific creator from the seed catalog, not like a generic AI script.

---

**What the script agent must produce:**

A complete Script object as defined in Phase 0 Schema 4. Every section required. Every scene with a scene type that maps to a valid HyperFrames template type.

The quality bar for this agent is about voice consistency:

The hook must follow the creator's hook_pattern from the profile. If the profile says the creator always opens with a provocative question or a bold personal claim within the first 8 seconds, the hook must do exactly that. Not a greeting. Not a "today we're going to talk about." A provocative question or bold claim, immediately.

The vocabulary must match the vocabulary_level from the profile. If the profile says the creator uses everyday language, avoids jargon, and uses specific numbers wherever possible, the script should demonstrate all three. Not "we'll explore the ecosystem of productivity tooling" — that is jargon. "I tested 5 tools for 30 days and here's the number that surprised me" — that is the correct register.

The signature phrases from the profile should appear naturally in the script. Not forced in at arbitrary points, but where they would actually fit. If the creator says "here's the thing" as a transition, the script should use it as a transition, not as an opener or closer.

The what_to_avoid list from the profile should visibly influence the script. If the profile says the creator never uses passive voice, the script should not contain passive voice. If the profile says the creator avoids inspirational quotes, the script should not contain any. These negative constraints are as important as the positive ones.

The scene types must be chosen to serve the content. A listicle about 5 tools needs list_reveal scenes for the reveals. A comparison video needs comparison_split scenes. The scene types are not decorative — they map to actual HyperFrames rendering templates in Phase 3, so choosing the right scene types here makes Phase 3 easier.

The estimated duration should fall within the optimal_duration_range from the creator profile. If the profile says 4 to 7 minutes (240 to 420 seconds), the sum of all scene durations should be within that range.

---

**How to write the script agent system prompt:**

The system prompt provides the full voice section of the CreatorDNAProfile and instructs the model to write the script as if it were written by this specific creator — not as a generic content creator, not as an AI assistant, but as someone who naturally speaks in this voice.

It provides the ContentOpportunity including the topic, working title, recommended format, recommended duration, and target hook. The script should serve the opportunity, not deviate from it.

It provides the scene_type vocabulary explicitly — the list of allowed values — and instructs the model to choose scene types that serve the content structure.

It instructs the model that the hook must follow the hook_pattern from the voice profile and that the first line of the hook should not contain any greeting.

It provides the signature_phrases list and instructs the model to use them where natural, not to force them in.

It provides the what_to_avoid list and frames it explicitly as a prohibition: these patterns must not appear anywhere in the script.

It specifies the duration constraint: the sum of all scene durations must fall within the optimal_duration_range from the profile.

---

**How to test the script agent:**

Run 1: Full DNA profile and top opportunity as input. Verify JSON parses and schema validates. Read the hook — does it open with a provocative question or bold claim? Does it avoid a greeting? Does it match the register of the seed data transcripts?

Run 2: Read the full_voiceover_text as if you were the creator speaking it aloud. Does it sound like someone who could have written the seed data transcripts? If it sounds formal or generic, the voice conditioning is not working.

Run 3: Check the what_to_avoid list from the profile against the script text. Are any prohibited patterns present? If yes, the prompt needs to be more explicit about these as hard constraints, not suggestions.

Run 4: Sum the scene durations. Does the total fall within the optimal_duration_range? If a script consistently runs long or short, the prompt needs to include the duration constraint more prominently.

Run 5: Check the scene types. Are they all valid values from the allowed set? Do the chosen scene types actually serve the content — for example, does a tool comparison video use comparison_split scenes for the comparison moments?

---

**What "done" looks like for the script agent:**

Five runs all produce correctly shaped JSON passing schema validation. The hook never opens with a greeting and always uses the creator's established hook pattern. The voice is recognizably consistent with the seed data transcripts. No prohibited patterns from the what_to_avoid list appear. Scene types are all valid values. Estimated duration falls within the creator's optimal range.

---

## Phase 2 — Step 6: Build the Metadata Agent (Title, Description, Tags Agent)

**What the metadata agent does:**

The metadata agent takes the Script object and the CreatorDNAProfile and generates the publishing metadata: the final title, the video description, and the tags. The title must follow the creator's title formula exactly. The description must match the creator's voice. The tags must be relevant and appropriately sized.

This is the shortest agent to build in this phase but one of the most visible — the title is the first thing a viewer and a judge sees.

---

**What the metadata agent must produce:**

A complete Metadata object as defined in Phase 0 Schema 6. The most important field is the title_formula_match — the agent's own explanation of how the title it generated maps to the creator's formula. This field is evaluated by the scorer agent in the next step and displayed in the decision log. If the metadata agent cannot explain how the title follows the formula, the title probably does not follow it.

The title quality bar: it must follow the title_formula.structure from the profile. For the seed creator, the structure is first-person + specific timeframe + honest qualifier, or number + specific outcome. The title must use the right capitalization pattern (uses_caps from the profile), must hit the average word count (within plus or minus 2 words of avg_word_count), and must employ the emotional hook type (curiosity gap for the seed creator).

The description quality bar: it should expand on the hook from the script, explain what the viewer will get from the video, and end with a clear call to action. It should be written in the creator's voice — same register as the script, same vocabulary level.

The tags should include the topic, the format, relevant tool names, and searchable phrase combinations. 10 to 15 tags for YouTube. No tag should be more than 5 words. Tags should be lowercase.

---

**How to test the metadata agent:**

Run 1: Script and DNA profile as input. Verify JSON parses and schema validates. Read the title — does it follow the formula? Read the title_formula_match — does it correctly explain how the title maps to the formula?

Run 2: Count the words in the title. Is it within 2 words of the avg_word_count from the profile?

Run 3: Check whether the title uses the correct capitalization pattern. The seed creator uses some ALL CAPS words. Does the title?

Run 4: Read the description. Does it sound like the creator from the seed transcripts?

Run 5: Count the tags. Are there between 10 and 15? Are they all relevant to the actual topic?

---

**What "done" looks like for the metadata agent:**

Five runs produce correctly shaped JSON passing schema validation. Every title follows the creator's formula — this is verifiable by checking the title_formula_match explanation. Tag count is consistently within range. Description is written in the creator's voice register.

---

## Phase 2 — Step 7: Build the Scorer Agent (Quality Gate and Critic Agent)

**What this agent does:**

The scorer agent is the differentiation layer — the piece that no comparable tool has. It takes the GeneratedAsset (specifically the chosen thumbnail description, the metadata, and the script) alongside the CreatorDNAProfile, and evaluates whether the generated content actually matches the creator's established style. It produces a QualityScore object. If the score is below the threshold, it produces a specific rejection reason that tells the orchestrator what was wrong and what needs to change.

This agent must be built to reject output. The purpose of the reject path is not to be punitive — it is to demonstrate that the system has genuine quality standards, not just a pipeline that outputs whatever it generates. The demo's strongest moment is a live rejection with a specific, readable reason, followed by a regeneration that fixes the identified problem.

---

**What the scorer agent must produce:**

A complete QualityScore object as defined in Phase 0 Schema 7. Four dimension scores, one overall score, a pass/fail decision, and — critically — a rejection reason when the asset fails.

The quality bar for the scorer is specificity of rejection. A rejection reason that says "the thumbnail does not match the creator's style" is unacceptable. The acceptable form is: "The thumbnail uses a blurred background (variant 2, layout_description indicates 'blurred desk background') which directly conflicts with the creator's thumbnail_style.background_type specification of 'solid color.' Additionally, the creator's thumbnail_style.text_style specifies 2-4 words in all-caps, but the generated thumbnail uses 7 words in mixed case."

Every rejection reason must cite the specific profile field that was violated and describe the specific way the generated asset violates it. This is what makes the decision log look intelligent rather than scripted.

---

**The scoring dimensions and what each one evaluates:**

Thumbnail fit evaluates the selected thumbnail's layout description against the thumbnail_style section of the profile. It checks background type, text style, facial expression type, layout pattern, and color palette. Each mismatch reduces the score proportionally.

Title fit evaluates the metadata title against the title_formula section of the profile. It checks structure match, word count, capitalization pattern, number usage, and emotional hook type. The title_formula_match explanation from the metadata agent is also evaluated — if the explanation does not actually match the formula, that is a signal the title may be off.

Voice fit evaluates the script's full_voiceover_text against the voice section of the profile. It checks whether the hook follows the hook_pattern, whether the vocabulary matches the vocabulary_level, whether any of the what_to_avoid patterns are present, and whether the signature phrases appear naturally.

Overall score is a weighted average: thumbnail fit is weighted 35%, title fit is weighted 35%, and voice fit is weighted 30%. These weights can be adjusted by updating the system prompt — they do not need to be hardcoded in the logic.

---

**How to write the scorer agent system prompt:**

The system prompt provides the full CreatorDNAProfile, the selected thumbnail's layout description, the metadata title and title_formula_match, and the script's full_voiceover_text.

It instructs the model to evaluate each dimension methodically — not to produce a gut-feel score, but to go through each relevant profile field and assess whether the generated content matches it, then convert that assessment into a score.

It instructs the model that rejection reasons must be specific — they must name the profile field that was violated and describe the specific mismatch. Generic rejection reasons are not acceptable.

It provides the threshold (0.75 by default) and instructs the model to set passed to true only if the overall score is at or above the threshold.

---

**How to test the scorer agent — and how to force a rejection deliberately:**

Testing the scorer agent requires deliberately giving it bad input. Do not just test the happy path where everything passes. You need to test the reject path explicitly.

Test run for a pass: Use the output from the previous agents — the thumbnail description, the metadata title, and the script — with the full creator profile. The scorer should pass because the previous agents were built to follow the profile.

Test run for a rejection (thumbnail): Manually write a thumbnail description that violates the creator's style — "blurred background, no creator face, small text in mixed case." Feed this to the scorer. It must reject with a specific reason citing the background_type and text_style violations.

Test run for a rejection (title): Manually write a title that does not follow the formula — a vague title with no numbers, no timeframe, no first-person framing. Feed this to the scorer. It must reject with a specific reason citing the title_formula.structure violation.

Test run for a borderline case: Manually write a thumbnail and title that partially follow the profile — maybe the thumbnail is correct but the title is wrong. The scorer should produce a score that fails the overall threshold even if one dimension scores well, and the rejection reason should identify specifically which dimension dragged it below the threshold.

Test run for a full pass after fixing a rejection: Take the rejected thumbnail description from the first rejection test, fix the specific issue the scorer identified, and resubmit. The scorer should now pass the thumbnail dimension.

These deliberate rejection tests are not just for verification — they are for building confidence that the scorer will produce a live rejection during the demo when you need it to. If the scorer never rejects anything realistic, the demo moment does not work.

---

**What "done" looks like for the scorer agent:**

Five runs with correct-profile-matching input all produce a pass with an overall score at or above 0.75. Three deliberate rejection tests all produce specific, readable rejection reasons that cite the profile fields violated. One deliberate fix-and-resubmit test produces a pass on the previously failing dimension. The rejection reasons are specific enough that someone reading them could fix the problem without needing additional explanation.

---

## Phase 2 — Step 8: Verify the Full Agent Chain End to End (Still in Isolation, Not Through the API)

**What this step is about:**

Now that every agent works standalone, you run the full chain once — not through the API, not through the orchestrator, but as a manual sequence in a test script. You call each agent in order, passing the output of each one as the input to the next, and verify that the chain produces a complete result without any agent failing on another agent's real output.

This is different from Phase 4 (orchestration) because you are not building the orchestrator yet. You are doing a manual integration check — verifying that the contracts between agents are sound before the orchestrator formalizes them.

---

**The sequence:**

Step one: Call the DNA agent with the 8 seed videos and pre-calculated benchmarks. Store the output CreatorDNAProfile.

Step two: Call the opportunity agent with the stored CreatorDNAProfile and the trends list. Store the three ContentOpportunity objects. Select the one with the highest fit score.

Step three: Call the thumbnail agent with the selected ContentOpportunity and the CreatorDNAProfile. Store the 3 ThumbnailVariant objects.

Step four: Call the script agent with the selected ContentOpportunity and the CreatorDNAProfile. Store the Script object.

Step five: Call the metadata agent with the Script and the CreatorDNAProfile. Store the Metadata object.

Step six: Select the first thumbnail variant. Call the scorer agent with the selected thumbnail's layout description, the metadata title, the script's full voiceover text, and the CreatorDNAProfile. Read the QualityScore.

Step seven: If the score passes, record the result. If the score fails, note the rejection reason, manually adjust the input that failed (thumbnail description or title), and call the scorer again. Verify that a targeted fix produces a pass.

---

**What you are checking:**

Does every agent accept the real output of the previous agent without a schema error? The DNA agent's output has been validated, but when you pass it directly to the opportunity agent, are there any field name mismatches or type issues that were not caught in isolation?

Does the final QualityScore reflect the actual quality of the chain's output? If every agent followed the profile correctly, the scorer should produce a pass. If it rejects without a good reason, either the scorer prompt is too strict or one of the earlier agents drifted from the profile in a way the individual tests did not catch.

How long does the full chain take? Time it. A full chain run at this stage — without video rendering — should take under 60 seconds. If it takes longer, identify which agent is slow and decide whether to optimize it or simply prepare the demo to narrate through the wait.

---

**What "done" looks like for Step 8:**

One complete manual chain run produces a full result — a CreatorDNAProfile, three ContentOpportunity objects, a Script, three ThumbnailVariant SVGs, Metadata, and a QualityScore — with no schema errors at any stage. The QualityScore reflects the actual quality of the output. The end-to-end time is measured and recorded. You know what the full chain produces for the seed creator and it looks like genuinely personalized content for that creator.

---

## Phase 2 — The Done Definition

Phase 2 is complete when all of the following are true simultaneously.

Every agent has been run at least 5 to 10 times with varied inputs and consistently produces correctly shaped JSON that passes schema validation.

The DNA agent produces a profile that accurately reflects the patterns in the seed catalog — distinguishing high performers from low performers and identifying the creator's specific voice, title formula, and thumbnail style.

The opportunity agent produces rationales that explicitly cite specific fields from the creator profile — not generic advice.

The thumbnail agent produces SVG markup that renders without errors and visually follows the creator's thumbnail style.

The script agent produces scripts that sound recognizably like the seed creator — using the hook pattern, vocabulary level, and signature phrases from the profile.

The metadata agent produces titles that follow the creator's title formula and includes a title_formula_match explanation that correctly describes the mapping.

The scorer agent produces specific, field-citing rejection reasons when given intentionally mismatched input, and passes correctly matched input.

One complete manual chain run succeeds end to end with no schema errors and a passing quality score.

The end-to-end time for the full agent chain is measured and recorded.

---

*Phase 2 produces no API endpoints, no rendered media, and no frontend. It produces six reliable, tested agents that each do exactly one thing correctly and consistently. Every phase after this builds on these agents as trusted components.*