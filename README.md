# Customer Engagement & Product Utilization Analytics for Retention Strategy

A complete, working analytics project: data pipeline, KPI engine, and an interactive Streamlit dashboard, built on the real 10,000-row Bank Customer Churn dataset.

## What's included

```
project/
├── data/
│   └── Churn_Modelling.csv       # Real dataset (10,000 customers)
├── engagement_analytics.py       # Core analytics engine (all 5 methodology steps + KPIs)
├── app.py                        # Streamlit dashboard (4 modules, full filter set)
├── requirements.txt
├── Research_Paper.md             # Deliverable 1: EDA, insights, recommendations
├── Executive_Summary.md          # Deliverable 3: stakeholder summary
└── README.md
```

The Streamlit dashboard itself is Deliverable 2 (live analytics).

## How to run it

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Launch the dashboard:
   ```bash
   streamlit run app.py
   ```

3. Open the URL Streamlit prints (usually `http://localhost:8501`).

## How to use your own data instead

If you have your own version of the dataset (or a live extract from your bank's systems), just replace `data/Churn_Modelling.csv` with a CSV containing these exact column names:

```
CustomerId, Surname, CreditScore, Geography, Gender, Age, Tenure,
Balance, NumOfProducts, HasCrCard, IsActiveMember, EstimatedSalary, Exited
```

The pipeline validates this schema automatically on load and will raise a clear error if a required column is missing.

## Dashboard modules (matches spec exactly)

1. **Engagement vs Churn Overview** — profile-level churn rates, active vs inactive comparison
2. **Product Utilization Impact Analysis** — churn by product count, single vs multi-product retention
3. **High-Value Disengaged Customer Detector** — "silent churn" segment, balance/activity cross-analysis, salary-balance mismatch
4. **Retention Strength Scoring Panels** — composite 0–100 score, tier validation, threshold scan

## User capabilities (sidebar filters)

- Engagement profile filter
- Product count range slider
- Minimum balance threshold
- Minimum salary threshold
- Geography filter

## Extending this project

- **Predictive modeling:** the `data` DataFrame returned by `run_full_pipeline()` is ready to feed directly into scikit-learn (logistic regression, random forest, XGBoost) for a churn *prediction* model layered on top of this *diagnostic* analysis.
- **Export to Word/PDF:** the Research Paper and Executive Summary are plain Markdown — ask to have them converted into formatted `.docx` or `.pdf` deliverables if your submission requires that format.
- **Deploy the dashboard:** push this folder to a GitHub repo and deploy for free on [Streamlit Community Cloud](https://streamlit.io/cloud) to get a shareable public link.
