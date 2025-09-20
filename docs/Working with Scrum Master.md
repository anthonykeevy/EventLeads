# Working with Scrum Master

Purpose: A quick guide for starting new stories and coordinating with the Scrum Master (SM) agent.

## Workflow (Propose → Confirm → Execute → Summarise → Handover)
1) You propose the next task or say “next”.
2) SM proposes the exact task, agent owner, and deliverables; asks for approval.
3) On approval, SM activates the agent and produces the deliverable (code/doc/tests/migration).
4) SM summarises results and updates story docs with evidence and shard citations.
5) SM hands off to QA → UAT → next task.

## Documentation Standards
- Story docs live in `docs/stories/` and follow ACs with shard citations.
- Implementation doc: `docs/story-<id>-implementation-walkthrough.md` records evidence and links.
- PRs use `.github/pull_request_template.md` with shard citations and migration checks.

## Database & Migrations
- All required seed data (e.g., `GlobalSetting`) added via Alembic migrations with downgrade.
- Idempotent seeds; verified on Dev (SQL Server) and Test (SQLite).

## UAT Expectations
- SM provides a MailHog-ready flow for email-based features.
- Frontend configured to proxy or use `NEXT_PUBLIC_API_BASE` so you can test without setup.
- SM fixes issues found in UAT and re-runs evidence before re-handover.

## British English Copy
- Use British English (e.g., “organisation”).

## Scope Changes During UAT
- If UAT uncovers UX/policy gaps, SM will:
  - Propose the smallest change that unblocks the user experience.
  - Implement and record the change with evidence in the implementation doc.
  - Update the story doc with a “Scope Changes & UAT Enhancements” section describing what changed and why.
  - Mark “Original vs Completed” to reflect the final body of work.

## Starting a New Story
- Say: “@sm Next story: <title>”.
- SM will: create/update story doc, propose Sprint tasks, and start with the smallest deliverable that unlocks UAT.
