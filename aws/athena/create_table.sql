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
    year_month,
    ROUND(SUM(total_net_cost), 2) AS actual_net_cost,
    ROUND(SUM(total_forecast_monthly_cost), 2) AS forecast_cost,
    ROUND(SUM(total_budget_amount), 2) AS budget_amount
FROM finops_db.finops_kpis
GROUP BY year_month
ORDER BY year_month;

SELECT
    cloud_provider,
    ROUND(SUM(total_net_cost), 2) AS total_net_cost
FROM finops_db.finops_kpis
GROUP BY cloud_provider
ORDER BY total_net_cost DESC
LIMIT 5;

SELECT *
FROM finops_db.finops_kpis
WHERE anomaly_count > 0
ORDER BY anomaly_count DESC, total_net_cost DESC;
