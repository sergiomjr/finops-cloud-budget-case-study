-- Replace bucket name before running.
-- Athena is optional. Keep files small to avoid unexpected cost.

CREATE EXTERNAL TABLE IF NOT EXISTS finops_db.finops_kpis (
    year_month string,
    cloud_provider string,
    account_id string,
    environment string,
    total_list_cost double,
    total_net_cost double,
    total_on_demand_cost double,
    total_amortized_cost double,
    total_forecast_monthly_cost double,
    total_budget_amount double,
    avg_budget_utilization_pct double,
    avg_cost_variance_7d_pct double,
    avg_cost_variance_30d_pct double,
    anomaly_count bigint,
    row_count bigint
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
    'separatorChar' = ',',
    'quoteChar' = '"',
    'escapeChar' = '\\'
)
STORED AS TEXTFILE
LOCATION 's3://finops-cloud-budget-sergiomjr-2026-523271872890-us-east-2-an/processed/'
TBLPROPERTIES (
    'skip.header.line.count'='1'
);

-- Example queries

SELECT
  month,
  SUM(actual_cost) AS total_cost,
  SUM(budget) AS total_budget,
  SUM(budget_variance) AS variance
FROM finops_kpis
GROUP BY month
ORDER BY month;

SELECT
  service,
  SUM(actual_cost) AS total_cost
FROM finops_kpis
GROUP BY service
ORDER BY total_cost DESC
LIMIT 5;

SELECT *
FROM finops_kpis
WHERE anomaly_flag = 'Y'
ORDER BY ABS(z_score) DESC;
