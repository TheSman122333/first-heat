# AI Use Log

## Summary (updated 2026-10-25)

FirstHeat was built in two stages. The dated entries below give the details.

**My work in the core files (Stage 1).** I wrote most of FirstHeat's core, and these files are unchanged in the redesign:
- core/wbgt.py: the hourly WBGT estimate, using the lwbgt library (Liljegren method) with UTC time handling.
- core/weather.py: Open-Meteo forecast and archive requests, with input checks and error handling.
- core/acclim.py: the acclimatization engine: Person and Session data, the NIOSH schedules for new and experienced workers, heat-wave counting and the stricter-limit rule, athlete practice limits and regional heat caps, and the plan dispatcher. I found and fixed the returning-athlete bug. (ChatGPT helped with break detection, the athlete day logic and input checks.)
- core/planner.py: today's limit and the projected limits beside the 7-day forecast, including the rest-day and double-practice fixes. (ChatGPT helped structure project_week.)
- core/today.py and core/plan.py: today's local hours, current hour and peak; seven local days and lower-heat windows.
- core/geocoding.py: US city and ZIP code search.
- storage.py and main.py: saved settings and attendance with validation, the startup storage fix, and navigation.
- The first versions of the Home, Settings, Plan, My plan, Emergency and developer screens, and the day-by-day check scripts (with the AI help listed in their entries).

Today about 1,190 of the 1,436 lines in core/ are Stage 1 code (including the ChatGPT parts listed in the entries).

1. **Stage 1, Days 1–5 (Oct 19–22, commits up to 04ec278): the core app.** I built this stage. ChatGPT wrote data/rules.json and most of core/rules.py, and helped with parts of core/acclim.py, core/planner.py, views/emergency.py, views/developer_mode.py and the check scripts. Claude Code helped with debugging, reviews, environment and tooling, and deployment. Each entry lists exactly what the AI wrote.
2. **Stage 2, interface redesign (Oct 22–25, every commit after 04ec278): code written by Claude Code, directed by me.** This stage redesigned the interface and added features on top of my Stage 1 app. It did not replace or rewrite my work. I decided what to change and how each screen should look and read, described each change, and reviewed it on the live site. Claude Code wrote the code: the redesigned Home, Forecast and My Plan screens, the activity tracker with break reminders, the current conditions tiles, the on-site reading features, the logo, and the safety disclaimer and legal text. Git shows these commits with "Claude" as the author.

All of my Stage 1 work is kept. Claude Code did not write or change the core calculations; its additions to core/ are only the data the new features needed (core/conditions.py, and small helper functions in core/rules.py, core/today.py and core/plan.py). What stayed the same from stage 1: the WBGT calculation (core/wbgt.py), the weather fetch (core/weather.py), the acclimatization engine (core/acclim.py), the 7-day planner (core/planner.py), city search (core/geocoding.py), and the heat thresholds in data/rules.json. The redesign only added to core/rules.py, core/today.py, core/plan.py, storage.py and data/rules.json; it did not change the existing logic or numbers.

Size of the redesign (git diff from 04ec278 to af7444f): in core/, about 240 of the 1,440 lines are Claude Code's (all of core/conditions.py plus small additions). In views/, the interface, about 3,700 of the 4,700 lines are Claude Code's. In total the Python code grew from about 2,900 to about 6,500 lines. These counts are approximate, since blank lines and moved lines count as changes.

## Commit history
- **Stage 1: 6 commits (Oct 21–22, 8f12a56 to 04ec278), author swqg-messiah (me).** They are the same commits as in my Day 1–5 repository (TheSman122333/firstheat). They also list "Co-Authored-By: Claude" because Claude Code ran the git commands for me and edited the setup files named in the entries below; the app code in them is mine, apart from the ChatGPT parts listed.
- **Stage 2: one commit per redesign change (Oct 22–25), author "Claude", starting right after 04ec278.**

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

## 2026-10-22: Emergency screen and developer mode (ChatGPT)
- Tool: ChatGPT
- Problem: Needed the Emergency mode (911, heat stroke steps, timer, EMS log) and a developer mode for simulated testing.
- AI's help: Assisted with views/emergency.py and views/developer_mode.py (both marked "ASSISTED BY AI" in the files).
- What I did: Checked the emergency wording against the CDC/NIOSH and KSI sources; added both screens to the app in main.py (Emergency tab, Home shortcut, developer mode inside Settings); fixed the storage startup crash in storage.py and the "Rest day" label in core/planner.py.
- Files the AI wrote: parts of views/emergency.py and views/developer_mode.py.

