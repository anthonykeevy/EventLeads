# Story 0002 — UAT Testing Guide

Shard refs: docs/shards/02-data-schema.md, docs/shards/04-auth-rbac.md

## Prereqs
- Auth working; tester has JWT for an org
- DB migrated to head (a014 applied)

## Scenarios
1) Create Event (Happy Path)
   - POST /api/v1/events with name, timezone, dates
   - Expect 201 with id; GET returns event fields
2) List Events (Org Scope)
   - GET /api/v1/events returns only tester’s org events
3) Update Event
   - PUT /api/v1/events/{id} changes name/timezone/dates
4) Create Form
   - POST /api/v1/events/{id}/forms with name
   - Expect unique PublicSlug, GET returns slug
5) List Forms
   - GET /api/v1/events/{id}/forms returns created form
6) Create Layout
   - POST /api/v1/canvas/forms/{form_id}/layouts (device_type, aspect_ratio, resolution_x/y)
   - Expect id and revision_number=1
7) Soft Delete Event (Admin)
   - DELETE /api/v1/events/{id} expects status=deleted; list no longer shows item
8) Restore Event (Admin)
   - POST /api/v1/events/{id}/restore shows again in list
9) Soft Delete/Restore Form (Admin)
   - DELETE / POST restore under event
10) Slug Collision Handling
   - Create two forms with same name; second gets suffixed slug

## Negative Cases
- Non-Admin delete/restore → 403
- Cross-org access → 404
- Missing required fields → 400

## Evidence Capture
- Record request/response pairs
- Note slugs, ids, timestamps
