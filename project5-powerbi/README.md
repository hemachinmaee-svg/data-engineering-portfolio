# Project 5 — Power BI: Retail Executive Dashboard

## Overview
Executive-level Power BI report with advanced DAX measures, row-level security,
time intelligence, and a fully documented semantic model.

## Dashboard Pages
1. **Executive Summary** — KPIs: Revenue, Margin, Units Sold, YoY Growth
2. **Sales Trends** — Monthly/Weekly revenue with time intelligence comparisons
3. **Product Performance** — Top/bottom performers, margin analysis
4. **Regional Breakdown** — Map visual with drill-through to store level
5. **Customer Analytics** — Segment analysis, repeat purchase rate

## Key Features
- DAX time intelligence (YTD, MTD, YoY, rolling averages)
- Row-level security (RLS) by region/manager
- Composite model (Import + DirectQuery)
- Deployment pipeline config (Dev → Test → Prod)
- Fully documented semantic model

## Tech Stack
| Tool | Purpose |
|------|---------|
| Power BI Desktop | Report development |
| DAX | Measures & KPIs |
| Power Query (M) | Data transformation |
| Power BI Service | Publishing & sharing |

## Folder Structure
```
project5-powerbi/
├── dax_measures/      # All DAX measure definitions
├── documentation/     # Semantic model documentation
├── deployment/        # Deployment pipeline config
└── README.md
```
