"""
ETL Script: E-Commerce Orders Pipeline
Reads raw orders from Azure Blob Storage, validates, transforms,
and loads into Azure SQL Database with incremental load support.
"""

import pyodbc
import pandas as pd
import logging
import json
from datetime import datetime
from azure.storage.blob import BlobServiceClient

# ── Logging Setup ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


# ── Config Loader ──────────────────────────────────────────────
def load_config(path="config/config.json"):
    with open(path) as f:
        return json.load(f)


# ── Blob Storage Reader ────────────────────────────────────────
def read_blob_csv(config, container: str, blob_name: str) -> pd.DataFrame:
    logger.info(f"Reading blob: {container}/{blob_name}")
    client = BlobServiceClient.from_connection_string(config["blob_connection_string"])
    blob = client.get_blob_client(container=container, blob=blob_name)
    data = blob.download_blob().readall()
    df = pd.read_csv(pd.io.common.BytesIO(data))
    logger.info(f"Loaded {len(df)} rows from blob")
    return df


# ── Schema Validation ──────────────────────────────────────────
REQUIRED_COLUMNS = ["order_id", "customer_id", "order_date", "product_id", "quantity", "unit_price"]

def validate_schema(df: pd.DataFrame) -> pd.DataFrame:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Separate valid vs invalid rows
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    invalid = df[df["order_date"].isna() | df["quantity"].le(0) | df["unit_price"].le(0)]
    valid = df.drop(invalid.index)

    logger.info(f"Valid rows: {len(valid)} | Invalid rows: {len(invalid)}")
    return valid, invalid


# ── Transformation ─────────────────────────────────────────────
def transform_orders(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["total_amount"] = df["quantity"] * df["unit_price"]
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["year_month"] = df["order_date"].dt.to_period("M").astype(str)
    df["etl_loaded_at"] = datetime.utcnow()
    df.columns = [c.lower().strip() for c in df.columns]
    return df


# ── Watermark (Incremental Load) ───────────────────────────────
def get_watermark(conn) -> datetime:
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(order_date) FROM dbo.orders_cleansed")
    row = cursor.fetchone()
    return row[0] if row[0] else datetime(2000, 1, 1)


def update_watermark(conn, new_mark: datetime):
    cursor = conn.cursor()
    cursor.execute(
        "MERGE dbo.etl_watermark AS t "
        "USING (SELECT 'orders' AS entity, ? AS last_load) AS s "
        "ON t.entity = s.entity "
        "WHEN MATCHED THEN UPDATE SET last_load = s.last_load "
        "WHEN NOT MATCHED THEN INSERT (entity, last_load) VALUES (s.entity, s.last_load);",
        new_mark
    )
    conn.commit()


# ── SQL Loader ─────────────────────────────────────────────────
def load_to_sql(df: pd.DataFrame, config: dict, conn):
    cursor = conn.cursor()
    rows_inserted = 0
    for _, row in df.iterrows():
        cursor.execute("""
            MERGE dbo.orders_cleansed AS t
            USING (SELECT ? AS order_id) AS s ON t.order_id = s.order_id
            WHEN NOT MATCHED THEN
                INSERT (order_id, customer_id, order_date, product_id,
                        quantity, unit_price, total_amount, year_month, etl_loaded_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        row["order_id"],
        row["order_id"], row["customer_id"], row["order_date"],
        row["product_id"], row["quantity"], row["unit_price"],
        row["total_amount"], row["year_month"], row["etl_loaded_at"]
        )
        rows_inserted += 1
    conn.commit()
    logger.info(f"Inserted/merged {rows_inserted} rows into dbo.orders_cleansed")


# ── Error Logger ───────────────────────────────────────────────
def log_errors(invalid_df: pd.DataFrame, conn):
    if invalid_df.empty:
        return
    cursor = conn.cursor()
    for _, row in invalid_df.iterrows():
        cursor.execute(
            "INSERT INTO dbo.etl_error_log (source, raw_data, logged_at) VALUES (?, ?, ?)",
            "orders", str(row.to_dict()), datetime.utcnow()
        )
    conn.commit()
    logger.warning(f"Logged {len(invalid_df)} error rows to dbo.etl_error_log")


# ── Main ───────────────────────────────────────────────────────
def main():
    config = load_config()
    conn = pyodbc.connect(config["sql_connection_string"])

    watermark = get_watermark(conn)
    logger.info(f"Incremental load from: {watermark}")

    raw_df = read_blob_csv(config, container="raw-data", blob_name="orders.csv")
    raw_df["order_date"] = pd.to_datetime(raw_df["order_date"], errors="coerce")
    raw_df = raw_df[raw_df["order_date"] > watermark]

    if raw_df.empty:
        logger.info("No new records to process.")
        return

    valid_df, invalid_df = validate_schema(raw_df)
    transformed_df = transform_orders(valid_df)
    load_to_sql(transformed_df, config, conn)
    log_errors(invalid_df, conn)
    update_watermark(conn, transformed_df["order_date"].max())

    conn.close()
    logger.info("ETL pipeline completed successfully.")


if __name__ == "__main__":
    main()
