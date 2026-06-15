
--Passo 1 — Query: custo por Cloud Provider
SELECT
    cloud_provider,
    ROUND(SUM(total_net_cost), 2) AS total_net_cost,
    ROUND(SUM(total_list_cost), 2) AS total_list_cost,
    ROUND(SUM(total_list_cost) - SUM(total_net_cost), 2) AS estimated_savings
FROM finops_db.finops_kpis
GROUP BY cloud_provider
ORDER BY total_net_cost DESC;

--Passo 2 — Query: custo por ambiente

--SELECT
    environment,
    ROUND(SUM(total_net_cost), 2) AS total_net_cost,
    ROUND(SUM(total_on_demand_cost), 2) AS total_on_demand_cost,
    ROUND(SUM(total_amortized_cost), 2) AS total_amortized_cost
FROM finops_db.finops_kpis
GROUP BY environment
ORDER BY total_net_cost DESC;

--Passo 3 — Query: Actual vs Forecast
SELECT
    year_month,
    ROUND(SUM(total_net_cost), 2) AS actual_net_cost,
    ROUND(SUM(total_forecast_monthly_cost), 2) AS forecast_cost,
    ROUND(SUM(total_net_cost) - SUM(total_forecast_monthly_cost), 2) AS forecast_variance
FROM finops_db.finops_kpis
GROUP BY year_month
ORDER BY year_month;

--Passo 4 — Query: Actual vs Budget
SELECT
    year_month,
    ROUND(SUM(total_net_cost), 2) AS actual_net_cost,
    ROUND(SUM(total_budget_amount), 2) AS budget_amount,
    ROUND(SUM(total_net_cost) - SUM(total_budget_amount), 2) AS budget_variance,
    ROUND(AVG(avg_budget_utilization_pct) * 100, 4) AS avg_budget_utilization_percent
FROM finops_db.finops_kpis
GROUP BY year_month
ORDER BY year_month;

--Passo 5 — Query: anomalias por provider e ambiente
SELECT
    cloud_provider,
    environment,
    SUM(anomaly_count) AS total_anomalies,
    ROUND(SUM(total_net_cost), 2) AS total_net_cost
FROM finops_db.finops_kpis
GROUP BY cloud_provider, environment
ORDER BY total_anomalies DESC, total_net_cost DESC;

--Passo 6 — Query: top contas por custo
SELECT
    account_id,
    ROUND(SUM(total_net_cost), 2) AS total_net_cost,
    ROUND(SUM(total_forecast_monthly_cost), 2) AS forecast_cost,
    SUM(anomaly_count) AS total_anomalies
FROM finops_db.finops_kpis
GROUP BY account_id
ORDER BY total_net_cost DESC
LIMIT 10;

--Passo 7 — Criar uma view no Athena
CREATE OR REPLACE VIEW finops_db.vw_finops_monthly_summary AS
SELECT
    year_month,
    cloud_provider,
    environment,
    ROUND(SUM(total_net_cost), 2) AS actual_net_cost,
    ROUND(SUM(total_list_cost), 2) AS list_cost,
    ROUND(SUM(total_list_cost) - SUM(total_net_cost), 2) AS estimated_savings,
    ROUND(SUM(total_forecast_monthly_cost), 2) AS forecast_cost,
    ROUND(SUM(total_budget_amount), 2) AS budget_amount,
    SUM(anomaly_count) AS total_anomalies,
    SUM(row_count) AS total_records
FROM finops_db.finops_kpis
GROUP BY
    year_month,
    cloud_provider,
    environment;
	
SELECT *
FROM finops_db.vw_finops_monthly_summary
LIMIT 10;