# AI Use Log

## 2026-10-19: Flet crash from wrong Python environment; Day 1 scaffolding
- Tool: Claude Code
- Problem: Running main.py crashed with "TypeError: FastAPI.__init__() got an unexpected keyword argument 'openapi_prefix'".
- Claude's help: Traceback paths showed the conda base env was running the app, not firstheat. Base had fastapi 0.149.0, which is incompatible with flet-web 1.0.4. The firstheat env had no packages. VS Code's user settings defaulted to the base interpreter, and conda isn't set up in PowerShell. Claude also explained the planned file structure and what weather.py needs to do (in words only).
- What I did: Approved installing flet[all]==1.0.4, fastapi<0.149 and pytest into firstheat. Confirmed the VS Code Run button now launches the app. Chose to use the Run button for now instead of setting up conda in the terminal. Asked Claude to create empty Day 1 placeholder files; all code in core/ and tests/ will be written by me.
- Files Claude edited (if any): .vscode/settings.json (firstheat interpreter path, pytest enabled for the Testing panel); pytest.ini (new); AI_LOG.md (new). Created empty placeholders: core/__init__.py, core/weather.py, core/wbgt.py, core/rules.py, tests/test_weather.py, tests/test_wbgt.py, tests/test_rules.py, tests/fixtures/.gitkeep, and data/rules.json containing only {}. Claude also ran the approved pip install into firstheat.

## 2026-10-19: HTTP 400 from Open-Meteo archive
- Tool: Claude Code
- Problem: Detroit history fetch in weather.py failed with "HTTP Error 400: Bad Request".
- Claude's help: Reproduced the request. Open-Meteo's error body said temperature_unit "celcius" was invalid (should be "celsius"). Explained that HTTPError hides the API's reason unless its body is read. Pointed out that fetch_forecast passes the URL where latitude should go. Explained that the "�" characters in output were a terminal encoding issue, not bad data.
- What I did: Fixed the spelling in weather.py; confirmed 24 sensible hourly rows for 2024-06-19.
- Files Claude edited (if any): .vscode/settings.json (PYTHONUTF8=1 for VS Code terminals); tests/fixtures/detroit_2024-06-15_2024-06-23.json (new: raw Open-Meteo archive response for Detroit, June 15–23 2024, recorded with the same parameters as weather.py).

## 2026-10-19: Concept explanations (Open-Meteo coverage, WBGT method)
- Tool: Claude Code
- Problem: Questions, not errors: does Open-Meteo cover every country; what calculations a Liljegren WBGT estimate needs; where a manual weather-fetch check should live.
- Claude's help: Explained Open-Meteo's global coverage and limits (archive delay, free-use limits). Walked through the Liljegren WBGT steps in words (sun position, direct/diffuse sunlight split, 2 m wind, vapor pressure, air properties, iterative globe and wet-bulb temperatures) and suggested per-step test ideas. Advised keeping manual network checks out of tests/.
- What I did: Decided to target the US only for now. Kept the manual check in weather.py's __main__ block.
- Files Claude edited (if any): none

## 2026-10-19: WBGT review and offline test setup
- Tool: Claude Code
- Problem: Asked Claude to check my wbgt.py (which uses the lwbgt library for the Liljegren calculation) and set up testing.
- Claude's help: Checked my lwbgt inputs against the library's docs and source. Confirmed the UTC timestamps, 60-minute averaging and 10 m wind height match the Open-Meteo data, and that sample WBGT values are realistic. Pointed out: tests/test_wbgt.py runs network code at import (not a real test); times are UTC so display needs conversion to local time; lwbgt was missing from requirements.txt. Suggested (in words) considering urban vs. rural, pressure from elevation, keeping full precision in core/, handling missing (None) values, and crediting lwbgt and its license in the README. Found that the saved fixture was in local time while weather.py now requests UTC. Declined to write the test functions (CAC rule); gave test ideas in words.
- What I did: Wrote wbgt.py using lwbgt; switched weather.py to request UTC; approved Claude's setup changes below. I will write the tests myself.
- Files Claude edited (if any): tests/fixtures/detroit_2024-06-15_2024-06-24_utc.json (new: re-recorded in UTC through my fetch_history); deleted tests/fixtures/detroit_2024-06-15_2024-06-23.json (old, local time); tests/conftest.py (new: fixtures detroit_coords, detroit_response, offline_open_meteo, and an automatic network block; no test assertions); requirements.txt (re-frozen from the firstheat env, adds lwbgt, removes unrelated packages). Claude ran a temporary plumbing check of conftest.py (3 passed) and deleted it.

