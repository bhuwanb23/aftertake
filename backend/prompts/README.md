# Agent System Prompts (Phase 2 — Practice 5)

One system prompt per agent, in its own `.txt` file, loaded at runtime by
`backend.agents.core.load_prompt(name)` — never hardcoded in agent code.
To iterate on an agent, edit its file here and re-run that agent's dev script;
nothing else is touched.

**Files:**
- `dna_system.txt` — DNA agent (creates the CreatorDNAProfile)
- `opportunity_system.txt` — opportunity agent
- `script_system.txt` — script agent
- `thumbnail_system.txt` — thumbnail agent
- `metadata_system.txt` — metadata agent
- `scorer_system.txt` — scorer agent

**Every file follows the same structure, in this order:**

1. **Role definition** — exactly what the agent is and what it does
   (e.g. "You are the script-writing agent for a content engine...").
2. **Task description** — the detailed job it must perform with the inputs it
   receives.
3. **Output field specification** — every field it must include, what each one
   means, and its allowed values. Field names must match the Phase 1 Pydantic
   model exactly (shape drift costs an iteration).
4. **What to avoid** — explicit negative instructions (style drift, generic
   output, extra text, forbidden values).
5. **The JSON-only instruction** — the verbatim `JSON_ONLY_INSTRUCTION` from
   `backend/agents/core.py` ends every file. `with_json_instruction()` is the
   idempotent safety net if a file ever omits it.

**Rule (Phase 0 Step 3d / 2):** output must be conditioned on the creator's
learned profile — if a prompt could produce the same output for any creator,
the prompt is wrong. Fix prompts, never switch models.
