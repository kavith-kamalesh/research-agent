# ARC — Personal Stress / Rumination Tracker (Local)

A private, local-only tool for tracking stress and rumination patterns
through daily check-ins. Runs entirely on your machine — nothing is sent
anywhere except loading the Chart.js CDN script for graphing (optional).

## What this is NOT
- Not a hormone, cortisol, or brain-chemistry measurement.
- Not a diagnosis of depression, anxiety, or anything else.
- Not a replacement for a doctor or therapist.

Every score in this app is a self-report or word-frequency signal, fully
traceable to a named method. Nothing here outputs a clinical verdict.

## What it is

- **Daily check-in** (card-stack UI): a journal entry (with voice-to-text via
  Chrome's Web Speech API), an activity context tag, a rumination slider, a
  body-signals slider, and a small protective-habits checklist inspired by
  *The Upward Spiral* (Alex Korb) — tracked as actions taken, not scored
  against the book itself.
- **A 0–100 index** per entry, combining:
  - Self-report (RRS-style rumination question): 40–50%
  - Somatic/body checklist: 20–25%
  - Text signal (word-frequency scan — absolutist, negative-emotion,
    past-focus, somatic words): 20–25%
  - Protective habits (inverted — more protective actions taken pulls the
    index down): 20%, when logged
  - Exact weights and reasoning are in `combine_index()` in `app.py`.
- **Weekly deeper screenings**, separate from the daily index:
  - **PHQ-9** — standard public-domain depression screening questionnaire,
    with the real published scoring bands. Item 9 (self-harm/suicidal
    ideation) is checked independently and always surfaces a crisis message
    if flagged, regardless of total score.
  - **GAD-7** — standard public-domain anxiety screening questionnaire, same
    scoring approach.
  - Both are screening signals only — the app never outputs a diagnosis.
- **Crisis-keyword safety net** — certain phrases in journal text trigger a
  real crisis-line message (India: KIRAN, iCall).
- **Obsidian export** — every check-in is also written as a markdown note
  with frontmatter (index, subscores, habits, tags) into an Obsidian vault
  on your Desktop, so you can browse/graph/link entries in Obsidian itself.
- **Incidents log** — add past/present events gradually, not all at once.
- **Trend graph** and recent check-ins list on the dashboard view.

## Setup

1. Install Python 3.10+.
2. From this folder:

```bash
python3 -m venv venv
source venv/bin/activate
pip install flask
python3 app.py
```

3. Open **http://127.0.0.1:5000** (or whichever port you run it on).
4. Use **Chrome** for voice-to-text.

`/` serves the card-stack check-in flow. `/dashboard` serves the older
graph/history dashboard view. Both share the same backend and database.

## Data & privacy

- All data lives in `data.db` (SQLite) in this folder — gitignored, never
  committed. Delete it to reset everything.
- The Obsidian export writes to `~/Desktop/Rumination-Journal` by default —
  change `VAULT_PATH` in `app.py` if you want a different location.
- No accounts, no cloud sync, no analytics.

## Notes on the scoring (so it stays honest)

- **RRS-style**: item content drawn from Nolen-Hoeksema's Ruminative
  Response Scale themes. `score_self_report()` in `app.py`.
- **PHQ-9 / GAD-7**: public-domain instruments, standard clinical scoring
  and published interpretation bands, applied exactly as published — not
  invented. `score_phq9()` / `score_gad7()`.
- **Text sub-score**: word-category frequency (per 100 words) across four
  hand-built word lists — fully visible/editable in `app.py`, not a
  licensed LIWC dictionary, just LIWC-inspired categories.
- **Habits checklist**: informed by *The Upward Spiral*'s described
  mechanisms (gratitude, decision-making, movement, social contact, sleep
  regularity, naming rumination) — the book determines *what* is tracked;
  the weighting in the index is this project's own stated choice, not
  attributed to the book as if it were the book's formula.

Everything is plain Python/HTML/JS — no build step. Edit word lists,
question wording, or weights directly in `app.py` and the templates.

## If you're building on this

If you're picking this up to extend it, please keep the guardrails intact:
- Never claim to measure hormones or brain chemistry, or output a
  diagnosis — index and screening bands only, never a verdict.
- Keep the crisis-keyword detection and hotline messaging visible and
  functional, including the PHQ-9 item-9 check.
- Keep scoring traceable to named, real methods rather than an
  unexplainable model.
