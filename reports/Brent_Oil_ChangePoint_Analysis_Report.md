# Brent Oil Price Analysis: Progress Report

*From data exploration and Bayesian change point modeling to an interactive dashboard—with remaining work outlined in Chapter 4.*

---

Brent Crude Oil isn’t just a commodity—it’s a barometer of global politics, supply shocks, and economic sentiment. This project takes **35 years of daily Brent prices (1987–2022)** and answers a deceptively simple question: *when did the rules of the game actually change?*

This document is a **progress report**. Chapters 1–3 describe what has been completed so far: **exploring** the data and flagging major events, **modeling** structural breaks with Bayesian inference, and **communicating** results through an interactive dashboard. Chapter 4 outlines **remaining tasks**, including unit tests, GitHub Actions (CI/CD), and insights and recommendations. Each chapter is organised with sections and subsections for easy reference.

---

# Chapter 1 — Data Exploration & Event Detection

The first step is to get the data in shape and understand what we’re working with. Only then can we decide which “events” are worth modeling and sharing with stakeholders.

## 1.1 Why Start with the Data?

Raw numbers alone don’t tell a story. Prices come with messy dates, gaps, and mixed units. Before any modeling, we need a **clean, validated** series and a clear view of **trends, volatility, and returns**. That’s what Task 1 delivers: a reproducible pipeline from raw CSV to a curated list of candidate events.

## 1.2 Loading and Cleaning the Raw Data

### 1.2.1 The Dataset

The primary source is **Brent Oil Prices** (e.g. Kaggle): daily observations from May 1987 onward. The file typically has two columns—**Date** and **Price**—but date formats can vary (e.g. `20-May-87` vs `Apr 22, 2020`), which can break naive parsers.

### 1.2.2 Robust Loading

The project uses a dedicated loader that:

- Strips whitespace from column names and date strings.
- Parses dates with a flexible strategy (e.g. `pd.to_datetime(..., errors="coerce", dayfirst=True)`).
- Converts **Price** to numeric and drops or flags invalid rows.
- Sorts by date ascending and validates that required columns exist.

Invalid or missing dates/prices raise clear errors so the pipeline fails fast instead of silently corrupting downstream steps.

### 1.2.3 Validation and Sorting

After parsing, the pipeline checks for missing or non-positive prices. The result is a single **Date**–**Price** series, sorted in time, ready for aggregation and returns.

## 1.3 Exploratory Data Analysis (EDA)

### 1.3.1 Price Levels and Trends

A natural first step is to plot **price over time**. We look for long-run trends (e.g. the run-up in the 2000s, the 2008 and 2020 crashes) and any obvious structural shifts. EDA is documented in the foundations notebook and sets the narrative for later modeling.

### 1.3.2 Volatility and Regime Changes

Volatility often shifts around crises. Simple rolling standard deviations or squared returns help identify **calm vs turbulent** periods. These visuals inform both the choice of events and the interpretation of the Bayesian change point later.

### 1.3.3 Log Returns

For modeling, we work with **log returns**: log(Price_t / Price_{t-1}). They are time-additive, symmetric for gains and losses, and better behaved for Gaussian-style models. The preprocessing step computes log returns and optionally aggregates (e.g. weekly or monthly) to reduce noise and runtime.

## 1.4 Detecting Major Events

### 1.4.1 The Idea of “Event” Detection

An “event” here is a **large move** in the series—e.g. an extreme log return—that might correspond to a geopolitical or economic shock. We don’t label events by hand first; we use **statistical thresholds** (e.g. beyond ±2 standard deviations of log returns) to flag candidate dates.

### 1.4.2 Threshold-Based Detection

By defining a threshold (e.g. 2σ or 3σ of historical log returns), we get a list of dates where the market moved unusually. These become the **10–15 major events** we export and later try to align with the Bayesian change point.

### 1.4.3 From Detection to Export

The detected events are written to **`detected_events.csv`** in `data/processed/`. Each row typically includes at least: date, magnitude of the move, and optionally a short label. This file feeds both the short Task 1 report and the dashboard’s “event highlight” view.

