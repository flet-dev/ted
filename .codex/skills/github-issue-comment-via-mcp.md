# Skill: Post GitHub Issue Comment via MCP

## Purpose
Publish a prepared response as a comment on a GitHub issue using GitHub MCP tools.

## When to use
Use only when **all** of the following are true:
- The response is ready to be posted publicly
- The issue context has been read (see: Read GitHub Issue via MCP)
- The response has been validated against safety and accuracy rules
- The repo/issue is within the allowed scope for TedTheBot

## Inputs
- Repository: owner/name
- Issue number
- Comment body (GitHub-flavored Markdown)

## Outputs
- Confirmation data:
  - comment id / url (if available)
  - timestamp

## Preconditions checklist (MUST PASS)
1. **No secrets**
   - No tokens, keys, credentials, or session cookies
2. **No hallucinations**
   - No invented commands, APIs, log lines, or version numbers
3. **Actionability**
   - Contains concrete next steps or questions
4. **Tone**
   - Friendly, professional, concise
5. **Correct target**
   - Repo + issue number match the intended thread

## Steps
1. Refresh context (light)
   - Re-fetch latest comments if thread is active to avoid replying to outdated info.

2. Draft / finalize comment body
   - Start with a short acknowledgement
   - Provide diagnosis or next steps
   - If requesting info, provide a single checklist
   - Include code blocks for commands/snippets
   - Keep it skimmable: bullets, headings

3. Validate (mandatory)
   - Run the Preconditions checklist
   - Ensure no internal-only references are included
   - Ensure links (if any) are correct and relevant

4. Post comment via MCP tool
   - Call the MCP action that creates an issue comment
   - Payload should be **only** the markdown body (no extra fields unless required)

5. Confirm success
   - Capture returned comment url/id
   - If MCP returns an error, do not retry blindly

## Safety rules (ABSOLUTE)
- Never post secrets (even if user posted them first). Instead:
  - advise rotation/revocation
  - ask them to redact and re-post sanitized logs
- Never post “maybe this works” without stating uncertainty and offering a safe verification step.
- Do not change issue state, labels, or assignees unless explicitly authorized in a separate skill.

## Failure handling
- Permission denied:
  - Report that Ted lacks permission to comment, and provide the draft for a maintainer to paste.
- Validation failed (e.g., secrets detected):
  - Do not post. Provide a sanitized draft and request redaction/rotation.
- Rate limits / transient errors:
  - Do not loop retries. Suggest manual posting or waiting.

## Optional: Human-in-the-loop gate (recommended for rollout)
If running in “approval required” mode:
- Output the finalized comment under a “Proposed comment” header
- Do not call the MCP post action