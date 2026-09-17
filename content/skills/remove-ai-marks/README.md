# remove-ai-marks

Vendored from [guillaumemeyer/watermarks-remover](https://github.com/guillaumemeyer/watermarks-remover) (MIT, see `LICENSE.upstream`).

`SKILL.md` and `references/` are an unmodified copy. `service/`, `config/` and
`compose.yaml` were added here so the skill is self-contained — upstream keeps
them at the repository root.

## Bring the service up

The skill is a thin HTTP client and refuses to fall back to local cleaning, so
nothing works until this is running:

```bash
cd content/skills/remove-ai-marks
docker compose up --build -d
curl -sf http://127.0.0.1:8765/health
```

`127.0.0.1:8765` is the default the skill expects; override with
`WATERMARKS_SERVICE_URL` if you move it. Set `WATERMARKS_SERVER_API_KEY` on both
sides to require a bearer token.

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
