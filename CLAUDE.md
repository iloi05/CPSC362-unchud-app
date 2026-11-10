# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Unchud (CPSC 362 class project): a student assignment tracker with a gamified avatar. Users add assignments manually (Canvas integration is planned). Completing an assignment earns "choin" currency to buy avatar accessories. The planned rule is that missing a deadline repossesses a random item from the user's inventory.

## Running

Windows only, because notifications use `win11toast`/`winrt`. There is no build step, linter, or test suite.

```powershell
pip install -r requirements.txt          # a venv lives in wvenv/ (and an old one is committed under .env/)
uvicorn back_unchud:app --reload         # run from the repo root
# then open http://127.0.0.1:8000/home
```

`main.py` is a stale CLI menu. It calls `Assignment` methods with no arguments and its menu numbers don't match its branches, so it doesn't work against the current backend. The web app is the real entry point.

## Architecture

**Backend: `back_unchud.py` (FastAPI, single file).**
- Importing the module creates the global `tracker = Assignment()` and `game = Game(tracker)`. It also starts a daemon thread that runs `schedule`, which fires `tracker.random_notif()` (a Windows toast) **every 10 seconds**. Any import of this module (uvicorn, `main.py`, a test) starts that thread.
- Assignments are saved to `%LOCALAPPDATA%\Unchud\assignments.json` (not in the repo) as `{"assignments": ..., "choin": n}`. `save_data()` runs after each change, and `load_data()` runs in `Assignment.__init__`.
- The assignment data is nested: `{class_name: {due_date "YYYY-MM-DD": {due_time "HH:MM AM/PM": [assignment_name, ...]}}}`. `GET /assignments` returns this dict as-is, and `front-unchud.js` flattens it by date for the calendar. If you change the shape, update both files.
- `Game` subclasses `Assignment` but reads and writes money through `self.tracker.choin`. Because it calls `super().__init__()`, it also loads its own copy of the data. The `catalog` maps slot (`headwear/face/body/pants/feet`) to rank (`SR/R/N`) to price. `p_inventory` lives only in memory and `buy()` doesn't call `save_data()`.
- Endpoints: `POST /add_assignment`, `POST /mark_assignment` (both take an `AssignmentData` body), `GET /assignments`, `POST /buy` (`GameData`), and `GET /home`. Methods return `{"success": bool, "message": str}` dicts rather than raising HTTP errors.
- `app.mount("/", StaticFiles(...Front_end_files))` is registered last so it doesn't shadow the API routes. Keep new routes above it.

**Frontend: `Front_end_files/` (plain HTML/JS, no framework or bundler).**
- `home.html` holds the inline CSS and the markup for the calendar and the avatar panel. It loads `/front-unchud.js` and `/avatar.js`.
- `front-unchud.js` renders the month calendar and reloads `/assignments` whenever the window gets focus.
- `avatar.js` draws the avatar by stacking 64×64 pixel-art PNGs from `/assets/` onto a canvas at 5× scale with smoothing off. The body choice is saved in `localStorage`. Clothing PNGs (`hat`, `shirt`, `pants`, `shoes`, `hair_*`) are in `assets/` but are not yet tied to the inventory.

## Known backend bugs (recent commits say "figure out why back end is not working")

- `check_time` uses `"%H:%M %p"`, but `convert` and `mark_assignment` parse with `"%I:%M %p"`, so the formats don't match.
- In `mark_assignment`, the late-completion branches compare `date.today()` with the string `due_date` and a `time` with the string `due_time`, which raises `TypeError`. It also indexes `[due_date][due_time]` without checking that those keys exist, which raises `KeyError`. The reward message prints the total balance instead of the amount earned.