## 1.5 Deliverables for Task 1

- **`foundations.ipynb`** (or equivalent EDA notebook): documents loading, cleaning, EDA, and event detection.
- **`detected_events.csv`**: 10–15 statistically detected major events.
- **1–2 page PDF report**: summary of data quality, main trends, volatility, and how events were chosen.

With this, we have a data-driven, auditable basis for the next step: modeling *when* the regime actually changed.

---

# Chapter 2 — Bayesian Change Point Modeling

Once we have clean data and a list of candidate events, we want to **quantify** structural breaks: not just “something happened,” but *when* it happened and *how strong* the impact was. That’s where Bayesian change point modeling comes in.

## 2.1 What Is a Change Point?

### 2.1.1 Definition

A **change point** is a time index at which the **statistical properties** of the series (e.g. mean or variance) shift. Before that point, the process follows one “regime”; after it, another. For Brent oil, a change point is a **structural break** in price behavior—often aligned with wars, recessions, or supply decisions.

### 2.1.2 One vs Many Change Points

In principle there could be many change points. For clarity and stability, this project focuses on **one major structural change** (or a small number in extended versions). The same ideas scale to multiple τ’s with a more complex model.

## 2.2 Why Bayesian?

### 2.2.1 Uncertainty Over a Single Date

Classical methods often give a single “best” change point date. Bayesian inference gives a **full posterior distribution** over the change point τ: we can say “there is a 95% probability the break occurred between date A and date B.” That’s directly useful for investors and policymakers.

### 2.2.2 Priors and Interpretability

We can encode weak prior beliefs (e.g. mean log return near zero, bounded volatility). The posterior then combines data and prior, and we get **interpretable parameters**: mean log return before (μ₁) and after (μ₂) the break, plus uncertainty on all of them.

### 2.2.3 MCMC and Posterior Summaries

We use **Markov Chain Monte Carlo (MCMC)**—e.g. PyMC’s NUTS sampler—to draw samples from the posterior. From those samples we compute medians, credible intervals, and probabilities. No closed-form math is required; the computer does the integration.

## 2.3 The Model in Plain Language

### 2.3.1 The Switch Point τ

**τ (tau)** is the unknown time index where the regime switches. We put a **discrete uniform prior** on τ over all valid indices (e.g. 0 to n−1). The data then “vote” for which τ is most plausible.

### 2.3.2 Means Before and After: μ₁ and μ₂

- **μ₁**: mean log return *before* the change point.  
- **μ₂**: mean log return *after* the change point.  

Each gets a prior (e.g. Normal centered at 0 with moderate variance). The difference **μ₂ − μ₁** tells us the **direction and size** of the structural shift.

### 2.3.3 Volatility σ

We typically assume a single **σ** (standard deviation) for the log returns, with a prior that keeps it positive (e.g. HalfNormal). In fancier versions, σ could also switch at τ.

### 2.3.4 The Likelihood and the Switch

For each time t, the *expected* log return is μ₁ if t is before τ and μ₂ if t is at or after τ. We implement that with a **switch** (e.g. pm.math.switch in PyMC). The observed log returns are then modeled as Normal with mean μ and standard deviation σ. That’s the likelihood; the rest is sampling.

## 2.4 Implementation and Sampling

### 2.4.1 PyMC Model

The project implements this in **PyMC**: define the model (priors + likelihood), then call `pm.sample()` with a sensible number of draws, tune steps, and chains. To keep runtimes manageable (e.g. under a few minutes), the notebook often uses **aggregated** data (e.g. weekly) and moderate MCMC settings.

### 2.4.2 What We Get From the Trace

After sampling we have:

- **Posterior of τ**: distribution over the change point index (convert to dates using the time index).
- **Posterior of μ₁, μ₂**: distributions over mean log return before and after.
- **Posterior of σ**: distribution over volatility.

From these we build a **change point report**: MAP or median τ, mean before/after, delta, percent change, and a simple “confidence” (e.g. fraction of samples at the MAP τ).

## 2.5 Interpreting the Results

### 2.5.1 Reading the Posterior of τ

