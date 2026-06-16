# Project 1 — Azure ETL Pipeline: E-Commerce Data Platform

## Overview
End-to-end ETL pipeline ingesting raw e-commerce orders, customers, and products
from Azure Blob Storage into a cleansed Azure SQL Database using Azure Data Factory and Python.

## Architecture
```
Azure Blob Storage (Raw CSV/JSON)
        ↓
Azure Data Factory (Orchestration)
        ↓
Python Transformation Scripts
        ↓
Azure SQL Database (Cleansed & Validated)
```

## Key Features
- Incremental loads using watermark pattern
- Schema validation on ingest
- Error logging to dedicated error table
- Parameterised ADF pipelines (reusable across entities)

## Tech Stack
| Tool | Purpose |
|------|---------|
| Azure Data Factory | Pipeline orchestration |
| Azure Blob Storage | Raw data landing zone |
| Azure SQL Database | Cleansed data storage |
| Python | Transformation logic |

## Folder Structure
```
project1-azure-etl/
├── adf_pipelines/       # ADF pipeline JSON definitions
├── python_scripts/      # ETL transformation scripts
├── sql_scripts/         # Table DDL and stored procedures
├── config/              # Config templates
└── README.md
```

## How to Run
1. Deploy SQL scripts in `sql_scripts/` to your Azure SQL instance
2. Import ADF pipeline JSON from `adf_pipelines/` into your ADF instance
3. Update `config/config.json` with your connection strings
4. Trigger pipeline manually or set a schedule trigger in ADF