## 2026-10-22: Day 5 check
- Tool: Claude Code
- Problem: Asked Claude to check and push the Day 5 work.
- Claude's help: Compiled every file; confirmed the Flet 1.0 APIs used exist (Button.action, CopyToClipboard, OpenUrl, Wakelock, HapticFeedback, an icon control in NavigationBar); ran developer mode on simulated cases (black, red, green, worker, invalid input); confirmed day4check now shows "Rest day"; checked the source links; confirmed the local web server builds the app. Explained in words only; did not edit app code.
- What I did: Wrote the fixes and integration listed above.
- Files Claude edited (if any): AI_LOG.md. Also ran git commit/push.

## 2026-10-22: Day 5 deployment and live check
- Tool: Claude Code
- Problem: Needed the Day 5 version (Emergency, developer mode, storage fix) live for testers, without risking a broken site.
- Claude's help: Before deploying, ran the app's web server locally with a stand-in browser client in two scenarios (browser storage failing the way the Vercel logs showed, and a normal new visitor) and confirmed the app starts and builds every screen in both. Deployed commit 0f270c9 from GitHub to firstheat.vercel.app, then opened a real session against the live site (Home showed live WBGT; all five tabs and the CALL 911 shortcut loaded) and confirmed Vercel showed no runtime errors.
- What I did: Approved the deployment; sharing the link with coaches and athletes for feedback.
- Files Claude edited (if any): AI_LOG.md. Test scripts were kept in Claude's scratch folder, outside the project.

## 2026-10-22: Redesign repository and Vercel project
- Tool: Claude Code
- Problem: Wanted to redesign the app's interface and add features without risking the working Day 5 app.
- Claude's help: Copied the project at commit 04ec278 into a new repository (now TheSman122333/first-heat) and a new Vercel project (now first-heat.vercel.app). The Day 1–5 repository was not changed. From here on, Claude Code wrote the interface and new-feature code in this repository; my core files stayed as they were.
- What I did: Asked for the copy and decided to have Claude Code write the redesign code from my directions. The redesign entries below were written on 2026-10-24 from the commit history.
- Files Claude wrote or edited: CLAUDE.md.

## 2026-10-22 to 2026-10-23: Interface redesign
- Tool: Claude Code
- Problem: Wanted a more visual, easier-to-read app.
- Claude's help: Wrote the code for every change I asked for:
  - Logo, two-tone wordmark and tagline ("Your adaptive heat-safety planner").
  - Home: a large heat-stress number colored by category, with an activity illustration behind it; an hourly 6 AM–10 PM chart in the category colors; the emergency button shown only for Orange, Red and Black.
  - Simulate a Session moved to Home, with color sliders, an intensity setting and a visual result report.
  - Forecast tab: graphical 7-day bars and a chart for each day.
  - My Plan: interactive redesign with profile sliders, a tappable 7-day bar chart with dates and done check marks, and a dial for each day.
  - Brand header on Emergency and Settings, and a full-width CALL 911 button.
  - Time zone labels; Open-Meteo and guideline links moved to Settings.
- What I did: Described each change in my own words, reviewed it on the live site, and asked for adjustments.
- Files Claude wrote or edited: views/home.py (most of the current file), views/plan.py (most), views/my_plan.py (most), views/developer_mode.py (most), views/emergency.py, views/settings.py, main.py; new files views/brand.py, views/peak_chart.py and views/sliders.py; assets/ (logo and icons drawn by Claude; activity illustrations from unDraw, license in assets/activity/LICENSE.md); app.py (assets folder); core/today.py and core/plan.py (also return each hour's values and the region's thresholds for the charts).

## 2026-10-23: Safety disclaimer and About & legal
- Tool: Claude Code
- Problem: Asked what terms and privacy statements an app like this should have, then asked for a first-launch disclaimer and an About & legal section.
- Claude's help: Recommended what to include, then wrote the disclaimer, privacy notice, terms of use and credits, the first-launch dialog, and saving the accepted version on the device.
- What I did: Asked for the text and set the effective year to 2026. This is not legal advice; I still need to review the wording.
- Files Claude wrote or edited: views/legal.py (new), views/settings.py, main.py, storage.py (load_disclaimer, save_disclaimer).

## 2026-10-23: On-site WBGT reading and "could be higher" flags
- Tool: Claude Code
- Problem: Wanted users to enter an on-site WBGT meter reading in place of the estimate, and wanted estimates within about 1°F of the next category flagged.
- Claude's help: Wrote the reading card on Home (32–120°F, expires after 60 minutes), the could-be-higher check, and the flags on Home and Forecast. Later made the reading also shift today's chart and peak by its difference from the estimate.
- What I did: Asked for these features and reviewed them.
- Files Claude wrote or edited: core/rules.py (next_category_if_close), data/rules.json (caution_margin_f and caution_note), views/home.py, views/plan.py.

