"""
Streamlit Dashboard — Customer Engagement & Product Utilization Analytics
for Retention Strategy.

Run with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from engagement_analytics import (
    load_and_validate, classify_engagement, salary_balance_mismatch,
    retention_strength_index, product_utilization_analysis,
    single_vs_multi_product, balance_vs_activity, at_risk_premium_customers,
    churn_stability_by_tier, engagement_threshold_scan, compute_kpis,
)

st.set_page_config(
    page_title="Customer Engagement & Retention Analytics",
    page_icon="🏦",
    layout="wide",
)

# ---------------------------------------------------------------------------
# DATA LOADING (cached)
# ---------------------------------------------------------------------------

@st.cache_data
def get_base_data(path="data/Churn_Modelling.csv"):
    df = load_and_validate(path)
    df = classify_engagement(df)
    df = salary_balance_mismatch(df)
    df = retention_strength_index(df)
    return df

df_full = get_base_data()

# ---------------------------------------------------------------------------
# SIDEBAR — USER CAPABILITIES (filters)
# ---------------------------------------------------------------------------

st.sidebar.title("🔎 Filters")

engagement_options = sorted(df_full["EngagementProfile"].unique())
selected_profiles = st.sidebar.multiselect(
    "Engagement profile", engagement_options, default=engagement_options
)

product_range = st.sidebar.slider(
    "Number of products", int(df_full["NumOfProducts"].min()),
    int(df_full["NumOfProducts"].max()),
    (int(df_full["NumOfProducts"].min()), int(df_full["NumOfProducts"].max())),
)

balance_min, balance_max = float(df_full["Balance"].min()), float(df_full["Balance"].max())
balance_threshold = st.sidebar.slider(
    "Minimum balance", balance_min, balance_max, balance_min, step=1000.0
)

salary_min, salary_max = float(df_full["EstimatedSalary"].min()), float(df_full["EstimatedSalary"].max())
salary_threshold = st.sidebar.slider(
    "Minimum estimated salary", salary_min, salary_max, salary_min, step=1000.0
)

geo_options = sorted(df_full["Geography"].unique())
selected_geo = st.sidebar.multiselect("Geography", geo_options, default=geo_options)

st.sidebar.markdown("---")
st.sidebar.caption(f"Dataset: {len(df_full):,} customers loaded")

# Apply filters
df = df_full[
    (df_full["EngagementProfile"].isin(selected_profiles)) &
    (df_full["NumOfProducts"].between(*product_range)) &
    (df_full["Balance"] >= balance_threshold) &
    (df_full["EstimatedSalary"] >= salary_threshold) &
    (df_full["Geography"].isin(selected_geo))
].copy()

if df.empty:
    st.warning("No customers match the current filters. Please widen your filter selection.")
    st.stop()

kpis = compute_kpis(df)

# ---------------------------------------------------------------------------
# HEADER
# ---------------------------------------------------------------------------

st.title("🏦 Customer Engagement & Product Utilization Analytics")
st.caption("Retention strategy dashboard — behavior and relationship depth, not just demographics")

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Customers (filtered)", f"{len(df):,}", f"of {len(df_full):,} total")
k2.metric("Overall Churn Rate", f"{df['Exited'].mean()*100:.1f}%")
k3.metric("Engagement Retention Ratio", f"{kpis['Engagement Retention Ratio']}x",
          help="Inactive churn rate ÷ Active churn rate. >1 means inactive customers churn more.")
k4.metric("High-Balance Disengagement", f"{kpis['High-Balance Disengagement Rate (%)']}%",
          help="% of top-quartile balance customers who are NOT active members")
k5.metric("Card Stickiness Score", f"{kpis['Credit Card Stickiness Score (pp)']} pp",
          help="Churn rate (no card) minus churn rate (with card), in percentage points")

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Engagement vs Churn Overview",
    "🧩 Product Utilization Impact",
    "🚨 High-Value Disengaged Detector",
    "💪 Retention Strength Scoring",
])

# ---------------------------------------------------------------------------
# TAB 1 — ENGAGEMENT VS CHURN OVERVIEW
# ---------------------------------------------------------------------------

with tab1:
    st.subheader("Engagement Profiles vs Churn")

    col1, col2 = st.columns([1, 1])

    with col1:
        profile_summary = (
            df.groupby("EngagementProfile")
            .agg(Customers=("CustomerId", "count"), ChurnRate=("Exited", "mean"))
            .reset_index()
        )
        profile_summary["ChurnRate"] = (profile_summary["ChurnRate"] * 100).round(2)

        fig = px.bar(
            profile_summary, x="EngagementProfile", y="ChurnRate",
            color="EngagementProfile", text="ChurnRate",
            title="Churn Rate by Engagement Profile",
            labels={"ChurnRate": "Churn Rate (%)", "EngagementProfile": "Profile"},
        )
        fig.update_traces(texttemplate="%{text}%", textposition="outside")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.pie(
            profile_summary, names="EngagementProfile", values="Customers",
            title="Customer Distribution by Engagement Profile",
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### Active vs Inactive — Direct Comparison")
    activity_summary = (
        df.assign(Status=np.where(df["IsActiveMember"] == 1, "Active", "Inactive"))
        .groupby("Status")
        .agg(Customers=("CustomerId", "count"), ChurnRate=("Exited", "mean"))
        .reset_index()
    )
    activity_summary["ChurnRate"] = (activity_summary["ChurnRate"] * 100).round(2)
    c1, c2 = st.columns(2)
    c1.dataframe(activity_summary, use_container_width=True, hide_index=True)
    with c2:
        fig3 = px.bar(activity_summary, x="Status", y="ChurnRate", color="Status",
                       text="ChurnRate", title="Active vs Inactive Churn Rate")
        fig3.update_traces(texttemplate="%{text}%", textposition="outside")
        st.plotly_chart(fig3, use_container_width=True)

    st.info(
        f"**Insight:** Inactive customers churn at **{kpis['Engagement Retention Ratio']}x** "
        "the rate of active customers — engagement is one of the strongest retention levers available."
    )

# ---------------------------------------------------------------------------
# TAB 2 — PRODUCT UTILIZATION IMPACT
# ---------------------------------------------------------------------------

with tab2:
    st.subheader("Product Depth vs Churn")

    prod_util = product_utilization_analysis(df)
    col1, col2 = st.columns([1, 1])

    with col1:
        fig4 = px.bar(
            prod_util, x="NumOfProducts", y="ChurnRate", text="ChurnRate",
            title="Churn Rate by Number of Products",
            labels={"ChurnRate": "Churn Rate (%)", "NumOfProducts": "Number of Products"},
        )
        fig4.update_traces(texttemplate="%{text}%", textposition="outside", marker_color="#2E86AB")
        st.plotly_chart(fig4, use_container_width=True)

    with col2:
        single_multi = single_vs_multi_product(df)
        fig5 = px.bar(
            single_multi, x="ProductTier", y="RetentionRate", text="RetentionRate",
            title="Single-Product vs Multi-Product Retention",
            color="ProductTier",
            labels={"RetentionRate": "Retention Rate (%)"},
        )
        fig5.update_traces(texttemplate="%{text}%", textposition="outside")
        fig5.update_layout(showlegend=False)
        st.plotly_chart(fig5, use_container_width=True)

    st.dataframe(prod_util, use_container_width=True, hide_index=True)

    max_churn_products = prod_util.loc[prod_util["ChurnRate"].idxmax(), "NumOfProducts"]
    st.warning(
        f"**Insight:** Customers holding **{int(max_churn_products)} products** show the "
        "highest churn — this is a classic sign of over-selling or product/service "
        "mismatch rather than loyalty. The sweet spot is typically 2 products."
    )

# ---------------------------------------------------------------------------
# TAB 3 — HIGH-VALUE DISENGAGED DETECTOR
# ---------------------------------------------------------------------------

with tab3:
    st.subheader("High-Value, Disengaged Customer Detector")
    st.caption("Financially strong customers showing behavioral disengagement — the 'silent churn' risk group")

    at_risk = at_risk_premium_customers(df)

    col1, col2, col3 = st.columns(3)
    col1.metric("At-Risk Premium Customers", f"{len(at_risk):,}")
    col2.metric("% of Filtered Base", f"{len(at_risk)/len(df)*100:.1f}%")
    col3.metric("Their Churn Rate", f"{at_risk['Exited'].mean()*100:.1f}%" if len(at_risk) else "N/A")

    st.markdown("#### Balance vs Activity Cross-Analysis")
    bva = balance_vs_activity(df)
    fig6 = px.bar(
        bva, x="BalanceTier", y="ChurnRate", color="ActivityStatus", barmode="group",
        text="ChurnRate", title="Churn Rate by Balance Tier and Activity Status",
        labels={"ChurnRate": "Churn Rate (%)", "BalanceTier": "Balance Tier"},
    )
    fig6.update_traces(texttemplate="%{text}%", textposition="outside")
    st.plotly_chart(fig6, use_container_width=True)

    st.markdown("#### Salary–Balance Mismatch Segment")
    mismatch = df[df["SalaryBalanceMismatch"]]
    st.write(
        f"**{len(mismatch):,} customers** ({len(mismatch)/len(df)*100:.1f}%) have a high estimated "
        "salary but unusually low account balance — a signal of an under-utilized relationship."
    )

    st.markdown("#### Top At-Risk Premium Customers (highest balance, inactive)")
    display_cols = ["CustomerId", "Surname", "Geography", "Age", "Balance",
                     "NumOfProducts", "EstimatedSalary", "Exited"]
    st.dataframe(
        at_risk[display_cols].head(25).style.format({"Balance": "{:,.2f}", "EstimatedSalary": "{:,.2f}"}),
        use_container_width=True, hide_index=True,
    )

# ---------------------------------------------------------------------------
# TAB 4 — RETENTION STRENGTH SCORING
# ---------------------------------------------------------------------------

with tab4:
    st.subheader("Retention Strength Assessment")
    st.caption("Composite score (0-100): Activity 40% · Product Depth 35% · Credit Card 25%")

    col1, col2 = st.columns([1, 1])

    with col1:
        fig7 = px.histogram(
            df, x="RetentionStrengthScore", color="RetentionTier", nbins=25,
            title="Distribution of Retention Strength Scores",
        )
        st.plotly_chart(fig7, use_container_width=True)

    with col2:
        tier_churn = churn_stability_by_tier(df)
        fig8 = px.bar(
            tier_churn, x="RetentionTier", y="ChurnRate", color="RetentionTier",
            text="ChurnRate", title="Churn Rate by Retention Tier",
            category_orders={"RetentionTier": ["Weak", "Moderate", "Strong"]},
        )
        fig8.update_traces(texttemplate="%{text}%", textposition="outside")
        fig8.update_layout(showlegend=False)
        st.plotly_chart(fig8, use_container_width=True)

    st.markdown("#### Engagement Threshold Scan")
    st.caption("Churn rate for customers scoring above each threshold — used to define a practical 'safe' cut-off")
    scan = engagement_threshold_scan(df)
    fig9 = go.Figure()
    fig9.add_trace(go.Scatter(x=scan["Threshold"], y=scan["ChurnRate"],
                               mode="lines+markers", name="Churn Rate (%)"))
    fig9.update_layout(
        title="Churn Rate vs Retention-Score Threshold",
        xaxis_title="Retention Score Threshold (≥)", yaxis_title="Churn Rate (%)",
    )
    st.plotly_chart(fig9, use_container_width=True)

    st.dataframe(tier_churn, use_container_width=True, hide_index=True)

    st.success(
        f"**Insight:** 'Strong' tier customers churn at **{tier_churn.loc[tier_churn['RetentionTier']=='Strong','ChurnRate'].values[0] if 'Strong' in tier_churn['RetentionTier'].values else 'N/A'}%** "
        "vs the overall base rate — confirming that activity + product depth + card ownership "
        "meaningfully predicts retention."
    )

st.markdown("---")
st.caption("Customer Engagement & Product Utilization Analytics for Retention Strategy · Streamlit Dashboard")
