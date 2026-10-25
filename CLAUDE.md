# CLAUDE.md: FirstHeat

FirstHeat is an adaptive heat-safety planner for people who are new to the heat. Days 1–5 (through commit 04ec278) built the core app; later commits are the redesign. AI_LOG.md records all AI use.

## Rules
- Claude Code works on the interface and new features only. Don't change the calculation files (core/wbgt.py, core/weather.py, core/acclim.py, core/planner.py, core/geocoding.py) without asking.
- Log every AI-assisted change in AI_LOG.md (what the AI wrote, what I did, and which files changed).
- Keep the Day 1–5 repository (`TheSman122333/firstheat`) unchanged. Its old address, firstheat.vercel.app, redirects to first-heat.vercel.app.
- Deploys: Vercel project `first-heat` -> first-heat.vercel.app, linked to this repo. Pushes trigger deploys.

## Stack notes
- Python 3.12, Flet 1.0.4. Use `ft.run(main)`, not the old `ft.app(target=main)`.
- `fastapi==0.144.0` is pinned: flet-web 1.0.4 passes `openapi_prefix`, which FastAPI removed in 0.145.0. Keep the pin in `requirements.txt` and `pyproject.toml`.
- Web entry for Vercel is `app.py` (`flet_web.fastapi.app(main)`); `pyproject.toml` has `[tool.vercel] entrypoint = "app:app"`.
- Weather comes from Open-Meteo (no API key).
- `core/` has no `flet` imports, so it stays testable with pytest.
- Owner works on Windows with PowerShell and the conda env `firstheat`.

## Product wording
- Heat-safety guidance defers to official sources (CDC, NATA/KSI, OSHA/NIOSH), never promises safety, and labels WBGT as an estimate.
- Emergency mode always says to call 911 first.
