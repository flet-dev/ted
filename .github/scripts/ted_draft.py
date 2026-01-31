#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path


def main() -> int:
    repo_root = Path(".")
    ted_dir = repo_root / ".ted"
    ted_dir.mkdir(parents=True, exist_ok=True)

    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path:
        raise SystemExit("GITHUB_EVENT_PATH is not set")
    shutil.copyfile(event_path, ted_dir / "event.json")

    schema_path = ted_dir / "draft.schema.json"
    schema = {
        "type": "object",
        "properties": {
            "should_post": {"type": "boolean"},
            "draft_body": {"type": "string"},
            "escalate": {"type": "boolean"},
            "labels_to_add": {"type": "array", "items": {"type": "string"}},
            "dev_summary": {"type": "string"},
        },
        "required": [
            "should_post",
            "draft_body",
            "escalate",
            "labels_to_add",
            "dev_summary",
        ],
        "additionalProperties": False,
    }
    schema_path.write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")

    agent_path = repo_root / ".codex" / "agents" / "tedthebot.md"
    prompt_path = ted_dir / "prompt.txt"
    prompt_suffix = """

---
DRAFT PHASE TASK

The GitHub webhook payload is in: .ted/event.json

Produce JSON that matches .ted/draft.schema.json:
- should_post: true only if a helpful reply is warranted
- draft_body: the proposed reply in GitHub-flavored Markdown

Also decide if this should be escalated to developers.

- If escalate=true, include "needs-dev" in labels_to_add.
- labels_to_add must be a small set (0-5), from: needs-dev, bug, regression, needs-repro, platform:macos, platform:windows, platform:linux, platform:web, platform:ios, platform:android
- dev_summary must be a short 3-6 bullet summary for maintainers (no secrets).

  Do NOT apply labels in draft phase.

Constraints:
- Do NOT post to GitHub in draft phase.
- If you need more context, use GitHub MCP tools to read the issue and recent comments.
"""
    prompt_path.write_text(
        agent_path.read_text(encoding="utf-8") + prompt_suffix,
        encoding="utf-8",
    )

    draft_path = ted_dir / "draft.json"
    prompt_text = prompt_path.read_text(encoding="utf-8")
    subprocess.run(
        [
            "codex",
            "exec",
            "--output-schema",
            str(schema_path),
            "-o",
            str(draft_path),
            prompt_text,
        ],
        check=True,
    )

    print(draft_path.read_text(encoding="utf-8"))

    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    should_post = draft.get("should_post", False)
    escalate = draft.get("escalate", False)
    labels = draft.get("labels_to_add") or []
    dev_summary = draft.get("dev_summary", "")
    draft_body = draft.get("draft_body", "")

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as fh:
            fh.write(f"should_post={str(should_post).lower()}\n")
            fh.write(f"escalate={str(escalate).lower()}\n")

    step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if step_summary:
        labels_block = "\n".join(f"- {label}" for label in labels)
        summary = (
            "## 🤖 TedTheBot draft\n\n"
            f"**should_post:** `{str(should_post).lower()}`\n\n"
            "### Proposed reply\n\n"
            "```md\n"
            f"{draft_body}\n"
            "```\n"
            "### Escalation\n\n"
            f"- escalate: {str(escalate).lower()}\n"
            "- labels_to_add:\n"
            "```\n"
            f"{labels_block}\n"
            "```\n\n"
            "### Dev summary\n\n"
            "```\n"
            f"{dev_summary}\n"
            "```\n"
        )
        with open(step_summary, "a", encoding="utf-8") as fh:
            fh.write(summary)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
