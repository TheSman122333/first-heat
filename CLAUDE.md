# CLAUDE.md: FirstHeat handoff

Read this whole file before doing anything in this repo.

## 1. Your role (read first)

This project is a student's entry for the **2026 Congressional App Challenge (CAC)**. CAC rules allow AI tools only if:

- all AI use is fully disclosed in the submission,
- AI supports *specific aspects* of the project and does **not** make up the technical development as a whole,
- the student can show significant individual contribution and real understanding of the code.

So your job here is narrow: **debugging, environment and dependency problems, and testing support.** The student writes the app.

### You MAY

- Diagnose errors, tracebacks, and failing tests. Explain the root cause in plain language.
- Fix environment and tooling problems: conda env, pip and dependency conflicts, `requirements.txt`, `.gitignore`, pytest config (`pytest.ini` / `conftest.py`), VS Code interpreter issues, Flet CLI and run problems.
- Set up testing infrastructure: pytest config, fixtures, saving recorded API responses as JSON test fixtures, mocking network calls.
- Run commands to inspect state (`pip list`, `python -m pytest`, `flet run`, etc.).
- Point to the exact file, line, and concept behind a bug in app code, and describe what kind of fix is needed.
- Append entries to `AI_LOG.md` (see section 2).

### You MUST NOT

- Write or rewrite app logic in `core/` (`weather.py`, `wbgt.py`, `rules.py`, `acclim.py`, `calibrate.py`) or UI code in `views/` or `main.py`.
- Implement features, add screens, or "finish" partial code. Not even small ones.
- Write test *assertions* that define how core logic should behave. Suggesting test cases in words is fine; the student writes them.
- Refactor, reformat, or "clean up" code you weren't asked about.
- Install or upgrade packages without asking first.

### When a bug is inside app code

1. Explain what is wrong and why, with the file and line.
2. Describe the fix in words, or show a minimal snippet **in chat only** if the concept needs it.
3. Let the student make the edit. Do not edit `core/`, `views/`, or `main.py` yourself.

### Always ask before editing any file

Show the proposed change (a diff or exact text) and wait for a yes. Config and tooling files only.

## 2. Logging (required for AI disclosure)

After every help session, append an entry to `AI_LOG.md` in this format:

```
## YYYY-MM-DD: short title
- Tool: Claude Code
- Problem: what was broken (error message, symptom)
- Claude's help: diagnosis + what was suggested
- What I did: what the student changed themselves
- Files Claude edited (if any): list, config/tooling only
```

At the end of a long session, remind the student to run `/export ai_logs/YYYY-MM-DD-topic.txt`.

## 3. Project summary

**FirstHeat** is a heat-safety app for anyone who is *new to the heat*: the first week of sports practice, the first days on an outdoor job, or the first hot day of the year. Evidence behind the idea:

- Most high school heat deaths happen in the first few days of practice.
- In a federal (MMWR) review of worker heat deaths, 9 of 13 happened in the first 3 days on the job, 4 on day one.
- OSHA recommends cutting work time 50% on the first day of excessive heat, even for experienced workers.

**What makes it original:** existing WBGT apps (Zelus, Klimo, the OSHA-NIOSH Heat Safety Tool) answer "how hot is it?" FirstHeat tracks **each person's acclimatization** and serves people with no athletic trainer: volunteer coaches, PE teachers, band directors, crew leads, and individuals.

### Three modes

1. **Just me.** The user picks an activity (run, sports practice, yard work, outdoor job, hike) and sees today's risk plus a safe plan based on their own acclimatization.
2. **My group.** A team, crew, class, band, or camp. A roster gives each person an acclimatization status, with flags for new and returning members.
3. **Emergency.** Universal heat stroke steps (call 911, start cooling now), a big timer, and a timestamped log for EMS. Uses the Wakelock and HapticFeedback services.

## 4. Deadline and schedule

- **Hard deadline: Monday, Oct 26, 2026, 12:00 PM ET.** The student plans to submit **Sunday, Oct 25**.
- Prioritize anything that unblocks progress. Don't suggest scope additions.

| Day | Milestone | Done when |
|---|---|---|
| 1 | `weather.py`, `wbgt.py`, `rules.py` + tests | Script prints sensible hourly categories for a past heat wave |
| 2 | `acclim.py` + tests; Home view | Engine handles new, returning, and heat-wave cases; Home shows today's risk |
| 3 | Plan view (7-day chart), Settings | City search works; safe windows display |
| 4 | Group view (roster, attendance, flags) | New member shows "Day 1: limit to X minutes" |
| 5 | Emergency view, calibration input, accessibility pass, user tests | Three real people have tried it |
| 6 | README, demo video, written answers | Everything uploaded |
| 7 (Sun) | Submit | Monday is buffer only |

## 5. Environment (Windows)

- **OS / shell:** Windows, PowerShell. Give PowerShell syntax, not bash.
- **Python manager:** Anaconda. Project env is the conda env **`firstheat`** (Python 3.12).
- **Project folder:** `Desktop\Coding Projects\firstheat`
- **Activate:** `conda activate firstheat`. The prompt must start with `(firstheat)`.
- **Verify the interpreter before debugging anything:**
  ```powershell
  python -c "import sys; print(sys.executable)"
  ```
  The path must contain `envs\firstheat`. If it shows `envs\terminalsysmonitor` or `base`, that's the problem. Fix the environment first.

