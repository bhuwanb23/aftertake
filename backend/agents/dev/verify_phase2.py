"""Phase 2 done-definition runner — one command to run the whole agent bank.

    backend/.venv/Scripts/python backend/agents/dev/verify_phase2.py [script...]

Runs the per-agent verification scripts in dependency order and the full
chain, reporting pass/fail per script. With no args it runs all seven; pass
names to run a subset:

    backend/.venv/Scripts/python backend/agents/dev/verify_phase2.py dna scorer

Each script is the durable evidence for one done-definition item (the last
recorded full pass of every script was green). This runner costs real LLM
calls (~40 with the current Ollama cloud model, ~5-8 minutes) — run it when
you want a fresh proof, not for iteration. The model is whatever
config/OLLAMA_MODEL resolves to (env override works: OLLAMA_MODEL=...).
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
PY = sys.executable

SCRIPTS = [
    ("dna", "verify_dna.py"),              # profile reflects seed patterns
    ("opportunity", "verify_opportunity.py"),  # rationales cite profile fields
    ("thumbnail", "verify_thumbnail.py"),  # SVGs render, follow the style
    ("script", "verify_script.py"),        # voice recognizably the creator's
    ("metadata", "verify_metadata.py"),    # titles follow the formula
    ("scorer", "verify_scorer.py"),        # rejects bad, passes good
    ("chain", "chain_e2e.py"),             # full chain, timed, no schema errors
]


def main() -> int:
    names = sys.argv[1:]
    targets = [s for s in SCRIPTS if not names or s[0] in names]
    if not targets:
        print("no matching scripts; available:", [s[0] for s in SCRIPTS])
        return 2

    failed = []
    for name, script in targets:
        path = ROOT / "backend" / "agents" / "dev" / script
        print(f"\n{'=' * 70}\n>>> {name}: {script}\n{'=' * 70}")
        r = subprocess.run([PY, str(path)], cwd=ROOT)
        status = "PASS" if r.returncode == 0 else f"FAIL (exit {r.returncode})"
        print(f">>> {name}: {status}")
        if r.returncode != 0:
            failed.append(name)

    print("\n=== PHASE 2 BANK SUMMARY ===")
    if failed:
        print(f"FAILED: {failed}")
        return 1
    print("ALL GREEN — every agent passes its done-definition verification.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
