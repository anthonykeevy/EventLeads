# Story 0002 — Monitoring Guide

Shard refs: docs/shards/05-devops-migrations.md

## What to Monitor
- API: events/forms/canvas endpoints (2xx/4xx/5xx, latency)
- DB: migration health, slow queries on Event/Form/CanvasLayout
- Auth/Org: unexpected 403/404 rates on delete/restore

## Metrics
- HTTP request count/duration per route
- DB execution time (if available)
- Create/update/delete success/failure counters

## Logs
- Structured: request_id, org_id, event_id, form_id
- Errors: include reason_code for RBAC failures, validation errors

## Alerts
- Elevated 5xx on events/forms/canvas
- Migration failures
- Spike in 403/404 on protected endpoints

## Dashboards
- CRUD throughput and error rate
- Slug collision frequency (forms)
- Layout creations by device_type