- **Narrow posterior** → high certainty about when the break occurred.  
- **Wide posterior** → uncertainty; the data support a range of dates.  

Both are useful: narrow suggests a clear event; wide suggests either diffuse information or multiple competing shocks.

### 2.5.2 Reading μ₁ and μ₂

The **magnitude of μ₂ − μ₁** indicates how strong the structural shift was. Positive means average returns increased after the break; negative means they decreased. Credible intervals show how precise that estimate is.

### 2.5.3 Linking to Historical Events

We compare the posterior distribution of the change point date to **known events** (e.g. from Task 1’s `detected_events.csv` or from history). When the posterior clusters near a major event (e.g. 2008 financial crisis, COVID-19), we can tell a coherent story: “The model identifies a structural break consistent with ….”

## 2.6 Deliverables for Task 2

- **`modelling.ipynb`**: full pipeline from data load → preprocessing → PyMC model → sampling → report and export.
- **Posterior plots**: τ, μ₁, μ₂ (and optionally σ) with credible intervals.
- **Written interpretation**: what the change point date means, how it aligns with events, and what the magnitude of the break implies.

This sets us up to serve the same insights through an API and a dashboard—Task 3.

---

# Chapter 3 — Interactive Dashboard

The final step is **communication**. Analysts and stakeholders need to explore historical prices and change points without opening a notebook. Task 3 delivers a **backend API** and a **React frontend** that do exactly that.

## 3.1 Goals of the Dashboard

### 3.1.1 Who It’s For

The dashboard is for **investors, policymakers, and analysts** who want to:

- See Brent price history at a glance.  
- Filter by date range.  
- See where change points (and optionally detected events) fall on the timeline.  
- Get a feel for volatility and structural breaks without running code.

### 3.1.2 Core Features

- **Historical price trends**: line chart of Brent price over time.  
- **Date range filters**: focus on specific periods (e.g. 2005–2015).  
- **Change points and events**: overlay of detected change points and/or event list.  
- **Simple, responsive UI**: built so it works on different screen sizes.

## 3.2 Architecture Overview

### 3.2.1 Backend: FastAPI

The project uses **FastAPI** (not Flask) for the API: it’s fast, auto-documents endpoints (OpenAPI), and handles JSON and CORS easily. The app runs with **uvicorn** (e.g. on port 8000) and mounts an API router under `/api`.

### 3.2.2 Frontend: React + Vite

The UI is a **React** app bundled with **Vite**. It uses **React Router** for navigation and **Recharts** for the price line chart. Components are organized by view: Home, Price Chart, Event Highlight.

### 3.2.3 Data Flow

- The frontend calls the backend (e.g. `http://127.0.0.1:8000/api/...`).  
- The backend reads from **`data/raw/BrentOilPrices.csv`** and **`data/processed/detected_events.csv`** (or equivalent).  
- No database is required for this scope; CSV is the source of truth produced by the notebooks and `src` pipeline.

## 3.3 API Design

### 3.3.1 Historical Prices

**Endpoint:** `GET /api/historical_prices`

- **Purpose:** Return all (or a subset of) historical Brent prices for plotting.  
- **Response:** JSON array of objects with at least `Date` (e.g. ISO string) and `Price`.  
- **Implementation:** Read raw CSV, parse dates, format for frontend, handle missing/invalid rows.

### 3.3.2 Change Points

**Endpoint:** `GET /api/change_points`

- **Purpose:** Return detected change points (and optionally event metadata).  
- **Response:** JSON array with fields such as date, mean before/after, and any labels.  
- **Implementation:** Read from `detected_events.csv` (or a CSV produced by the modeling pipeline). Column names in the CSV and in the API response should be aligned so the frontend can show dates and metrics consistently.

## 3.4 Frontend Structure

### 3.4.1 Routes and Pages

- **Home:** landing or overview.  
- **Price Chart:** historical prices + date filters + line chart (Recharts).  
- **Event Highlight:** view focused on change points/events on the timeline.

Navigation is handled by React Router so users can bookmark or share specific views.

### 3.4.2 Key Components

