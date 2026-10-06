"""
engagement_analytics.py
------------------------
Core analytical engine for the "Customer Engagement & Product Utilization
Analytics for Retention Strategy" project.

Implements every step in the Analytical Methodology section:
  1. Data Ingestion & Validation
  2. Engagement Classification
  3. Product Utilization Analysis
  4. Financial Commitment vs Engagement Analysis
  5. Retention Strength Assessment
  6. Key Performance Indicators (KPIs)
"""

import pandas as pd
import numpy as np


# ---------------------------------------------------------------------------
# 1. DATA INGESTION & VALIDATION
# ---------------------------------------------------------------------------

REQUIRED_COLS = [
    "CustomerId", "Surname", "CreditScore", "Geography", "Gender", "Age",
    "Tenure", "Balance", "NumOfProducts", "HasCrCard", "IsActiveMember",
    "EstimatedSalary", "Exited",
]


def load_and_validate(path: str) -> pd.DataFrame:
    """Load the dataset and validate schema, types, and label integrity."""
    df = pd.read_csv(path)

    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")

    # Ensure binary fields are strictly 0/1
    for col in ["HasCrCard", "IsActiveMember", "Exited"]:
        bad = ~df[col].isin([0, 1])
        if bad.any():
            df = df[~bad].copy()

    # Drop rows with nulls in analytically critical fields
    critical = ["Balance", "NumOfProducts", "IsActiveMember", "EstimatedSalary", "Exited"]
    df = df.dropna(subset=critical)

    # Type safety
    df["NumOfProducts"] = df["NumOfProducts"].astype(int)
    df["IsActiveMember"] = df["IsActiveMember"].astype(int)
    df["HasCrCard"] = df["HasCrCard"].astype(int)
    df["Exited"] = df["Exited"].astype(int)

    return df.reset_index(drop=True)


# ---------------------------------------------------------------------------
# 2. ENGAGEMENT CLASSIFICATION
# ---------------------------------------------------------------------------

def classify_engagement(df: pd.DataFrame, balance_high_pct: float = 0.75) -> pd.DataFrame:
    """
    Assigns each customer to one engagement profile:
      - Active Engaged        : active member AND holds 2+ products
      - Active, Low-Product   : active member AND holds only 1 product
      - Inactive Disengaged   : not active AND holds only 1 product
      - Inactive High-Balance : not active AND balance is in the top
                                 (1 - balance_high_pct) of all balances
    Priority: inactive + high balance is flagged even if product count is 1,
    since it represents the highest-value at-risk segment.
    """
    df = df.copy()
    balance_threshold = df["Balance"].quantile(balance_high_pct)

    def profile(row):
        active = row["IsActiveMember"] == 1
        multi_product = row["NumOfProducts"] >= 2
        high_balance = row["Balance"] >= balance_threshold

        if not active and high_balance:
            return "Inactive High-Balance"
        if active and multi_product:
            return "Active Engaged"
        if active and not multi_product:
            return "Active, Low-Product"
        return "Inactive Disengaged"

    df["EngagementProfile"] = df.apply(profile, axis=1)
    df["BalanceHighThreshold"] = balance_threshold
    return df


# ---------------------------------------------------------------------------
# 3. PRODUCT UTILIZATION ANALYSIS
# ---------------------------------------------------------------------------

