# Customer Engagement & Product Utilization Analytics for Retention Strategy

## 1. Background and Context

Banks increasingly recognize that customer behavior and engagement — not just demographics — determine long-term retention. Customers may appear financially strong (high balance or salary) but still churn due to low engagement, limited product adoption, and weak relationship depth with the bank. Understanding how customers use banking products and services is essential to designing effective cross-sell strategies, loyalty programs, and engagement-driven retention initiatives.

## 2. Problem Statement

Despite having data on customer engagement and product usage, banks often lack quantitative insight into which behaviors drive retention, clarity on whether product depth reduces churn, and evidence on whether high balances alone ensure loyalty. As a result, retention strategies are frequently generic and misaligned with actual customer behavior.

## 3. Objectives

**Primary:**
- Evaluate the relationship between engagement and churn
- Measure the retention impact of product count and product mix
- Identify disengaged yet high-value customers

**Secondary:**
- Support engagement-driven retention strategies
- Improve product bundling decisions
- Reduce silent churn among premium customers

## 4. Dataset

10,000 bank customer records (`Churn_Modelling.csv`) with the following fields: CustomerId, Surname, CreditScore, Geography, Gender, Age, Tenure, Balance, NumOfProducts, HasCrCard, IsActiveMember, EstimatedSalary, and the churn label Exited. Overall churn rate in the base population is **20.4%**.

## 5. Methodology

The analysis follows a five-stage pipeline (implemented in `engagement_analytics.py`):

1. **Data Ingestion & Validation** — schema check, binary-field consistency, null handling on analytically critical fields.
2. **Engagement Classification** — every customer assigned to one of four profiles: *Active Engaged*, *Active, Low-Product*, *Inactive Disengaged*, *Inactive High-Balance*.
3. **Product Utilization Analysis** — churn rate by product count; single vs multi-product retention comparison.
4. **Financial Commitment vs Engagement Analysis** — balance tier × activity cross-analysis, salary-balance mismatch detection, at-risk premium customer identification.
5. **Retention Strength Assessment** — a composite 0–100 "stickiness" score (Activity 40% + Product Depth 35% + Card Ownership 25%), validated against actual churn outcomes.

## 6. Key Findings (EDA)

### 6.1 Engagement Drives Churn More Than Demographics

| Engagement Profile | Customers | Churn Rate |
|---|---|---|
| Active Engaged | 2,588 | **9.7%** |
| Active, Low-Product | 2,563 | 18.9% |
| Inactive Disengaged | 3,602 | 25.6% |
| Inactive High-Balance | 1,247 | **30.5%** |

Inactive customers churn at **1.88x** the rate of active customers (Engagement Retention Ratio). Strikingly, the *Inactive High-Balance* segment — customers who look financially healthy on paper — has the **highest churn rate of all**, confirming the core hypothesis: balance alone does not guarantee loyalty.

### 6.2 Product Depth Has a Non-Linear Effect on Retention

| Products Held | Customers | Churn Rate |
|---|---|---|
| 1 | 5,084 | 27.7% |
| 2 | 4,590 | **7.6%** |
| 3 | 266 | 82.7% |
| 4 | 60 | 100.0% |

Two products is the retention "sweet spot." Beyond that, churn rises sharply — customers with 3–4 products churn almost universally, a pattern typically associated with over-selling, product/service mismatch, or customers already exiting the relationship (e.g., holding multiple products briefly before a full account closure). Single-product customers churn nearly 4x more than 2-product customers (27.7% vs 7.6%).

### 6.3 The "Silent Churn" Segment

1,247 customers (12.5% of the base) are premium (top-balance-quartile) yet inactive. This group churns at 30.5% — the highest of any segment — despite being the most financially valuable. This is the clearest actionable target for retention intervention.

### 6.4 Retention Strength Score Validates the Model

| Retention Tier | Customers | Churn Rate |
|---|---|---|
| Weak | 1,351 | 23.2% |
| Moderate | 4,286 | 27.0% |
| Strong | 4,363 | **13.0%** |

Customers scoring in the "Strong" tier churn at roughly half the rate of "Moderate" tier customers, confirming that the composite score is a meaningful, actionable retention signal.

## 7. KPI Summary

| KPI | Value | Interpretation |
|---|---|---|
| Engagement Retention Ratio | 1.88x | Inactive customers churn 88% more often than active ones |
| Product Depth Index | 0.72 | Strong positive gap between best- and worst-performing product tiers |
| High-Balance Disengagement Rate | 49.9% | Nearly half of top-quartile-balance customers are inactive |
| Credit Card Stickiness Score | 0.6 pp | Card ownership alone has minimal standalone retention effect |
| Relationship Strength Index (Retained vs Churned) | 57.9 vs 48.8 | Retained customers score ~9 points higher on average |

## 8. Recommendations

1. **Prioritize reactivation campaigns for inactive high-balance customers** — this segment is both the highest-value and highest-risk.
2. **Cap cross-sell at 2 products** for standard retention purposes; investigate the 3–4 product segment specifically for over-selling or service friction rather than treating more products as inherently "stickier."
3. **Use the Retention Strength Score as a live monitoring signal** — customers dropping below the "Strong" threshold (≈60) should trigger proactive outreach.
4. **De-prioritize credit card issuance as a standalone retention lever** — its marginal effect on churn is small; pair it with activity-driving incentives instead.

## 9. Conclusion

This project reframes customer churn from a behavioral and relationship-strength perspective. By focusing on engagement and product utilization rather than demographics, it provides actionable insights for retention strategy design, product optimization, and customer loyalty enhancement. The data confirms that **activity status and product depth — not balance or salary — are the dominant predictors of retention**, and that the most valuable intervention target is the disengaged-but-premium customer segment.
