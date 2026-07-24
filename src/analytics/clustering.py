import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from src.screener.engine import _cagr_to_each_row

DB_PATH = "db/nifty100.db"

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)

conn = sqlite3.connect(DB_PATH)

ratios = pd.read_sql(
    """
    SELECT
        fr.company_id,
        fr.year,
        s.broad_sector,

        fr.return_on_equity_pct,
        fr.debt_to_equity,
        fr.revenue_cagr_5yr,
        fr.operating_profit_margin_pct,
        fr.free_cash_flow_cr,

        fr.net_profit_margin_pct,
        fr.roce_pct,
        fr.asset_turnover,
        fr.interest_coverage
    FROM financial_ratios fr
    LEFT JOIN sectors s
        ON fr.company_id = s.company_id
    """,
    conn,
)

# ---------------- Add FCF CAGR ----------------

ratios["year_number"] = (
    ratios["year"]
    .str.extract(r"(\d{4})")
    .astype(float)
)

ratios["fcf_cagr_5yr"] = (
    ratios
    .groupby("company_id", group_keys=False)
    .apply(
        lambda group: _cagr_to_each_row(
            group,
            "free_cash_flow_cr",
            5,
        )
    )
)

print("Shape:", ratios.shape)
print()

print("Columns:")
print(ratios.columns.tolist())

print()

print(ratios.head())

# ---------------- Load Official Company List ----------------

official_companies = pd.read_sql(
    """
    SELECT id AS company_id
    FROM companies
    """,
    conn,
)

conn.close()

ratios = ratios.merge(
    official_companies,
    on="company_id",
    how="inner",
)

# ---------------- Latest Annual Records ----------------

latest = (
    ratios[
        ratios["year"] != "TTM"
    ]
    .sort_values("year_number")
    .groupby("company_id")
    .tail(1)
    .reset_index(drop=True)
)

# ---------------- Feature Columns ----------------

feature_columns = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "fcf_cagr_5yr",
    "operating_profit_margin_pct",
]

# ---------------- KPI Columns ----------------

kpi_columns = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "fcf_cagr_5yr",
    "operating_profit_margin_pct",
    "net_profit_margin_pct",
    "roce_pct",
    "asset_turnover",
    "interest_coverage",
    "free_cash_flow_cr",
]

# ---------------- Sector Median Imputation ----------------

for column in kpi_columns:

    latest[column] = (
        latest
        .groupby("broad_sector")[column]
        .transform(
            lambda x: x.fillna(x.median())
        )
    )

    latest[column] = latest[column].fillna(
        latest[column].median()
    )

# ---------------- Clip Extreme Values ----------------

for column in feature_columns:

    lower = latest[column].quantile(0.05)
    upper = latest[column].quantile(0.95)

    latest[column] = latest[column].clip(
        lower=lower,
        upper=upper,
    )

print("\nFeature Summary After Clipping")
print(
    latest[feature_columns]
    .describe(percentiles=[0.01, 0.05, 0.50, 0.95, 0.99])
    .round(2)
)

# ---------------- Standard Scaling ----------------

X = latest[feature_columns].copy()

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)

# ---------------- Elbow Plot ----------------

inertia = []

for k in range(2, 11):

    model = KMeans(
        n_clusters=k,
        random_state=42,
        n_init=10,
    )

    model.fit(X_scaled)

    inertia.append(model.inertia_)

plt.figure(figsize=(8, 5))

plt.plot(
    range(2, 11),
    inertia,
    marker="o",
)

plt.xlabel("Number of Clusters (k)")
plt.ylabel("Inertia")
plt.title("KMeans Elbow Method")

plt.grid(True)

plt.savefig(
    REPORT_DIR / "elbow_plot.png",
    dpi=300,
    bbox_inches="tight",
)

plt.close()

print("\nElbow plot saved:")
print(REPORT_DIR / "elbow_plot.png")

print("\nScaled Shape:", X_scaled.shape)

print("\nInertia Values")

for k, value in zip(range(2, 11), inertia):
    print(f"k={k}: {value:.2f}")

print("\nElbow observed near k = 5.")
print("Proceeding with KMeans (n_clusters=5).")

# ---------------- Final KMeans ----------------

kmeans = KMeans(
    n_clusters=5,   
    random_state=42,
    n_init=10,
)

latest["cluster_id"] = kmeans.fit_predict(X_scaled)

latest["distance_from_centroid"] = (
    kmeans.transform(X_scaled)
    .min(axis=1)
)

# ---------------- Cluster Labels ----------------

cluster_names = {
    0: "High Margin Leaders",
    1: "Stable Blue Chips",
    2: "Growth Compounders",
    3: "Leveraged Financials",
    4: "High ROE Champions",
}

