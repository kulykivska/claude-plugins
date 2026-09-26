---
name: backend-coding
description: >-
  How to write correct backend code in Python/FastAPI or TypeScript/NestJS: follow the
  repo's layering, and apply failure handling, security, data and migration discipline,
  scalability and performance while implementing. Use when adding or changing an
  endpoint, service, job, schema or migration.
---

# Backend coding guide

Read **`engineering-standards`** first; it is the list `python-reviewer` and the
other reviewers mark against. Then the repo's own rules, and a sibling module to copy.

## Shape
- **Layers stay separate:** transport (route / controller) validates and maps;
  services hold the rules; repositories talk to the database. No SQL in a route, no
  HTTP types in a service.
- **Contracts first.** Change the request / response schema (Pydantic model, Zod or
  class-validator DTO, OpenAPI) before the code behind it, and keep optional fields
  optional so older clients still decode.
- **FastAPI:** async all the way down, no blocking I/O in `async def`; dependencies
  for auth and sessions; response models on every route. Keep request types imported
  at module level (FastAPI resolves annotations against module globals).
- **NestJS:** one module per bounded area; commands and queries through the pattern
  the repo already uses; DTOs validated at the edge.

## While writing
- **Failure handling.** Every external call has a timeout and a decided outcome on
  failure. No bare `except` / empty `catch`; log with context at the right level and
  return a typed error, never a 500 that hides a known case.
- **Auth.** Check ownership on every object you load by id, not only that the caller
  is signed in. Fail closed.
- **Data.** Migrations are additive and reversible; large-table indexes are built
  concurrently; backfills run in batches. A money or counter change is idempotent and
  transactional.
- **Scale.** No N+1 queries, no unbounded list endpoints (paginate), no work per
  request that could be done once. Background work goes to a job, not a request.
- **Secrets** come from the environment or a secret manager, never the source.
- **Scheduled and notifying jobs** keep their "already sent" state outside process
  memory, so a restart does not send twice.

## Before done
Type check, lint and the affected tests green; exercise the endpoint for real
(success, validation error, auth failure, not found). Then `python-reviewer` (or the
matching reviewer) and `task-review`.
