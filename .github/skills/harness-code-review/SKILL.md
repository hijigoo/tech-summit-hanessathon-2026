---
name: harness-code-review
description: Agent-based code review Harness asset. Reviews a diff or files, classifies findings by severity (blocking/warning/info), and pushes them to the Harness Review Board canvas. WHEN: "review my code", "코드리뷰", "PR 점검", "보안 점검", "harness review".
---

# Harness Code Review

An agent-based ("하네스 엔지니어링") reusable asset that reviews code and
visualizes findings on the **Harness Review Board** canvas.

## Procedure
1. Gather the change set: `git diff`, staged files, or the paths the user names.
2. Review for, in priority order:
   - **blocking**: security holes (injection, secrets, authz), data loss, crashes, broken logic.
   - **warning**: error handling gaps, race conditions, perf cliffs, missing tests.
   - **info**: naming, structure, docs, minor style.
3. Open the board: `open_canvas` with `canvasId: "harness-review-board"`.
4. Push findings via the `set_findings` action. Each finding:
   `{ title, severity, file, line, detail }`.
5. Summarize counts in chat; mark items resolved with `resolve_finding` as fixed.

## Rules
- High signal only — no style nitpicks unless asked. Skip if nothing matters.
- Every blocking/warning finding must name file+line and a concrete fix.
- Don't modify code during review; propose fixes, apply only on request.