def product_utilization_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Churn rate broken down by number of products held."""
    out = (
        df.groupby("NumOfProducts")
        .agg(Customers=("CustomerId", "count"), ChurnRate=("Exited", "mean"))
        .reset_index()
    )
    out["ChurnRate"] = (out["ChurnRate"] * 100).round(2)
    return out


def single_vs_multi_product(df: pd.DataFrame) -> pd.DataFrame:
    """Single-product vs multi-product (2+) retention comparison."""
    df = df.copy()
    df["ProductTier"] = np.where(df["NumOfProducts"] == 1, "Single-Product", "Multi-Product")
    out = (
        df.groupby("ProductTier")
        .agg(Customers=("CustomerId", "count"), ChurnRate=("Exited", "mean"))
        .reset_index()
    )
    out["ChurnRate"] = (out["ChurnRate"] * 100).round(2)
    out["RetentionRate"] = (100 - out["ChurnRate"]).round(2)
    return out


# ---------------------------------------------------------------------------
# 4. FINANCIAL COMMITMENT VS ENGAGEMENT ANALYSIS
# ---------------------------------------------------------------------------

def balance_vs_activity(df: pd.DataFrame) -> pd.DataFrame:
    """Cross-tab of activity status vs churn, split by balance tier."""
    df = df.copy()
    df["BalanceTier"] = pd.qcut(df["Balance"].rank(method="first"), 4,
                                 labels=["Low", "Medium", "High", "Very High"])
    df["ActivityStatus"] = np.where(df["IsActiveMember"] == 1, "Active", "Inactive")
    out = (
        df.groupby(["BalanceTier", "ActivityStatus"], observed=True)
        .agg(Customers=("CustomerId", "count"), ChurnRate=("Exited", "mean"))
        .reset_index()
    )
    out["ChurnRate"] = (out["ChurnRate"] * 100).round(2)
    return out


def salary_balance_mismatch(df: pd.DataFrame) -> pd.DataFrame:
    """
    Flags customers whose EstimatedSalary is high but Balance is very low
    (or vice-versa) — a signal of an under-utilized banking relationship.
    """
    df = df.copy()
    salary_median = df["EstimatedSalary"].median()
    balance_median = df["Balance"].median()

    df["SalaryBalanceMismatch"] = (
        (df["EstimatedSalary"] >= salary_median) & (df["Balance"] <= balance_median * 0.25)
    )
    return df


def at_risk_premium_customers(df: pd.DataFrame, balance_high_pct: float = 0.75) -> pd.DataFrame:
    """
    Premium customers (top balance quartile) who are inactive — the
    "silent churn" segment: financially strong but behaviorally disengaged.
    """
    balance_threshold = df["Balance"].quantile(balance_high_pct)
    at_risk = df[(df["Balance"] >= balance_threshold) & (df["IsActiveMember"] == 0)].copy()
    return at_risk.sort_values("Balance", ascending=False)


# ---------------------------------------------------------------------------
# 5. RETENTION STRENGTH ASSESSMENT
# ---------------------------------------------------------------------------

def retention_strength_index(df: pd.DataFrame) -> pd.DataFrame:
    """
    Composite 0-100 score per customer combining:
      - Activity (40%)
      - Product depth, capped at 3 products (35%)
      - Credit card ownership (25%)
    Higher score = "stickier" customer, structurally less likely to churn.
    """
    df = df.copy()
    activity_score = df["IsActiveMember"] * 40
    product_score = (df["NumOfProducts"].clip(upper=3) / 3) * 35
    card_score = df["HasCrCard"] * 25
    df["RetentionStrengthScore"] = (activity_score + product_score + card_score).round(1)

    bins = [-1, 30, 60, 100]
    labels = ["Weak", "Moderate", "Strong"]
    df["RetentionTier"] = pd.cut(df["RetentionStrengthScore"], bins=bins, labels=labels)
    return df


def churn_stability_by_tier(df: pd.DataFrame) -> pd.DataFrame:
    """Churn rate for each Retention Tier — validates the scoring model."""
    out = (
        df.groupby("RetentionTier", observed=True)
        .agg(Customers=("CustomerId", "count"), ChurnRate=("Exited", "mean"))
        .reset_index()
    )
    out["ChurnRate"] = (out["ChurnRate"] * 100).round(2)
    return out


def engagement_threshold_scan(df: pd.DataFrame) -> pd.DataFrame:
    """
    Scans retention-score thresholds to find the point where churn risk
    drops off sharply — used to define a practical "safe" score cut-off.
    """
    rows = []
    for t in range(0, 101, 5):
        seg = df[df["RetentionStrengthScore"] >= t]
        if len(seg) == 0:
            continue
        rows.append({
            "Threshold": t,
            "CustomersAboveThreshold": len(seg),
            "ChurnRate": round(seg["Exited"].mean() * 100, 2),
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 6. KEY PERFORMANCE INDICATORS
# ---------------------------------------------------------------------------

def compute_kpis(df: pd.DataFrame) -> dict:
    """Returns the five headline KPIs defined in the project spec."""

    # Engagement Retention Ratio: active churn vs inactive churn
    active_churn = df.loc[df["IsActiveMember"] == 1, "Exited"].mean()
    inactive_churn = df.loc[df["IsActiveMember"] == 0, "Exited"].mean()
    engagement_retention_ratio = (
        round(inactive_churn / active_churn, 2) if active_churn > 0 else np.nan
    )

    # Product Depth Index: correlation-style measure of products vs loyalty
    prod_churn = df.groupby("NumOfProducts")["Exited"].mean()
    product_depth_index = round((1 - prod_churn.get(1, 0)) - (1 - prod_churn.max()), 4)

    # High-Balance Disengagement Rate
    balance_threshold = df["Balance"].quantile(0.75)
    high_balance_df = df[df["Balance"] >= balance_threshold]
    high_balance_disengagement_rate = round(
        (high_balance_df["IsActiveMember"] == 0).mean() * 100, 2
    )

    # Credit Card Stickiness Score: churn rate without card minus with card
    churn_with_card = df.loc[df["HasCrCard"] == 1, "Exited"].mean()
    churn_without_card = df.loc[df["HasCrCard"] == 0, "Exited"].mean()
    credit_card_stickiness_score = round((churn_without_card - churn_with_card) * 100, 2)

    # Relationship Strength Index: avg retention score of retained vs churned
    if "RetentionStrengthScore" not in df.columns:
        df = retention_strength_index(df)
    rsi_retained = df.loc[df["Exited"] == 0, "RetentionStrengthScore"].mean()
    rsi_churned = df.loc[df["Exited"] == 1, "RetentionStrengthScore"].mean()

    return {
        "Engagement Retention Ratio": engagement_retention_ratio,
        "Product Depth Index": product_depth_index,
        "High-Balance Disengagement Rate (%)": high_balance_disengagement_rate,
        "Credit Card Stickiness Score (pp)": credit_card_stickiness_score,
        "Relationship Strength Index (Retained)": round(rsi_retained, 1),
        "Relationship Strength Index (Churned)": round(rsi_churned, 1),
    }


# ---------------------------------------------------------------------------
# PIPELINE ENTRY POINT
# ---------------------------------------------------------------------------

def run_full_pipeline(path: str) -> dict:
    """Runs the entire methodology end-to-end and returns all artifacts."""
    df = load_and_validate(path)
    df = classify_engagement(df)
    df = salary_balance_mismatch(df)
    df = retention_strength_index(df)

    results = {
        "data": df,
        "product_utilization": product_utilization_analysis(df),
        "single_vs_multi": single_vs_multi_product(df),
        "balance_vs_activity": balance_vs_activity(df),
        "at_risk_premium": at_risk_premium_customers(df),
        "churn_by_tier": churn_stability_by_tier(df),
        "threshold_scan": engagement_threshold_scan(df),
        "kpis": compute_kpis(df),
    }
    return results


if __name__ == "__main__":
    results = run_full_pipeline("data/Churn_Modelling.csv")
    print("\n=== KPIs ===")
    for k, v in results["kpis"].items():
        print(f"{k}: {v}")
    print("\n=== Product Utilization ===")
    print(results["product_utilization"])
    print("\n=== Churn by Retention Tier ===")
    print(results["churn_by_tier"])