## 2026-10-19: Heat thresholds data file (ChatGPT)
- Tool: ChatGPT (separate thread from the Day 1 check below)
- Problem: Needed data/rules.json with sports (KSI regional) and worker (OSHA/NIOSH) WBGT thresholds and their sources.
- AI's help: ChatGPT wrote data/rules.json: the structure, the threshold values, the guidance text, the source links and the boundary notes.
- What I did: Asked ChatGPT for the file and added it to the project. Checked the threshold values against the cited sources on 2026-10-20.
- Files the AI wrote: data/rules.json (entire file).

## 2026-10-19: Rules engine (ChatGPT)
- Tool: ChatGPT
- Problem: Needed core/rules.py to load data/rules.json and map a WBGT value to a heat category for each rule set.
- AI's help: ChatGPT wrote most of core/rules.py.
- What I did: Reviewed and edited ChatGPT's code.
- Files the AI wrote: core/rules.py (most of the file).

## 2026-10-19: Day 1 check script (ChatGPT)
- Tool: ChatGPT
- Problem: Needed an end-to-end Day 1 check: weather → WBGT → heat category for each hour, printed in local time.
- AI's help: ChatGPT wrote daybyday/day1check.py, including check_rules() (assertions about how rules.py categorizes values at boundaries) and the default of sports region 2 for Detroit.
- What I did: Asked ChatGPT for the script and labeled the file "WRITTEN BY AI".
- Files the AI wrote: daybyday/day1check.py (entire file).

## 2026-10-19: Pytest explanation, judging prep, review of the Day 1 check
- Tool: Claude Code
- Problem: Asked Claude to write all the tests (declined under the CAC rules); asked what judges might ask and whether tests are needed; asked whether AI can write the day-end checks.
- Claude's help: Explained pytest basics with a toy example unrelated to FirstHeat and described the first weather test in words. Listed likely judge questions. Suggested a small set of safety-focused tests instead of full checklists. Reviewed daybyday/day1check.py: pointed out that check_rules() holds AI-written assertions that define rules.py behavior, and that the Detroit region 2 default was an unverified safety choice.
- What I did: Disclosed my ChatGPT use (entries above).
- Files Claude edited (if any): AI_LOG.md.

## 2026-10-20: Acclimatization engine, tricky parts (ChatGPT)
- Tool: ChatGPT
- Problem: Some of the acclimatization logic in core/acclim.py was tricky to get right.
- AI's help: A mix of writing code and explaining the approach for three parts: break detection (recent_work_days: work days since the last break of more than 7 days), the athlete day logic (consecutive practice days, the rest-day rule, the double-practice rule), and input validation (check_person and the type/value checks).
- What I did: Wrote the rest of acclim.py myself: the Person and Session dataclasses, the NIOSH new and experienced worker schedules, the heat-wave counting and the stricter-limit rule, the athlete practice limits and regional heat caps, and the acclimatization_plan dispatcher. Used or adapted ChatGPT's code for the three parts above.
- Files the AI wrote: parts of core/acclim.py (listed above).

## 2026-10-20: acclim.py review
- Tool: Claude Code
- Problem: Asked Claude whether core/acclim.py is correct.
- Claude's help: Ran scenarios through my code and found: returning athletes don't restart their progression; experienced workers get 50% or 20% depending only on whether old sessions exist; a worker who isn't marked experienced never counts as acclimatized; the heat caps are hard-coded instead of in rules.json; two warnings are missing a space. Asked me to verify the "rest day after 6 consecutive practice days" rule against the source. Explained the problems and fixes in words only; did not edit acclim.py.
- What I did: Disclosed which parts of acclim.py ChatGPT helped with. Fixed the returning-athlete bug myself.
- Files Claude edited (if any): AI_LOG.md.

