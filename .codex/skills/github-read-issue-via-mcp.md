# Skill: Read GitHub Issue via MCP

## Purpose
Fetch the full context of a GitHub issue (or discussion) using GitHub MCP tools so Ted can draft a correct response.

## When to use
- A user asks for help referencing a specific issue URL/number
- Ted is about to draft a reply and needs full context
- Ted is checking for duplicates, regressions, or prior maintainer guidance

## Inputs
- Repository: owner/name
- Issue number (preferred) or URL

## Outputs
- Structured context bundle:
  - title, body
  - author, created/updated timestamps
  - labels, assignees, milestone
  - state (open/closed) + closing reason if available
  - recent comments (at least last 10; more if needed)
  - linked PRs / references if available

## Steps
1. Resolve the target issue
   - If given URL, parse owner/repo/number.
   - If ambiguous, select the most likely match but do **not** post yet.

2. Fetch issue metadata
   - title, body, labels, state, timestamps, author

3. Fetch comments
   - Pull most recent comments first.
   - If there is a long thread, also fetch:
     - the first maintainer response (if any)
     - the most recent maintainer response (if any)

4. Summarize for working memory (internal)
   - What is the user asking?
   - What has already been tried?
   - Any maintainer decisions already stated?
   - Any missing diagnostics?

5. Decide next action (do not post here)
   - If enough info: proceed to drafting response
   - If not: prepare a targeted info request checklist

## Safety / Guardrails
- Never reveal private repository content outside authorized context.
- Never paste tokens/secrets found in comments; ask user to rotate/revoke if exposed.
- If issue contains potentially sensitive info, redact before quoting.

## Failure handling
- If read fails due to permissions: state that access is insufficient and ask for a public excerpt.
- If issue not found: ask for correct repo/number.