- **PriceChart:** fetches `/api/historical_prices`, applies start/end date filters, and renders a responsive line chart.  
- **Filters:** date pickers (or inputs) that call back to the parent with `startDate` and `endDate`.  
- **EventHighlight:** fetches `/api/change_points` and overlays or lists events relative to the price series.

### 3.4.3 Styling and UX

The app uses basic layout and typography (e.g. Tailwind-style or custom CSS) so the chart and filters are clear. Tooltips and axis labels help users read exact values and dates. “Loading…” states improve perceived performance while data is fetched.

## 3.5 Aligning Backend and Pipeline Outputs

The modeling pipeline (e.g. `analysis_utils.export_detected_event_csv`) exports columns such as **Date**, **MeanBefore**, **MeanAfter**, **Delta**, **PercentChange**, **Confidence**. The API may expect slightly different names (e.g. **ChangePoint**, **StdDev**). Keeping **one canonical CSV schema** and having both the export function and the API use it (or a thin mapping layer) avoids 404s or empty charts and keeps the dashboard in sync with the notebooks.

## 3.6 Deliverables for Task 3

- **Fully functional backend:** FastAPI app with CORS, serving historical prices and change points.  
- **Fully functional frontend:** React app with routing, filters, and interactive price + event visualizations.  
- **README (or equivalent):** how to install dependencies, run the backend, run the frontend, and (optionally) build for production.

---

# Chapter 4 — Remaining Tasks

The core analysis and dashboard (Chapters 1–3) are in place. The following work remains to harden the project, automate quality checks, and formalise insights for stakeholders.

## 4.1 Unit Tests

### 4.1.1 Purpose

Unit tests verify that individual functions and modules behave correctly in isolation. They catch regressions when code changes and document expected behaviour. For this project, tests should cover the data pipeline, the Bayesian model interface, and the analysis utilities.

### 4.1.2 Suggested Scope

- **Data loading:** Test that `load_brent_data` correctly parses valid CSV, handles missing files, and raises clear errors for invalid dates or prices. Include fixtures with mixed date formats (e.g. 20-May-87 and 2020-04-22).
- **Preprocessing:** Test `prepare_model_data` for correct log-return calculation, optional aggregation (daily, weekly, monthly), and validation (e.g. rejection of non-positive prices).
- **Model and analysis:** Test that `run_bayesian_change_point_model` returns a dict with the expected keys (trace, summary, tau_posterior) and that `build_change_point_report` and `export_detected_event_csv` produce consistent outputs for a small synthetic dataset.
- **API (optional):** Test FastAPI endpoints with mock or sample CSV data to ensure `/api/historical_prices` and `/api/change_points` return valid JSON and correct status codes.

### 4.1.3 Deliverable

A test suite (e.g. using pytest) under a `tests/` directory, runnable with a single command (e.g. `pytest`), with clear pass/fail reporting.

## 4.2 GitHub Actions (CI/CD)

### 4.2.1 Purpose

Continuous integration (CI) runs the test suite and other checks on every push or pull request. Continuous deployment (CD) can optionally build or deploy the dashboard when the main branch is updated. This keeps the repository maintainable and prevents broken code from being merged.

### 4.2.2 Suggested Workflow

- **Trigger:** On push and pull requests to main (and optionally other branches).
- **Jobs:**
  - **Install dependencies:** Set up Python (e.g. 3.10 or 3.11), create a virtual environment, install project dependencies (e.g. from requirements.txt or pyproject.toml).
  - **Run tests:** Execute the unit test suite (pytest). Fail the workflow if any test fails.
  - **Optional:** Run linting (e.g. ruff, flake8, or pylint) and type checking (e.g. mypy) if adopted.
  - **Optional (frontend):** A separate job to install Node dependencies and build the React app, to catch frontend breakages.
- **Artifacts (optional):** Store test reports or coverage reports for visibility.

### 4.2.3 Deliverable

A GitHub Actions workflow file (e.g. `.github/workflows/ci.yml`) that runs on every relevant push/PR and reports status in the GitHub UI. Documentation in the README on how to run the same checks locally.