latest["cluster_name"] = latest["cluster_id"].map(
    cluster_names
)

latest = latest.sort_values("company_id")

latest[
    [
        "company_id",
        "cluster_id",
        "cluster_name",
        "distance_from_centroid",
    ]
].to_csv(
    OUTPUT_DIR / "cluster_labels.csv",
    index=False,
)

# ---------------- Cluster Summary ----------------

cluster_profile = (
    latest
    .groupby("cluster_id")[feature_columns]
    .mean()
    .round(2)
)

print("\nCluster Centroids")
print(cluster_profile)

# ---------------- Cluster Profiling ----------------

cluster_profile_mean = (
    latest
    .groupby("cluster_name")[feature_columns]
    .mean()
    .round(2)
)

cluster_profile_median = (
    latest
    .groupby("cluster_name")[feature_columns]
    .median()
    .round(2)
)

print("\nCluster Mean Profile")
print(cluster_profile_mean)

print("\nCluster Median Profile")
print(cluster_profile_median)

cluster_profile_mean.to_csv(
    OUTPUT_DIR / "cluster_profile_mean.csv"
)

cluster_profile_median.to_csv(
    OUTPUT_DIR / "cluster_profile_median.csv"
)

# ---------------- Correlation Heatmap ----------------

corr = (
    latest[kpi_columns]
    .corr(method="pearson")
)

plt.figure(figsize=(10, 8))

sns.heatmap(
    corr,
    annot=True,
    cmap="coolwarm",
    center=0,
    fmt=".2f",
)

plt.title("Pearson Correlation Matrix")

plt.tight_layout()

plt.savefig(
    REPORT_DIR / "correlation_heatmap.png",
    dpi=300,
)

plt.close()

print("\nGenerated:")
print(REPORT_DIR / "correlation_heatmap.png")

cluster_profile.to_csv(
    OUTPUT_DIR / "cluster_centroids.csv"
)

# ---------------- Portfolio Statistics ----------------

portfolio_stats = pd.DataFrame({
    "P10": latest[feature_columns].quantile(0.10),
    "P25": latest[feature_columns].quantile(0.25),
    "P50": latest[feature_columns].quantile(0.50),
    "P75": latest[feature_columns].quantile(0.75),
    "P90": latest[feature_columns].quantile(0.90),
    "Mean": latest[feature_columns].mean(),
    "Std": latest[feature_columns].std(),
}).round(2)

portfolio_stats.index.name = "KPI"

portfolio_stats.to_csv(
    OUTPUT_DIR / "portfolio_stats.csv"
)

print("\nGenerated:")
print(OUTPUT_DIR / "portfolio_stats.csv")

# ---------------- Outlier Detection ----------------

outlier_df = latest.copy()

for column in feature_columns:

    sector_mean = (
        outlier_df
        .groupby("broad_sector")[column]
        .transform("mean")
    )

    sector_std = (
        outlier_df
        .groupby("broad_sector")[column]
        .transform("std")
    )

    outlier_df[f"{column}_zscore"] = (
        (outlier_df[column] - sector_mean) /
        sector_std.replace(0, np.nan)
    )

zscore_columns = [
    f"{c}_zscore"
    for c in feature_columns
]

outlier_report = outlier_df[
    outlier_df[zscore_columns]
    .abs()
    .gt(3)
    .any(axis=1)
]

outlier_report.to_csv(
    OUTPUT_DIR / "outlier_report.csv",
    index=False,
)

print("\nGenerated:")
print(OUTPUT_DIR / "outlier_report.csv")

print("\nGenerated Files")
print(f"- {OUTPUT_DIR / 'cluster_labels.csv'}")
print(f"- {OUTPUT_DIR / 'cluster_centroids.csv'}")
print(f"- {OUTPUT_DIR / 'cluster_profile_mean.csv'}")
print(f"- {OUTPUT_DIR / 'cluster_profile_median.csv'}")
print(f"- {OUTPUT_DIR / 'portfolio_stats.csv'}")
print(f"- {OUTPUT_DIR / 'outlier_report.csv'}")
print(f"- {REPORT_DIR / 'elbow_plot.png'}")
print(f"- {REPORT_DIR / 'correlation_heatmap.png'}")    

print("\nCluster Distribution")

print(
    latest["cluster_id"]
    .value_counts()
    .sort_index()
)

print("\nCluster Members")

for cid in sorted(latest["cluster_id"].unique()):
    print(f"\nCluster {cid}")
    print(
        latest.loc[
            latest["cluster_id"] == cid,
            ["company_id"]
        ].to_string(index=False)
    )
