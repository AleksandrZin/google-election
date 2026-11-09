# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A Dash (Plotly) web dashboard that compares post–2024 US election Google Trends interest in two search terms ("Can I change my vote?" → `Interest_1`, "Change vote presidential election" → `Interest_2`) between red and blue states, and runs Welch's two-sample t-test (unequal variances) on them. Deployed on PythonAnywhere (https://aleksandrzin.pythonanywhere.com).

## Commands

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python dashboard.py        # dev server (debug=True) at http://localhost:5000
python scrap_script.py     # regenerate data/geo_df.csv (re-scrapes Reuters) and data/tl_df.csv
python scrap_script.py --timeline-only   # regenerate only data/tl_df.csv, no network
```

Both scripts use paths relative to the current directory (`data/...`), so run them from the repo root. There is no test suite, linter config, or build step.

## Architecture

Two-stage pipeline: an offline data-prep script produces processed CSVs, and the dashboard only reads those CSVs.

- **`scrap_script.py`** (offline): scrapes vote percentages from the Reuters results page, maps state names via `data/raw/state_short2long.json` → `state_long2abr.json`, and computes a `Winner` column (`build_geo_df`). Google Trends exports are named `GT_<region|timeline>_<can|president>_US_<start>_<end>.csv`, in two sets with different formats. `data/raw/GT_2024/` (3 header lines, read by `load_map_df`/`load_timeline_df`) is the set actually used for both the region data and the timeline (`build_timeline_df`). It was downloaded in November 2024, so the timeline ends on 2024-11-13: that is the last day of data available then, and the "can i change my vote" curve is still near its peak at the end. `data/raw/GT_2026/` (1 quoted header line, re-downloaded 2026-11-09) is kept for reference only and is not used. Its region files cover too few states. The script writes:
  - `data/geo_df.csv` — one row per state: `Abbreviation, State, Democrat, Republican, Interest_1, Interest_2, Winner`
  - `data/tl_df.csv` — daily timeline: `Date, Interest_1, Interest_2`
- **`src/utils.py`**: loads the processed CSVs and `data/us-states.json` (GeoJSON) **at import time into module-level globals** (`states`, `geo_df`, `tl_df`; `tl_df` is melted to long format `Date, Question, Interest`). All figure builders (`create_timeline_plot`, `create_map_plot`, `create_scatter_plot`, `create_box_plot`) and `welch_ttest` read these globals rather than taking dataframes as arguments.
- **`dashboard.py`**: builds the layout (four tabs: Timeline, Map, Result, Caveats; Caveats is static text) and the `@callback`s that call into `utils`. The Dash app is mounted on an explicit Flask `server` object, which is what the WSGI deployment imports. `assets/bootstrap.css` is picked up automatically by Dash's `assets/` folder convention and provides the Bootstrap classes used via `dash_bootstrap_components`.

Column names (`Interest_1`, `Interest_2`, `Democrat`, `Republican`) double as the radio-button `value`s in the UI and are passed straight through callbacks as dataframe column names, so renaming a column requires updating the scraper, utils, and the dashboard options together.