## 2026-10-23: Activity tracker with break reminders
- Tool: Claude Code
- Problem: Wanted My Plan to time today's activity, sound a break reminder at the recommended interval that lasts 30 seconds, count taken vs. ignored reminders, and show them on the day's dial.
- Claude's help: Wrote the tracker card (timer, progress against today's limit, reminders with a sound and vibration, taken/missed counts) and saving so a reconnect can resume. Set the reminder spacing from the existing guidance text in rules.json: three breaks per hour means one every 20 minutes, four per hour means one every 15 minutes. Added the green logged band and the green/red reminder dots to the dial. Later fixed a server error when the browser tab closed while the timer was running.
- What I did: Asked for the feature, tested it on the live site, and asked for the dot placement.
- Files Claude wrote or edited: views/tracker.py (new), views/my_plan.py, storage.py (tracker saving and the optional reminder counts on logged days), core/rules.py (break_schedule), data/rules.json (break_schedule and break_note), assets/index.html and assets/reminder-sound.js (new; play the sound in the browser).

## 2026-10-23: Demo reminder settings (temporary)
- Tool: Claude Code
- Problem: Needed to demo reminders without waiting 15–20 minutes.
- Claude's help: Added a "Reminder settings (DEMO)" card in Settings to set the reminder interval (15 seconds to 20 minutes), break length, and how long a reminder stays up.
- What I did: Asked for it for my demo; it is temporary and will be removed.
- Files Claude wrote or edited: views/demo_reminders.py (new), views/settings.py, views/tracker.py.

## 2026-10-23: Current conditions tiles, heat stress label, city and time zone
- Tool: Claude Code
- Problem: Wanted air temperature, humidity, UV index and air quality under the heat-stress number; the city name in the tile; the time zone next to the time; and clearer wording than "WBGT".
- Claude's help: Wrote core/conditions.py (Open-Meteo forecast and air-quality data for the current hour, EPA UV and AQI levels) and the four tiles. Changed the label to "Heat stress (WBGT)" with the time zone. Renamed "Today's peak" to "Today's WBGT index". Removed the SIMULATED labels and the Run simulation button from Simulate a Session. Added credits for Copernicus CAMS and the EPA scales.
- What I did: Asked for these changes, chose the wording and colors, and reviewed them.
- Files Claude wrote or edited: core/conditions.py (new), views/home.py, views/developer_mode.py, views/legal.py.

## 2026-10-23 to 2026-10-24: Explanations and AI-use review
- Tool: Claude Code
- Problem: Questions: what makes up WBGT; how much of the code is reused vs. AI-written; whether the redesign's backend matches the Day 5 version; how the Congressional App Challenge AI rules apply.
- Claude's help: Explained the three WBGT parts (natural wet bulb, black globe and air temperature, weighted 0.7 / 0.2 / 0.1) and how my wbgt.py estimates them with lwbgt. Measured the AI-written share of the code. Compared this repository with the Day 1–5 version (the calculation files are identical; the rest are additions). Looked up the 2026 CAC rules on AI use (full disclosure, AI supports specific aspects and is not the entirety of the work, students explain their contributions and understand how the project and its code work). Wrote this summary and the redesign entries.
- What I did: Decided to submit this repository and asked Claude to update this log.
- Files Claude wrote or edited: AI_LOG.md.

## 2026-10-25: Cover image
- Tool: Claude Code
- Problem: Needed a 600x800 JPEG cover image for the Congressional App Challenge submission.
- Claude's help: Designed the cover: the FirstHeat logo, name and tagline, three feature highlights, and a phone showing a screenshot of this app's Home screen. The screenshot was taken from the app running locally with sample weather data, because the session couldn't reach the live weather service.
- What I did: Asked for the cover and chose to show this repository's version of the app.
- Files Claude wrote or edited: AI_LOG.md. The cover image itself is not in the repository.

## 2026-10-25: Cleanup before submission
- Tool: Claude Code
- Problem: Getting the repository ready to submit.
- Claude's help: Updated CLAUDE.md, renamed the Vercel project and moved the site to first-heat.vercel.app (the old addresses redirect there), and updated this log.
- What I did: Chose the new name, renamed the GitHub repository, and reviewed this log.
- Files Claude wrote or edited: CLAUDE.md, AI_LOG.md.