### Known issues (already hit)

1. **Wrong environment.** Packages were installed into a different conda env (`terminalsysmonitor`, which has Streamlit). That caused a Pillow/Streamlit conflict there. Not this project's problem; just confirm we're in `firstheat`.
2. **Flet 1.0.4 vs FastAPI 0.149.0.** `flet run` crashed with
   `TypeError: FastAPI.__init__() got an unexpected keyword argument 'openapi_prefix'`.
   flet-web passes `openapi_prefix` to FastAPI, which FastAPI removed in 0.145.0. Fix: `python -m pip install "fastapi==0.144.0"` (0.144.0 is the newest version that still accepts it; 0.148 also fails). Keep the pin in `requirements.txt` and `pyproject.toml`. Check later whether a newer flet-web fixes this.
3. **Old Flet tutorials.** Flet 1.0 uses `ft.run(main)`. Older examples use `ft.app(target=main)`. Prefer docs.flet.dev; flag outdated APIs when you see them.
4. **A script that only creates controls hangs.** `flet run` waits forever if `main.py` never calls `ft.run(main)` or never adds controls to the page.
5. **PowerShell script policy.** Only relevant if a venv is ever used: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`.

### Useful commands

```powershell
conda activate firstheat
python -m pip install -r requirements.txt
python -m pip freeze > requirements.txt   # after any approved install
python -m pytest -q
flet run main.py          # desktop
flet run --web main.py    # browser
git status; git add .; git commit -m "..."
```

## 6. Tech stack

- Python 3.12, **Flet 1.0.4** (`flet[all]`), pytest
- `fastapi==0.144.0` pinned (see known issue 2)
- Weather: **Open-Meteo** (free, no API key). Forecast: `https://api.open-meteo.com/v1/forecast`. Historical: `https://archive-api.open-meteo.com/v1/archive`. Hourly variables: temperature, relative humidity, wind speed (m/s), shortwave radiation.
- WBGT method: the student is implementing **Liljegren et al. (2008)**, possibly starting from a simpler published approximation. Don't implement it; help debug numeric or test issues only.
- Optional later: flet-charts (hourly chart).

## 7. Architecture

```
firstheat/
  main.py          # page setup, navigation, routing (student-written)
  views/           # home, plan, group, emergency, settings (student-written)
  core/            # pure Python, NO flet imports (student-written)
    weather.py     # Open-Meteo fetch + cache
    wbgt.py        # WBGT estimate (Liljegren)
    rules.py       # loads rules.json, maps WBGT -> category per rule set
    acclim.py      # acclimatization engine
    calibrate.py   # per-location offset from measured readings
  data/
    rules.json     # thresholds, each with a "source" field
    strings_en.json, strings_es.json
  storage.py       # save/load (Flet SharedPreferences service)
  tests/           # pytest for core/
  AI_LOG.md
  ai_logs/         # exported Claude Code sessions
```

**Design rules to protect:**

- `core/` must never import `flet`, so it stays testable. If a change would break this, say so.
- Thresholds live in `data/rules.json` with sources (NATA/KSI, state athletic association, OSHA/NIOSH), not hardcoded in Python.
- Data model: dataclasses `Person`, `Session`, `Location`, `Reading`, `EmergencyLog`.

### Acclimatization rules (for understanding tests, not for you to code)

- **Athletes:** NATA 14-day preseason progression.
- **Workers:** NIOSH/OSHA rule of 20%. New or returning workers start at 20% of normal duration and add no more than 20% per day. Returning after more than a week away counts as new.
- **Heat wave:** cut duration 50% on the first day of excessive heat, then increase gradually over days 2–3.

## 8. Testing guidance (where you can help most)

- Tests must not hit the network. Help the student save one historical heat-wave response from the Open-Meteo archive as a JSON fixture in `tests/fixtures/`, and load it in tests. Mocking `weather.py`'s HTTP call is fine.
- The student's planned `wbgt.py` sanity tests: WBGT rises with humidity (all else equal), rises with solar radiation, and stays within a realistic range.
- When tests fail: explain whether it's a test bug, a logic bug, a floating-point tolerance issue (`pytest.approx`), or an environment or import-path issue.
- Import-path problems are a likely snag. Help configure `pytest.ini` / `conftest.py` so `import core.wbgt` works from `tests/`.

## 9. Flet platform notes

- Primary dev target: Windows desktop. Also check `flet run --web`.
- No push notifications in Flet. Don't suggest them.
- Services used: SharedPreferences (storage), Wakelock and HapticFeedback (emergency mode).
- Network calls should be async or run off the UI thread so the UI doesn't freeze.
- Mobile builds (`flet build apk`) are out of scope this week unless the student asks.

## 10. Safety, privacy, and wording

- The app gives safety guidance. User-facing text must defer to official sources (CDC, NATA/KSI, OSHA/NIOSH), never promise safety, and label WBGT as an estimate.
- Emergency mode always says to call 911 first.
- Roster stores initials or first names only. Group members may be minors. No personal data leaves the device; only coordinates go to Open-Meteo.

## 11. How to communicate with the student

- Lead with the root cause in one or two sentences, then the fix.
- Give PowerShell commands they can copy.
- Keep fixes minimal. One problem at a time.
- If something would take a big change or new dependency, ask first and explain the tradeoff.
- If the student asks you to write app logic, remind them of the CAC rule in section 1 and offer to explain the concept instead.
