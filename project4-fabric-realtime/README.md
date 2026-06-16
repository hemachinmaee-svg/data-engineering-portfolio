# Project 4 — Microsoft Fabric: Real-Time Sales Intelligence

## Overview
Real-time sales event streaming pipeline using Microsoft Fabric Eventstream,
KQL Database, and Lakehouse for sub-second analytics on live POS data.

## Architecture
```
POS Systems (JSON Events)
        ↓
Fabric Eventstream (Ingest & Route)
        ↓
   KQL Database          Lakehouse (Delta)
  (Real-time)        (Historical / Batch)
        ↓                     ↓
Real-Time Dashboard     Power BI Reports
```

## Key Features
- Sub-second event ingestion via Eventstream
- KQL queries for real-time aggregations
- Fabric notebooks for batch reconciliation
- Live dashboard with auto-refresh

## Tech Stack
| Tool | Purpose |
|------|---------|
| Microsoft Fabric Eventstream | Real-time event ingestion |
| KQL Database | Real-time analytics store |
| Fabric Lakehouse | Historical storage |
| Fabric Notebooks | PySpark batch processing |
| Power BI | Real-time dashboards |

## Folder Structure
```
project4-fabric-realtime/
├── kql_queries/          # KQL analytics queries
├── notebooks/            # Fabric notebook scripts
├── eventstream_config/   # Event schema definitions
└── README.md
```
