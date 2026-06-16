# Databricks notebook: Gold Layer Aggregations
# Silver → Gold: Business-ready aggregated tables

from pyspark.sql import functions as F

SILVER_PATH = "abfss://lakehouse@yourstorage.dfs.core.windows.net/silver/transactions/"
GOLD_PATH   = "abfss://lakehouse@yourstorage.dfs.core.windows.net/gold/"

silver_df = spark.read.format("delta").load(SILVER_PATH)

# ── Gold Table 1: Daily Sales by Store & Region ─────────────────
daily_sales = (
    silver_df
    .groupBy("txn_date", "store_id", "region")
    .agg(
        F.sum("total_amount").alias("total_revenue"),
        F.sum("quantity").alias("units_sold"),
        F.countDistinct("transaction_id").alias("transaction_count"),
        F.countDistinct("customer_id").alias("unique_customers"),
        F.avg("unit_price").alias("avg_unit_price")
    )
    .withColumn("gold_loaded_at", F.current_timestamp())
)

(daily_sales.write.format("delta")
    .partitionBy("region", "txn_date")
    .mode("overwrite")
    .save(f"{GOLD_PATH}daily_sales/"))

print("Gold: daily_sales written")

# ── Gold Table 2: Product Performance ──────────────────────────
product_perf = (
    silver_df
    .groupBy("product_id", "txn_year", "txn_month")
    .agg(
        F.sum("total_amount").alias("monthly_revenue"),
        F.sum("quantity").alias("units_sold"),
        F.countDistinct("store_id").alias("stores_selling"),
        F.avg("unit_price").alias("avg_price")
    )
    .withColumn("gold_loaded_at", F.current_timestamp())
)

(product_perf.write.format("delta")
    .partitionBy("txn_year", "txn_month")
    .mode("overwrite")
    .save(f"{GOLD_PATH}product_performance/"))

print("Gold: product_performance written")

# ── Gold Table 3: Customer RFM Summary ─────────────────────────
from pyspark.sql.window import Window

latest_date = silver_df.agg(F.max("txn_date")).collect()[0][0]

rfm = (
    silver_df
    .groupBy("customer_id")
    .agg(
        F.datediff(F.lit(latest_date), F.max("txn_date")).alias("recency_days"),
        F.count("transaction_id").alias("frequency"),
        F.sum("total_amount").alias("monetary_value")
    )
)

(rfm.write.format("delta")
    .mode("overwrite")
    .save(f"{GOLD_PATH}customer_rfm/"))

print("Gold: customer_rfm written")
