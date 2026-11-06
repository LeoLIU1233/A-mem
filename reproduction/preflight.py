"""Validate the local A-MEM reproduction inputs without calling an LLM."""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "data" / "locomo10.json"


def main() -> int:
    if not DATASET.exists():
        print(f"ERROR missing dataset: {DATASET}")
        return 1

    samples = json.loads(DATASET.read_text(encoding="utf-8"))
    qa_counts = Counter()
    total_turns = 0
    for sample in samples:
        qa_counts.update(
            int(qa.get("category", -1)) for qa in sample.get("qa", [])
        )
        conversation = sample.get("conversation", {})
        total_turns += sum(
            len(value) for key, value in conversation.items()
            if key.startswith("session_") and isinstance(value, list)
        )

    modules = [
        "numpy", "openai", "torch", "transformers",
        "sentence_transformers", "nltk", "rouge_score",
    ]
    missing = [name for name in modules if importlib.util.find_spec(name) is None]

    print(f"Python: {sys.version.split()[0]}")
    print(f"Workspace: {ROOT}")
    print(f"LoCoMo samples: {len(samples)}")
    print(f"LoCoMo QA pairs: {sum(qa_counts.values())}")
    print(f"LoCoMo conversation turns: {total_turns}")
    print("QA category counts:", dict(sorted(qa_counts.items())))
    print("Missing dependencies:", missing or "none")
    print(
        "API key configured:",
        "yes" if os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY") else "no",
    )
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
