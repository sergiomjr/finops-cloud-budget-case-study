# Interview Talking Points — Junior Cloud FinOps Analyst

## 1. Elevator pitch

I built a FinOps case study using a cloud budget dataset from Kaggle. The goal was to simulate the daily work of a Junior Cloud FinOps Analyst: track actual cloud costs against budget, identify cost drivers, detect anomalies, forecast future spend, and provide actionable optimization recommendations.

## 2. Why this project is relevant to CSG

The role asks for dashboard creation, cost tracking against forecast and budget, identifying optimization opportunities, building forecasts, developing KPIs, and communicating recommendations to leadership. This project covers those points in a small but practical way.

## 3. FinOps concepts used

- Visibility: cost by month, service, team, and environment.
- Accountability: grouping spend by owner, department, or cost center.
- Optimization: recommendations for right-sizing, lifecycle policy, reserved capacity, and reducing idle resources.
- Forecasting: simple linear model or moving average to estimate future spend.
- Anomaly detection: z-score to flag unusual spending patterns.

## 4. AWS concepts used

- S3 as a low-cost data lake layer.
- Lambda as serverless processing.
- Athena as optional SQL analytics over S3.
- Cost Explorer as native AWS tool for cost and usage analysis.
- AWS Budgets to prevent unexpected cost.

## 5. Business recommendations examples

- If EC2 is above budget: review instance utilization, schedule non-production shutdown, evaluate Savings Plans or Reserved Instances for stable workloads.
- If S3 cost grows: apply lifecycle policies and review storage class.
- If Lambda cost grows: optimize memory, timeout, and invocation volume.
- If data transfer spikes: investigate cross-region traffic and architecture changes.
- If a team is consistently over budget: create a dedicated budget and improve tagging.

## 6. How to explain limitations

The dataset is synthetic, so the recommendations are based on simulated billing behavior. In a real company, I would validate the analysis using AWS Cost Explorer, Cost and Usage Report, resource tags, utilization metrics from CloudWatch, and input from engineering/product teams.
