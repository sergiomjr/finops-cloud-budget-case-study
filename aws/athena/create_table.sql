-- Replace bucket name before running.
-- Athena is optional. Keep files small to avoid unexpected cost.

CREATE EXTERNAL TABLE IF NOT EXISTS finops_kpis (
  month string,
  service string,
  team string,
  actual_cost double,
  budget double,
  records int,
  budget_variance double,
  budget_variance_pct double,
  z_score double,
  anomaly_flag string,
  recommendation string
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
  "separatorChar" = ",",
  "quoteChar" = "\""
)
LOCATION 's3://finops-cloud-budget-sergio-2026/processed/'
TBLPROPERTIES (
  "skip.header.line.count"="1"
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
