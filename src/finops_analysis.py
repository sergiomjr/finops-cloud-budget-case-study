import argparse
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.linear_model import LinearRegression


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names to make the script flexible for Kaggle CSV variations."""
    df = df.copy()
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )
    return df


def find_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for c in candidates:
        if c in df.columns:
            return c
    return None


def build_finops_kpis(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)

    date_col = find_col(df, ["date", "usage_date", "billing_date", "month", "period"])
    cost_col = find_col(df, ["cost", "actual_cost", "amount", "spend", "cloud_cost"])
    budget_col = find_col(df, ["budget", "planned_budget", "forecast_budget", "allocated_budget"])
    service_col = find_col(df, ["service", "cloud_service", "product", "resource_type"])
    team_col = find_col(df, ["team", "department", "business_unit", "cost_center"])
    env_col = find_col(df, ["environment", "env"])

    if cost_col is None:
        raise ValueError("Cost column not found. Rename the cost field to cost, actual_cost, amount, spend, or cloud_cost.")

    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df["month"] = df[date_col].dt.to_period("M").astype(str)
    else:
        df["month"] = "unknown"

    if budget_col is None:
        # Fallback: assume budget is 10% above monthly average cost.
        monthly_avg = df.groupby("month")[cost_col].transform("mean")
        df["budget"] = monthly_avg * 1.10
        budget_col = "budget"

    for col, default in [(service_col, "unknown_service"), (team_col, "unknown_team"), (env_col, "unknown_env")]:
        if col is None:
            continue
        df[col] = df[col].fillna(default).astype(str)

    group_cols = ["month"]
    if service_col:
        group_cols.append(service_col)
    if team_col:
        group_cols.append(team_col)
    if env_col:
        group_cols.append(env_col)

    kpis = (
        df.groupby(group_cols, dropna=False)
        .agg(
            actual_cost=(cost_col, "sum"),
            budget=(budget_col, "sum"),
            records=(cost_col, "count")
        )
        .reset_index()
    )

    kpis["budget_variance"] = kpis["actual_cost"] - kpis["budget"]
    kpis["budget_variance_pct"] = np.where(
        kpis["budget"] != 0,
        kpis["budget_variance"] / kpis["budget"],
        np.nan
    )

    mean_cost = kpis["actual_cost"].mean()
    std_cost = kpis["actual_cost"].std(ddof=0)
    kpis["z_score"] = np.where(std_cost != 0, (kpis["actual_cost"] - mean_cost) / std_cost, 0)
    kpis["anomaly_flag"] = np.where(kpis["z_score"].abs() >= 2, "Y", "N")

    kpis["recommendation"] = np.select(
        [
            kpis["budget_variance_pct"] > 0.20,
            kpis["anomaly_flag"].eq("Y"),
            kpis["budget_variance_pct"].between(0.05, 0.20, inclusive="both"),
            kpis["budget_variance_pct"] < -0.10,
        ],
        [
            "High overspend: review right-sizing, reserved capacity/Savings Plans, and unused resources.",
            "Anomaly detected: investigate recent deployments, data transfer, or scaling events.",
            "Moderate overspend: monitor trend and validate forecast assumptions.",
            "Under budget: check whether capacity is overestimated or budget can be reallocated.",
        ],
        default="Within budget: continue monitoring."
    )

    return kpis.sort_values(["month", "actual_cost"], ascending=[True, False])


def build_monthly_forecast(kpis: pd.DataFrame) -> pd.DataFrame:
    monthly = kpis.groupby("month", as_index=False)["actual_cost"].sum()
    monthly = monthly[monthly["month"] != "unknown"].copy()

    if len(monthly) < 3:
        monthly["forecast_next_month"] = np.nan
        return monthly

    monthly["month_num"] = np.arange(len(monthly))
    model = LinearRegression()
    model.fit(monthly[["month_num"]], monthly["actual_cost"])

    next_month_num = [[len(monthly)]]
    forecast = float(model.predict(next_month_num)[0])
    monthly["forecast_next_month"] = np.nan

    next_row = pd.DataFrame({
        "month": ["next_period"],
        "actual_cost": [np.nan],
        "month_num": [len(monthly)],
        "forecast_next_month": [forecast]
    })

    return pd.concat([monthly, next_row], ignore_index=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to raw cloud budget CSV")
    parser.add_argument("--output", required=True, help="Path to output KPI CSV")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    kpis = build_finops_kpis(df)
    forecast = build_monthly_forecast(kpis)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    kpis.to_csv(output_path, index=False)
    forecast.to_csv(output_path.parent / "monthly_forecast.csv", index=False)

    print("FinOps KPIs generated successfully.")
    print(f"KPI file: {output_path}")
    print(f"Forecast file: {output_path.parent / 'monthly_forecast.csv'}")
    print("\nTop 10 cost drivers:")
    print(kpis.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