## 2026-10-20: acclim fix check, Flet resources, PYTHONPATH
- Tool: Claude Code
- Problem: Wanted my returning-athlete fix in acclim.py checked; needed resources to learn Flet so I can build the UI with less AI help; scripts in daybyday/ failed with "ModuleNotFoundError: No module named 'core'".
- Claude's help: Re-ran the earlier scenarios against my fix (a returning athlete now restarts at day 1). Gave a Flet 1.0 learning path from the official docs (intro, Calculator tutorial, layout, async apps, 1.0 migration guide; later NavigationBar, Client Storage, Accessibility), plus a Home view to-do list and a Day 2 check plan in words. Explained why scripts in a subfolder can't find core/.
- What I did: Fixed the returning-athlete bug in acclim.py myself. Checked rules.json against its sources. Will build the UI myself from the docs, and will note any AI help with the UI here.
- Files Claude edited (if any): .vscode/settings.json (PYTHONPATH set to the project folder for VS Code terminals); AI_LOG.md.

## 2026-10-20: Home view (ChatGPT first version, then redone)
- Tool: ChatGPT
- Problem: Needed a layout for the Home screen (views/home.py).
- AI's help: ChatGPT built the first version of the Home layout. For my redo, it helped a little with colors and with where some blocks are placed in the layout.
- What I did: Implemented the first version with my core code, then redid views/home.py, about 90% myself. Wrote core/today.py (today's local-day hours, current hour, peak) and main.py myself.
- Files the AI wrote: first version of views/home.py (since replaced); color and layout-placement suggestions in the current views/home.py.

## 2026-10-20: Home view and today.py review
- Tool: Claude Code
- Problem: Asked Claude to check the Home view and core/today.py.
- Claude's help: Ran the Home data path against the live forecast and built the screen without opening a window. Pointed out: white-on-white peak category text on black days, a low-contrast label on the black card, sports region 2 still unconfirmed, raw error text shown to users. Flagged that my AI use was getting high. Explained in words only; did not edit app code.
- What I did: Wrote core/today.py; redid views/home.py, about 90% myself.
- Files Claude edited (if any): AI_LOG.md.

## 2026-10-21: Web deployment, Git and GitHub
- Tool: Claude Code
- Problem: Wanted the app online for community feedback, plus Git and GitHub. Flet's web server also crashed on my laptop with the openapi_prefix error, even on fastapi 0.148.
- Claude's help: Found that FastAPI removed openapi_prefix in 0.145.0, so 0.144.0 is the newest version that works with flet-web 1.0.4, and tested it in a throwaway folder before changing my environment. Checked that Vercel supports Python WebSockets, which Flet's web mode needs. Explained storage choices: no database; use Flet SharedPreferences, which stays on the user's device or browser. Created the deployment config, deployed to Vercel through my connected account (as the project's first deployment it went straight to the public address firstheat.vercel.app), set up Git and pushed to GitHub.
- What I did: Approved each change and created the GitHub repository.
- Files Claude edited (if any): app.py, pyproject.toml, .python-version, .vercelignore and .gitignore (all new, deployment/tooling only); requirements.txt (fastapi pin); CLAUDE.md (known issue 2 and tech stack). Also installed fastapi==0.144.0 in the firstheat env, ran git init, made the initial commit, pushed to github.com/TheSman122333/firstheat, and created the Vercel project "firstheat".

## 2026-10-21: Day 3 screens and core logic (ChatGPT)
- Tool: ChatGPT
- Problem: Building Settings (city search and saved settings), the Plan view and its core logic.
- AI's help: Minimal help with linting and small debugging across the Day 3 files. Conceptual help with how Settings should work and with the logic in core/plan.py (grouping hours by local day and finding lower-heat windows).
- What I did: Wrote the Day 3 code: navigation in main.py, storage.py, core/geocoding.py, core/plan.py, the location changes in core/today.py, views/settings.py, views/plan.py and the Home updates, plus the heat-wave cases in daybyday/day2check.py.
- Files the AI wrote: no whole files; only small fixes during linting and debugging.

