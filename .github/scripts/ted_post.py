#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib.request import Request, urlopen


def api_post(url: str, token: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = Request(
        url,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        },
    )
    with urlopen(req) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body) if body else {}


def main() -> int:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("GITHUB_TOKEN is not set")

    ted_dir = Path(".ted")
    draft = json.loads((ted_dir / "draft.json").read_text(encoding="utf-8"))
    repo_full = (ted_dir / "target_repo.txt").read_text(encoding="utf-8").strip()
    issue_no = (ted_dir / "target_issue.txt").read_text(encoding="utf-8").strip()

    should_post = bool(draft.get("should_post"))
    escalate = bool(draft.get("escalate"))
    draft_body = draft.get("draft_body", "")
    labels = draft.get("labels_to_add") or []

    if should_post:
        comment_url = f"https://api.github.com/repos/{repo_full}/issues/{issue_no}/comments"
        comment_resp = api_post(comment_url, token, {"body": draft_body})
        html_url = comment_resp.get("html_url", "")
        if html_url:
            print(f"Posted comment: {html_url}")
        else:
            print("Posted comment.")

    if escalate:
        if not labels:
            print("Escalate=true but labels_to_add empty; skipping labels.")
            return 0
        labels_url = f"https://api.github.com/repos/{repo_full}/issues/{issue_no}/labels"
        labels_resp = api_post(labels_url, token, {"labels": labels})
        applied = [item.get("name") for item in labels_resp if isinstance(item, dict)]
        if applied:
            print(f"Applied labels: {', '.join(applied)}")
        else:
            print("Applied labels.")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Post job failed: {exc}", file=sys.stderr)
        raise
