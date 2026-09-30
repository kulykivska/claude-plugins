# remove-ai-marks

Vendored from [guillaumemeyer/watermarks-remover](https://github.com/guillaumemeyer/watermarks-remover) (MIT, see `LICENSE.upstream`).

`SKILL.md` and `references/` are an unmodified copy. `service/`, `config/` and
`compose.yaml` were added here (`service/scripts/server.py` carries local
security hardening, see below) so the skill is self-contained — upstream keeps
them at the repository root.

## Bring the service up

The skill is a thin HTTP client and refuses to fall back to local cleaning, so
nothing works until this is running:

The service requires an API key and will not start without one. Put it in the
shell or in a `.env` file next to `compose.yaml` (`.env` is git-ignored; never
commit the value):

```bash
cd content/skills/remove-ai-marks
printf 'WATERMARKS_SERVER_API_KEY=%s\n' "$(openssl rand -hex 32)" > .env
docker compose up --build -d
curl -sf http://127.0.0.1:8765/health
```

The skill sends the same key from `WATERMARKS_SERVICE_API_KEY` on the client
side, so export it there too:

```bash
export WATERMARKS_SERVICE_API_KEY=<the same value>
curl -s http://127.0.0.1:8765/capabilities -H "Authorization: Bearer $WATERMARKS_SERVICE_API_KEY"
```

`127.0.0.1:8765` is the default the skill expects; override with
`WATERMARKS_SERVICE_URL` if you move it.

### Security defaults

A page open in your browser can reach anything on localhost, so the service
only answers requests a browser page cannot forge:

- Every request except `GET /health` needs `Authorization: Bearer <key>`,
  compared in constant time.
- `POST` bodies must be `Content-Type: application/json`, otherwise `415`.
- The `Host` header must be `localhost`, `127.0.0.1` or `[::1]` (bare or with
  the service port), otherwise `421`. This stops DNS rebinding. Add names with
  `WATERMARKS_ALLOWED_HOSTS=name,name:port`.
- A request with an `Origin` header not in the allowlist gets `403`. Add
  origins with `WATERMARKS_ALLOWED_ORIGINS=https://app.example`.
- Bodies over `WATERMARKS_MAX_BODY_BYTES` (default 64 MiB, about 48 MiB of
  file) get `413`; more than `WATERMARKS_MAX_CONCURRENT` (default 2) requests
  in flight get `503`. The container is capped at 2 GB of memory.
- It binds `127.0.0.1` by default. In Docker it binds `0.0.0.0` inside the
  container and `compose.yaml` publishes the port on `127.0.0.1` only. If you
  publish a different host port, add `127.0.0.1:<port>` to
  `WATERMARKS_ALLOWED_HOSTS`.

For local development without Docker you can skip the key, and only then:

```bash
WATERMARKS_ALLOW_NO_AUTH=1 python3 service/scripts/server.py
```

Tests: `python3 service/tests/test_server_security.py`.

## What is not vendored

Upstream's `harness` and `heavy` compose profiles (markllm, markdiffusion,
ctrlregen, reverse-SynthID) build from all-rights-reserved or non-commercial
sources, so they are left out. `/capabilities` will report those backends
absent, and the skill is written to only offer what the service reports.

That means statistical Layer B rewrite, pixel removal and SynthID scoring are
unavailable; Layer A (invisible Unicode) and metadata cleaning (C2PA / EXIF /
XMP, PDF / DOCX / ODT containers) work.

## Known gotcha

The image pins `python:3.14-slim` by an amd64 digest, so on Apple Silicon it
builds and runs under emulation. It works, just slowly on first build.

## Updating

Re-copy `SKILL.md`, `references/`, `service/` and `config/` from upstream, then
re-trim `compose.yaml` — the local one drops the profiles above and mounts
`config/` into the container, which upstream does not.

Re-copying `service/scripts/server.py` drops the local security hardening:
re-apply it and keep `service/tests/test_server_security.py` passing.