## 2026-10-21: Day 3 review
- Tool: Claude Code
- Problem: Asked Claude to check the Day 3 work.
- Claude's help: Ran city search, today's summary and the 7-day plan for real cities (Phoenix and Honolulu) and built every screen without opening a window; checked the Flet 1.0 calls (SharedPreferences, Dropdown). Pointed out: the test-version note is still missing, raw error text is shown in three screens, there's no region reminder after changing city, the map link is unverified, core/today.py imports storage.py from outside core/, and the Plan shows a misleading message after 8 PM. Explained in words only; did not edit app code.
- What I did: Disclosed my ChatGPT use for Day 3.
- Files Claude edited (if any): AI_LOG.md.

## 2026-10-21: Acclimatization planner, project_week (ChatGPT)
- Tool: ChatGPT
- Problem: Needed to combine the acclimatization engine with the 7-day forecast so each future day shows a projected limit.
- AI's help: Helped structure project_week in core/planner.py (marked with a comment in the file).
- What I did: Wrote the rest of the Day 4 work: the My plan screen (views/my_plan.py) with attendance, reset and validation, saving the person in storage.py, the Weekly tab and navigation changes in main.py, the scroll fix, WBGT labels, ZIP search wording, the Region 1 default, and daybyday/day4check.py. Fixed the projection myself so projected double-practice days are followed by single-practice days.
- Files the AI wrote: parts of core/planner.py (project_week structure).

## 2026-10-21: Day 4 check script (ChatGPT)
- Tool: ChatGPT
- Problem: Needed a print-only script to check the planner's Day 4 cases.
- AI's help: Helped write daybyday/day4check.py (marked "AI USED" in the file).
- What I did: Chose the cases and the expected values (new worker, worked yesterday, returning worker, orange forecast, new athlete, athlete day 6, rest day, after rest day) and ran it against my planner.
- Files the AI wrote: parts of daybyday/day4check.py.

## 2026-10-21: Day 4 planning, scrolling bug and planner review
- Tool: Claude Code
- Problem: Planning the last days; screens couldn't scroll on some devices; questions about ZIP codes, automatic sports regions, and WBGT vs. heat index; asked Claude to check the planner.
- Claude's help: Committed and pushed Day 3. Checked my pinned packages against the OSV vulnerability database (certifi 2026.10.18 has a critical advisory, fixed in 2026.10.19; upgrade not done yet). Helped re-plan the week (Group view replaced by the planner; calibration and Spanish cut). Diagnosed the scrolling bug (SafeArea needed expand=True). Tested that Open-Meteo search accepts ZIP codes. Advised against automatic regions (the official map has no data file) and suggested defaulting to the most cautious region. Pointed out that the screens didn't say the numbers are WBGT. Ran the planner on made-up forecasts and found that projected athlete days allowed a double practice every day, plus raw error messages and no way to undo attendance. Explained in words only; did not edit app code.
- What I did: Made all the fixes and label changes myself.
- Files Claude edited (if any): AI_LOG.md. Also ran git commit/push for Day 3 and Day 4.

## 2026-10-22: Security alert fix and redeploy
- Tool: Claude Code
- Problem: GitHub reported a critical vulnerability: certifi 2026.10.18 included root certificates from an authority whose keys were compromised. Vercel logs also showed two visitors whose app never loaded (SharedPreferences.get timed out at startup).
- Claude's help: Upgraded certifi to 2026.10.19 (approved), re-checked all 59 pinned packages against the OSV database (no known vulnerabilities left), and confirmed the local web server still works. Redeployed the Day 4 commit from GitHub. Diagnosed the startup crash: storage.py doesn't catch the RuntimeError from a SharedPreferences timeout, so it should fall back to defaults. Reviewed the AI-assisted files again (planner.py, day4check.py, acclim.py, rules.py) and listed remaining issues in words only.
- What I did: Approved the certifi upgrade; I'm fixing the storage crash myself.
- Files Claude edited (if any): requirements.txt (certifi pin), pyproject.toml (certifi minimum version for Vercel), AI_LOG.md. Installed certifi==2026.10.19 in the firstheat env.
