# Project 3 — SQL Data Warehouse: Finance DWH

## Overview
Production-ready star schema data warehouse for a financial institution with dbt models,
slowly changing dimensions (SCD Type 2), and automated testing.

## Schema Design
```
                  ┌─────────────────┐
                  │  fact_transactions │
                  └────────┬────────┘
          ┌────────────────┼───────────────┐
          ▼                ▼               ▼
   dim_customer      dim_account      dim_date
   (SCD Type 2)      (SCD Type 2)    (Static)
```

## Key Features
- Star schema optimised for analytical queries
- SCD Type 2 for customer and account dimensions
- dbt models with full lineage
- Automated dbt tests (uniqueness, not-null, referential integrity)
- Stored procedures for batch loads

## Tech Stack
| Tool | Purpose |
|------|---------|
| SQL Server / Azure SQL | Data warehouse engine |
| dbt | Transformation framework |
| Python | Data generation & batch load |

## Folder Structure
```
project3-sql-dwh/
├── models/         # dbt models (staging, dimensions, facts)
├── procedures/     # SQL stored procedures
├── tests/          # dbt test definitions
├── seeds/          # Static reference data (dim_date)
└── README.md
```