## 4.3 Insights and Recommendations

### 4.3.1 Purpose

The analysis produces change point dates, before/after means, and event lists. Stakeholders need a concise **narrative**: what the main findings are, how they relate to real-world events, and what actions or further analysis are recommended. This section is the placeholder for that narrative.

### 4.3.2 Suggested Content

- **Summary of findings:** One or two paragraphs on the most important change points identified (e.g. “The model identifies a structural break around [date], consistent with [event]. Mean log return shifted from X to Y, indicating …”).
- **Link to events:** A short table or list mapping detected change point dates to known geopolitical or economic events (e.g. 2008 financial crisis, COVID-19, OPEC decisions). This can live in the report, in the docs, or in the dashboard as tooltips or a sidebar.
- **Limitations:** Brief statement of assumptions (e.g. single change point, Gaussian log returns) and data limitations (e.g. period covered, source). This builds trust and sets expectations.
- **Recommendations:** Two to four concrete recommendations. Examples: “Update the dashboard to allow multiple change point comparison”; “Extend the model to allow time-varying volatility”; “Produce a quarterly briefing that overlays new data with existing change points”; “Add unit tests and CI as in Chapter 4.1 and 4.2.”

### 4.3.3 Deliverable

A short “Insights and Recommendations” section or document (e.g. in `docs/insights_and_recommendations.md` or as a section in the main report), suitable for inclusion in stakeholder communications or a final PDF.

## 4.4 Summary of Remaining Work

| Area | Status | Deliverable |
|------|--------|-------------|
| Unit tests | Pending | pytest suite under tests/; coverage of load_data, preprocess, model, analysis_utils; optional API tests |
| GitHub Actions (CI/CD) | Pending | .github/workflows/ci.yml running tests (and optionally lint/build) on push/PR |
| Insights and recommendations | Pending | Written summary of findings, event mapping, limitations, and 2–4 actionable recommendations |

Once these are completed, the project will have full test coverage, automated quality gates, and a clear stakeholder-facing summary to accompany the technical work described in Chapters 1–3.

---

# Appendix — Unit Test Results (pytest output)

The project includes unit tests for data loading, preprocessing, modelling utilities, and the dashboard API. The following is the **pytest** output showing all tests passing. Run from the project root with: `pytest tests/ -v -m "not slow" --tb=short` (the `-m "not slow"` option skips the long-running MCMC test).

**Command run:** `python -m pytest tests/ -v -m "not slow" --tb=short`

```
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.0.2, pluggy-1.6.0
cachedir: .pytest_cache
rootdir: C:\Users\derej\Desktop\Kifya\changepoint_analysis
plugins: anyio-4.12.1
collecting ... collected 44 items / 1 deselected / 43 selected

tests/test_api.py::test_historical_prices_returns_200_and_list PASSED    [  2%]
tests/test_api.py::test_historical_prices_records_have_date_and_price PASSED [  4%]
tests/test_api.py::test_historical_prices_404_when_file_missing PASSED   [  6%]
tests/test_api.py::test_historical_prices_drops_invalid_dates PASSED     [  9%]
tests/test_api.py::test_change_points_returns_200_and_list PASSED        [ 11%]
tests/test_api.py::test_change_points_records_have_required_fields PASSED [ 13%]
tests/test_api.py::test_change_points_404_when_file_missing PASSED       [ 16%]
tests/test_api.py::test_change_points_400_when_columns_missing PASSED    [ 18%]
tests/test_api.py::test_api_prefix PASSED                                [ 20%]
tests/test_data_loading.py::test_load_valid_csv PASSED                   [ 23%]
tests/test_data_loading.py::test_load_valid_csv_mixed_date_formats PASSED [ 25%]
tests/test_data_loading.py::test_load_valid_csv_sorted_ascending PASSED  [ 27%]
tests/test_data_loading.py::test_load_valid_csv_whitespace_columns PASSED [ 30%]
tests/test_data_loading.py::test_file_not_found PASSED                   [ 32%]
tests/test_data_loading.py::test_missing_columns PASSED                  [ 34%]
tests/test_data_loading.py::test_missing_date_column_only PASSED         [ 37%]
tests/test_data_loading.py::test_invalid_date PASSED                     [ 39%]
tests/test_data_loading.py::test_invalid_price PASSED                    [ 41%]
tests/test_data_loading.py::test_price_with_empty_cell PASSED            [ 44%]
tests/test_data_processing.py::test_prepare_model_data_returns_date_price_logreturn PASSED [ 46%]
tests/test_data_processing.py::test_prepare_model_data_logreturn_formula PASSED [ 48%]
tests/test_data_processing.py::test_prepare_model_data_preserves_dates_and_prices PASSED [ 51%]
tests/test_data_processing.py::test_prepare_model_data_single_row_dropped PASSED [ 53%]
tests/test_data_processing.py::test_prepare_model_data_weekly_aggregation PASSED [ 55%]
tests/test_data_processing.py::test_prepare_model_data_monthly_aggregation PASSED [ 58%]
tests/test_data_processing.py::test_prepare_model_data_aggregate_none_same_as_omit PASSED [ 60%]
tests/test_data_processing.py::test_prepare_model_data_missing_date_column PASSED [ 62%]
tests/test_data_processing.py::test_prepare_model_data_missing_price_column PASSED [ 65%]
tests/test_data_processing.py::test_prepare_model_data_nan_price PASSED  [ 67%]
tests/test_data_processing.py::test_prepare_model_data_zero_price PASSED [ 69%]
tests/test_data_processing.py::test_prepare_model_data_negative_price PASSED [ 72%]
tests/test_data_processing.py::test_prepare_model_data_does_not_mutate_input PASSED [ 74%]
tests/test_modelling.py::test_build_change_point_report_returns_expected_keys PASSED [ 76%]
tests/test_modelling.py::test_build_change_point_report_uses_median_tau PASSED [ 79%]
tests/test_modelling.py::test_build_change_point_report_clamps_tau_to_bounds PASSED [ 81%]
tests/test_modelling.py::test_build_change_point_report_mean_before_after_delta PASSED [ 83%]
tests/test_modelling.py::test_build_change_point_report_confidence_between_0_and_1 PASSED [ 86%]
tests/test_modelling.py::test_build_change_point_report_empty_tau_samples_raises PASSED [ 88%]
tests/test_modelling.py::test_build_change_point_report_percent_change_when_mean_before_zero PASSED [ 90%]
tests/test_modelling.py::test_export_detected_event_csv_creates_file PASSED [ 93%]
tests/test_modelling.py::test_export_detected_event_csv_has_expected_columns PASSED [ 95%]
tests/test_modelling.py::test_export_detected_event_csv_content_matches_report PASSED [ 97%]
tests/test_modelling.py::test_export_detected_event_csv_creates_parent_dirs PASSED [100%]

================ 43 passed, 1 deselected, 4 warnings in 1.36s =================
```

**Summary:** 43 tests passed; 1 test is deselected (the slow MCMC test). Test files: `tests/test_data_loading.py`, `tests/test_data_processing.py`, `tests/test_modelling.py`, `tests/test_api.py`.

---

# Wrapping Up

This report summarises **progress** on the Brent Oil Change Point Analysis project. We started with raw Brent oil prices and the question *when did the rules change?*

- **Chapter 1** covered data exploration and event detection: clean data, EDA, and a list of statistically detected events.  
- **Chapter 2** described the Bayesian change point model: a posterior over the break date and before/after means, with interpretation and links to history.  
- **Chapter 3** described the interactive dashboard: FastAPI backend and React frontend for historical prices and change points.  
- **Chapter 4** outlined remaining tasks: unit tests, GitHub Actions (CI/CD), and insights and recommendations.

Chapters 1–3 form the core pipeline: **data → model → communication.** Chapter 4 completes the project with **quality assurance, automation, and stakeholder-facing insights.** Copy this document into MS Word and apply your preferred heading styles for a clean, editable progress report.

---

*For data sources, PyMC references, and methodological details, see docs/references.md and docs/analysis_overview.md.*
