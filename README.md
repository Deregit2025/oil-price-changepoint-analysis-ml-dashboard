# Brent Oil Price Analysis Project

[![Brent Oil CI](https://github.com/Deregit2025/oil-price-changepoint-analysis-ml-dashboard/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Deregit2025/oil-price-changepoint-analysis-ml-dashboard/actions/workflows/ci.yml)

**CI/CD:** The badge above shows the status of the [GitHub Actions workflow](https://github.com/Deregit2025/oil-price-changepoint-analysis-ml-dashboard/actions/workflows/ci.yml). On every push and pull request to `main` (and `task-3`), the pipeline runs **backend tests** (pytest) and **frontend build** (React + Vite). Green = passing.

**Deploy:** To deploy the backend and frontend on [Render](https://render.com), use the [Render Blueprint](https://render.com/docs/blueprint-spec) in this repo: connect the repo in Render → New → Blueprint. See **[docs/deploy-render.md](docs/deploy-render.md)** for step-by-step instructions.

---

### **2️⃣ README.md**

This README is **medium-blog style**, explaining the project, tasks, and structure:

````markdown
# Brent Oil Price Analysis Project

## Overview
This project analyzes **Brent Crude Oil prices (1987–2022)** to identify how major political, economic, and market events impact price behavior. The project is structured to combine **data-driven insights**, **Bayesian change point modeling**, and an **interactive dashboard** for stakeholders.

**Key Objectives:**
1. Identify significant events affecting Brent oil prices.
2. Quantify the impact of these events statistically.
3. Build a predictive and explanatory model of structural breaks.
4. Communicate insights through interactive visualization and reporting.

---

## Project Structure

```text
.
├── data/
│   ├── raw/                # Original datasets
│   │   └── BrentOilPrices.csv
│   └── processed/          # Processed datasets, detected events, etc.
│       └── detected_events.csv
├── notebooks/
│   ├── foundations.ipynb   # EDA, data-driven event detection
│   └── modelling.ipynb     # Bayesian change point modeling
├── backend/                # Flask backend for Task 3
│   ├── app.py
│   └── api_endpoints/
├── frontend/               # React frontend for Task 3
│   ├── src/
│   └── public/
├── docs/
│   ├── references.md       # Key references and model understanding
│   └── analysis_overview.md # Workflow, assumptions, limitations
├── reports/
│   └── Task1_Bayesian_ChangePoint_Analysis_and_Event_Insight_Report.pdf
├── .gitignore
└── README.md
````

---

## Task Breakdown

### Task 1: Data Exploration & Event Detection

* Clean and preprocess raw Brent oil price data.
* Perform **exploratory data analysis** (trends, volatility, log returns).
* Detect major events using **statistical thresholds** (log return shocks).
* Deliverables:

  * `foundations.ipynb` documenting the workflow
  * `detected_events.csv` (10–15 major events)
  * 1–2 page PDF report

### Task 2: Bayesian Change Point Modeling

* Apply **Bayesian change point detection** to identify structural breaks.
* Quantify impact of each detected change point.
* Associate change points with major historical events.
* Deliverables:

  * `modelling.ipynb` with model and visualizations
  * Posterior distribution plots
  * Written interpretation of results

### Task 3: Interactive Dashboard

* Backend: Flask API to serve historical price data, change points, and event correlations.
* Frontend: React dashboard with interactive plots.
* Features:

  * Historical price trends and event correlations
  * Filters, date ranges, and drill-down capabilities
  * Volatility and price change indicators
* Deliverables:

  * Fully functional Flask backend and React frontend
  * Interactive visualizations
  * README with setup instructions

---

## Learning Outcomes

**Skills:** Change Point Analysis, PyMC modeling, Bayesian inference, analytical storytelling, data visualization, dashboard development.
**Knowledge:** Probability distributions, Monte Carlo methods, model comparison, policy impact analysis.
**Communication:** Reporting to stakeholders including investors, policymakers, and analysts.

---

## References

See `docs/references.md` for all research papers, data sources, and methodological references.

```

---

### **3️⃣ One-line Professional Commit Messages**  

| File / Action | Commit Message |
|---------------|----------------|
| `.gitignore` | `Add comprehensive .gitignore for Python, Jupyter, Flask, and React` |
| `docs/references.md` | `Add key references and model understanding for Task 1` |
| `docs/analysis_overview.md` | `Document analysis workflow, assumptions, and limitations` |
| `notebooks/foundations.ipynb` | `Implement EDA and data-driven detection of major events` |
| `notebooks/modelling.ipynb` | `Set up Bayesian change point modeling for Task 2` |
| `data/processed/detected_events.csv` | `Export processed dataset of statistically detected major events` |
| `reports/Task1_Bayesian_ChangePoint_Analysis_and_Event_Insight_Report.pdf` | `Add Task 1 report summarizing EDA and event insights` |
| `frontend/` | `Initial commit for React dashboard for Task 3` |
| `backend/` | `Initial commit for Flask backend APIs for Task 3` |
| `README.md` | `Add comprehensive project README covering all tasks` |

