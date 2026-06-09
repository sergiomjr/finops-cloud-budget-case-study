import os
import io
import boto3
import pandas as pd
import numpy as np

s3 = boto3.client("s3")


def normalize_columns(df):
    df = df.copy()
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )
    return df


def find_col(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None


def lambda_handler(event, context):
    bucket = os.environ["BUCKET_NAME"]
    input_key = os.environ.get("INPUT_KEY", "raw/cloud_budget.csv")
    output_key = os.environ.get("OUTPUT_KEY", "processed/finops_kpis.csv")

    obj = s3.get_object(Bucket=bucket, Key=input_key)
    df = pd.read_csv(obj["Body"])
    df = normalize_columns(df)

    date_col = find_col(df, ["date", "usage_date", "billing_date", "month", "period"])
    cost_col = find_col(df, ["cost", "actual_cost", "amount", "spend", "cloud_cost"])
    budget_col = find_col(df, ["budget", "planned_budget", "forecast_budget", "allocated_budget"])
    service_col = find_col(df, ["service", "cloud_service", "product", "resource_type"])
    team_col = find_col(df, ["team", "department", "business_unit", "cost_center"])

    if cost_col is None:
        raise ValueError("Cost column not found.")

    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df["month"] = df[date_col].dt.to_period("M").astype(str)
    else:
        df["month"] = "unknown"

    if budget_col is None:
        df["budget"] = df.groupby("month")[cost_col].transform("mean") * 1.10
        budget_col = "budget"

    group_cols = ["month"]
    if service_col:
        group_cols.append(service_col)
    if team_col:
        group_cols.append(team_col)

    kpis = (
        df.groupby(group_cols, dropna=False)
        .agg(actual_cost=(cost_col, "sum"), budget=(budget_col, "sum"))
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

    csv_buffer = io.StringIO()
    kpis.to_csv(csv_buffer, index=False)

    s3.put_object(
        Bucket=bucket,
        Key=output_key,
        Body=csv_buffer.getvalue().encode("utf-8"),
        ContentType="text/csv"
    )

    return {
        "statusCode": 200,
        "body": f"KPIs generated at s3://{bucket}/{output_key}",
        "rows": len(kpis)
    }
