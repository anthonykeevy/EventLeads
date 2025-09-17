# Story 0002 — UAT Signoff Checklist

Shard refs: docs/shards/02-data-schema.md, docs/shards/04-auth-rbac.md

- [ ] Auth works and JWT contains org_id, role
- [ ] Create Event returns 201 and fields persisted
- [ ] List Events scoped to org
- [ ] Update Event persists changes
- [ ] Create Form assigns unique PublicSlug
- [ ] List Forms returns created forms
- [ ] Create Layout returns id and revision 1
- [ ] Admin-only delete/restore enforced (Events, Forms)
- [ ] Soft-deleted records excluded from lists
- [ ] Slug collision handled with suffix
- [ ] No PII leaked in error messages

Signoff:
- Tester:
- Date:
- Notes:
