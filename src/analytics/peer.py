import math
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

from src.screener.engine import (
    DEFAULT_DB_PATH,
    composite_quality_score,
    load_financial_ratios,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RADAR_DIR = PROJECT_ROOT / "reports" / "radar_charts"


PEER_METRICS = {
    "ROE": ("return_on_equity_pct", True),
    "ROCE": ("roce_pct", True),
    "Net Profit Margin": ("net_profit_margin_pct", True),
    "D/E": ("debt_to_equity", False),
    "FCF": ("free_cash_flow_cr", True),
    "PAT CAGR 5yr": ("pat_cagr_5yr", True),
    "Revenue CAGR 5yr": ("revenue_cagr_5yr", True),
    "EPS CAGR 5yr": ("eps_cagr_5yr", True),
    "Interest Coverage": ("interest_coverage_for_filter", True),
    "Asset Turnover": ("asset_turnover", True),
}


REPORT_METRICS = [
    "composite_quality_score",
    "return_on_equity_pct",
    "roce_pct",
    "net_profit_margin_pct",
    "operating_profit_margin_pct",
    "debt_to_equity",
    "interest_coverage_for_filter",
    "asset_turnover",
    "free_cash_flow_cr",
    "fcf_cagr_5yr",
    "cfo_pat_ratio",
    "revenue_cagr_5yr",
    "revenue_cagr_3yr",
    "pat_cagr_5yr",
    "eps_cagr_5yr",
    "pe_ratio",
    "pb_ratio",
    "dividend_yield_pct",
    "sales",
    "net_profit",
]


RADAR_METRICS = [
    ("ROE", "return_on_equity_pct"),
    ("ROCE", "roce_pct"),
    ("NPM", "net_profit_margin_pct"),
    ("D/E", "debt_to_equity_score"),
    ("FCF", "free_cash_flow_score"),
    ("PAT CAGR", "pat_cagr_5yr"),
    ("Revenue CAGR", "revenue_cagr_5yr"),
    ("Composite", "composite_quality_score"),
]


def load_peer_groups(db_path=DEFAULT_DB_PATH):
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql("SELECT * FROM peer_groups", conn)


def load_company_names(db_path=DEFAULT_DB_PATH):
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql(
            "SELECT id AS company_id, company_name FROM companies",
            conn,
        )


def latest_company_metrics(db_path=DEFAULT_DB_PATH):
    df = composite_quality_score(load_financial_ratios(db_path))

    latest = (
        df.dropna(
            subset=[
                "return_on_equity_pct",
                "roce_pct",
                "debt_to_equity",
            ]
        )
        .sort_values(["company_id", "year_number"])
        .groupby("company_id", as_index=False)
        .tail(1)
        .copy()
    )

    names = load_company_names(db_path)
    latest = latest.merge(names, on="company_id", how="left")

    latest["debt_to_equity_score"] = 100 - _scale_0_100(
        latest["debt_to_equity"],
    )
    latest["free_cash_flow_score"] = _scale_0_100(
        latest["free_cash_flow_cr"],
    )

    return latest.reset_index(drop=True)


def _percent_rank(values, higher_is_better=True):
    numeric = pd.to_numeric(values, errors="coerce")
    ranks = numeric.rank(method="min", pct=False)
    count = numeric.notna().sum()

    if count <= 1:
        percentile = pd.Series(1.0, index=values.index)
    else:
        percentile = (ranks - 1) / (count - 1)

    if not higher_is_better:
        percentile = 1 - percentile

    return percentile.where(numeric.notna())


def _scale_0_100(values):
    numeric = pd.to_numeric(values, errors="coerce").replace(
        [np.inf, -np.inf],
        np.nan,
    )

    if numeric.notna().sum() < 2:
        return pd.Series(50.0, index=values.index)

    low = numeric.quantile(0.10)
    high = numeric.quantile(0.90)

    if pd.isna(low) or pd.isna(high) or low == high:
        return pd.Series(50.0, index=values.index)

    return ((numeric.clip(low, high) - low) / (high - low) * 100).fillna(0)


def compute_peer_percentiles(db_path=DEFAULT_DB_PATH):
    peer_groups = load_peer_groups(db_path)
    latest = latest_company_metrics(db_path)

    universe = peer_groups.merge(latest, on="company_id", how="left")
    rows = []

    for peer_group_name, group in universe.groupby("peer_group_name"):
        for metric_name, (column, higher_is_better) in PEER_METRICS.items():
            ranks = _percent_rank(group[column], higher_is_better)

            for index, row in group.iterrows():
                value = row.get(column)
                rows.append({
                    "company_id": row["company_id"],
                    "peer_group_name": peer_group_name,
                    "metric": metric_name,
                    "value": None if pd.isna(value) else float(value),
                    "percentile_rank": (
                        None
                        if pd.isna(ranks.loc[index])
                        else float(ranks.loc[index])
                    ),
                    "year": row.get("year"),
                })

    return pd.DataFrame(rows)


def populate_peer_percentiles(db_path=DEFAULT_DB_PATH):
    peer_percentiles = compute_peer_percentiles(db_path)

    with sqlite3.connect(db_path) as conn:
        peer_percentiles.to_sql(
            "peer_percentiles",
            conn,
            if_exists="replace",
            index=False,
        )

    return peer_percentiles


def get_company_peer_group(company_id, db_path=DEFAULT_DB_PATH):
    peer_groups = load_peer_groups(db_path)
    assigned = peer_groups[peer_groups["company_id"].eq(company_id)]

    if assigned.empty:
        return "No peer group assigned"

    return assigned["peer_group_name"].iloc[0]


def peer_report_frame(db_path=DEFAULT_DB_PATH):
    peer_groups = load_peer_groups(db_path)
    latest = latest_company_metrics(db_path)
    percentiles = compute_peer_percentiles(db_path)

    wide = percentiles.pivot_table(
        index=["company_id", "peer_group_name"],
        columns="metric",
        values="percentile_rank",
        aggfunc="first",
    ).reset_index()
    wide.columns = [
        f"{column} Percentile" if column in PEER_METRICS else column
        for column in wide.columns
    ]

    for metric in PEER_METRICS:
        column = f"{metric} Percentile"
        if column not in wide.columns:
            wide[column] = np.nan

    report = (
        peer_groups.merge(latest, on="company_id", how="left")
        .merge(wide, on=["company_id", "peer_group_name"], how="left")
    )

    return report


def _draw_polygon(draw, center, radius, values, outline, fill=None, width=3):
    points = []
    total = len(values)

    for index, value in enumerate(values):
        angle = -math.pi / 2 + (2 * math.pi * index / total)
        scaled = max(0, min(100, value)) / 100
        x = center[0] + math.cos(angle) * radius * scaled
        y = center[1] + math.sin(angle) * radius * scaled
        points.append((x, y))

    if fill:
        draw.polygon(points, fill=fill)
    draw.line(points + [points[0]], fill=outline, width=width)


def generate_radar_charts(db_path=DEFAULT_DB_PATH, output_dir=RADAR_DIR):
    from PIL import Image, ImageDraw, ImageFont

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    report = peer_report_frame(db_path)
    latest = latest_company_metrics(db_path)
    peer_company_ids = set(report["company_id"].dropna())
    nifty_average = latest[RADAR_METRICS[0][1]].mean(skipna=True)

    generated = []

    def font(size):
        try:
            return ImageFont.truetype("arial.ttf", size)
        except OSError:
            return ImageFont.load_default()

    for _, row in report.iterrows():
        group = report[report["peer_group_name"].eq(row["peer_group_name"])]
        values = []
        averages = []

        for _, column in RADAR_METRICS:
            if column == "debt_to_equity_score":
                metric_values = 100 - _scale_0_100(group["debt_to_equity"])
                values.append(metric_values.loc[row.name])
                averages.append(metric_values.mean(skipna=True))
            elif column == "free_cash_flow_score":
                metric_values = _scale_0_100(group["free_cash_flow_cr"])
                values.append(metric_values.loc[row.name])
                averages.append(metric_values.mean(skipna=True))
            else:
                metric_values = _scale_0_100(group[column])
                values.append(metric_values.loc[row.name])
                averages.append(metric_values.mean(skipna=True))

        path = output_dir / f"{row['company_id']}_radar.png"
        _save_radar_image(
            path,
            row["company_id"],
            row["peer_group_name"],
            values,
            averages,
            font,
            Image,
            ImageDraw,
        )
        generated.append(path)

    unassigned = latest[~latest["company_id"].isin(peer_company_ids)]
    for _, row in unassigned.iterrows():
        value = row.get("return_on_equity_pct")
        values = [0 if pd.isna(value) else min(100, max(0, value))]
        averages = [0 if pd.isna(nifty_average) else min(100, max(0, nifty_average))]
        path = output_dir / f"{row['company_id']}_radar.png"
        _save_single_metric_image(
            path,
            row["company_id"],
            "No peer group assigned",
            "ROE vs Nifty 100 average",
            values[0],
            averages[0],
            font,
            Image,
            ImageDraw,
        )
        generated.append(path)

    return generated


def _save_radar_image(path, company_id, group_name, values, averages, font, Image, ImageDraw):
    image = Image.new("RGB", (720, 560), "#FFFFFF")
    draw = ImageDraw.Draw(image, "RGBA")
    center = (360, 290)
    radius = 180

    for step in range(1, 6):
        ring = radius * step / 5
        polygon = []
        for index in range(len(RADAR_METRICS)):
            angle = -math.pi / 2 + (2 * math.pi * index / len(RADAR_METRICS))
            polygon.append((
                center[0] + math.cos(angle) * ring,
                center[1] + math.sin(angle) * ring,
            ))
        draw.line(polygon + [polygon[0]], fill="#D1D5DB", width=1)

    for index, (label, _) in enumerate(RADAR_METRICS):
        angle = -math.pi / 2 + (2 * math.pi * index / len(RADAR_METRICS))
        x = center[0] + math.cos(angle) * (radius + 45)
        y = center[1] + math.sin(angle) * (radius + 35)
        draw.text((x - 45, y - 8), label, fill="#111827", font=font(13))

    _draw_polygon(draw, center, radius, averages, "#6B7280", None, 3)
    _draw_polygon(draw, center, radius, values, "#2563EB", "#93C5FD88", 4)

    draw.text((32, 24), f"{company_id} Radar", fill="#111827", font=font(24))
    draw.text((32, 58), f"Peer group: {group_name}", fill="#4B5563", font=font(15))
    draw.text((32, 510), "Blue = company | Grey = peer average", fill="#4B5563", font=font(13))
    image.save(path)


def _save_single_metric_image(
    path,
    company_id,
    group_name,
    title,
    value,
    average,
    font,
    Image,
    ImageDraw,
):
    image = Image.new("RGB", (720, 360), "#FFFFFF")
    draw = ImageDraw.Draw(image)
    draw.text((32, 24), f"{company_id} Standalone View", fill="#111827", font=font(24))
    draw.text((32, 58), group_name, fill="#4B5563", font=font(15))
    draw.text((32, 105), title, fill="#111827", font=font(16))

    bar_x = 170
    bar_y = 160
    bar_w = 420
    draw.rectangle((bar_x, bar_y, bar_x + bar_w, bar_y + 30), fill="#E5E7EB")
    draw.rectangle((bar_x, bar_y, bar_x + bar_w * value / 100, bar_y + 30), fill="#2563EB")
    draw.text((bar_x + bar_w + 16, bar_y + 5), f"{value:.1f}", fill="#111827", font=font(13))

    draw.rectangle((bar_x, bar_y + 62, bar_x + bar_w, bar_y + 92), fill="#E5E7EB")
    draw.rectangle((bar_x, bar_y + 62, bar_x + bar_w * average / 100, bar_y + 92), fill="#6B7280")
    draw.text((bar_x + bar_w + 16, bar_y + 67), f"{average:.1f}", fill="#111827", font=font(13))
    draw.text((32, bar_y + 5), "Company", fill="#111827", font=font(13))
    draw.text((32, bar_y + 67), "Nifty 100 avg", fill="#111827", font=font(13))
    image.save(path)


if __name__ == "__main__":
    count = len(populate_peer_percentiles())
    charts = generate_radar_charts()
    print(f"peer_percentiles rows: {count}")
    print(f"radar charts generated: {len(charts)}")
