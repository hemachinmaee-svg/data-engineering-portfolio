# Project 2 — PySpark Lakehouse: Retail Analytics

## Overview
Multi-layer (Bronze/Silver/Gold) Delta Lakehouse built on Azure Databricks processing
10M+ retail transaction records with PySpark transformations and Delta Lake optimisations.

## Architecture — Medallion Pattern
```
Raw CSV/JSON Files
      ↓
  BRONZE Layer   ← Raw ingestion, no transformation
      ↓
  SILVER Layer   ← Cleansed, validated, deduplicated
      ↓
  GOLD Layer     ← Aggregated, business-ready tables
```

## Key Features
- Medallion architecture (Bronze / Silver / Gold)
- Delta merge (upsert) for idempotent loads
- Data quality checks at each layer
- Optimised partitioning by date and region

## Tech Stack
| Tool | Purpose |
|------|---------|
| Azure Databricks | Compute & notebook orchestration |
| PySpark | Distributed data processing |
| Delta Lake | ACID transactions & time travel |
| Azure Data Lake Gen2 | Storage |

## Folder Structure
```
project2-pyspark-lakehouse/
├── notebooks/       # PySpark transformation notebooks
├── utils/           # Shared helper functions
├── config/          # Environment configs
└── README.md
```
