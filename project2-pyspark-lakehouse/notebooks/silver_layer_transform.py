# Databricks notebook: Silver Layer Transformation
# Bronze → Silver: Cleanse, validate, deduplicate retail transactions

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType
from delta.tables import DeltaTable

spark = SparkSession.builder.appName("RetailLakehouse_Silver").getOrCreate()

# ── Paths ───────────────────────────────────────────────────────
BRONZE_PATH = "abfss://lakehouse@yourstorage.dfs.core.windows.net/bronze/transactions/"
SILVER_PATH = "abfss://lakehouse@yourstorage.dfs.core.windows.net/silver/transactions/"

# ── Schema Enforcement ──────────────────────────────────────────
schema = StructType([
    StructField("transaction_id",  StringType(),    False),
    StructField("store_id",        StringType(),    True),
    StructField("product_id",      StringType(),    True),
    StructField("customer_id",     StringType(),    True),
    StructField("quantity",        IntegerType(),   True),
    StructField("unit_price",      DoubleType(),    True),
    StructField("transaction_date",TimestampType(), True),
    StructField("region",          StringType(),    True),
])

# ── Read Bronze ─────────────────────────────────────────────────
bronze_df = spark.read.format("delta").load(BRONZE_PATH)
print(f"Bronze record count: {bronze_df.count():,}")

# ── Data Quality Checks ─────────────────────────────────────────
def check_quality(df):
    total = df.count()
    nulls = df.filter(
        F.col("transaction_id").isNull() |
        F.col("quantity").isNull() |
        F.col("unit_price").isNull()
    ).count()
    negatives = df.filter((F.col("quantity") <= 0) | (F.col("unit_price") <= 0)).count()
    print(f"Quality Report — Total: {total:,} | Nulls: {nulls:,} | Negatives: {negatives:,}")
    return df.filter(
        F.col("transaction_id").isNotNull() &
        F.col("quantity").isNotNull() &
        F.col("unit_price").isNotNull() &
        (F.col("quantity") > 0) &
        (F.col("unit_price") > 0)
    )

# ── Transformations ─────────────────────────────────────────────
def transform_silver(df):
    return (
        df
        # Deduplicate on transaction_id, keep latest
        .dropDuplicates(["transaction_id"])
        # Derived columns
        .withColumn("total_amount",  F.round(F.col("quantity") * F.col("unit_price"), 2))
        .withColumn("transaction_date", F.to_timestamp("transaction_date"))
        .withColumn("txn_year",  F.year("transaction_date"))
        .withColumn("txn_month", F.month("transaction_date"))
        .withColumn("txn_date",  F.to_date("transaction_date"))
        # Standardise strings
        .withColumn("region",    F.upper(F.trim(F.col("region"))))
        .withColumn("store_id",  F.trim(F.col("store_id")))
        # Audit column
        .withColumn("silver_loaded_at", F.current_timestamp())
    )

# ── Delta Merge (Upsert) ────────────────────────────────────────
def upsert_to_silver(new_df):
    if DeltaTable.isDeltaTable(spark, SILVER_PATH):
        silver_table = DeltaTable.forPath(spark, SILVER_PATH)
        (
            silver_table.alias("t")
            .merge(new_df.alias("s"), "t.transaction_id = s.transaction_id")
            .whenMatchedUpdateAll()
            .whenNotMatchedInsertAll()
            .execute()
        )
        print("Delta merge completed.")
    else:
        # First run — write partitioned table
        (
            new_df.write
            .format("delta")
            .partitionBy("txn_year", "txn_month", "region")
            .mode("overwrite")
            .save(SILVER_PATH)
        )
        print("Silver table created.")

# ── Optimise Delta Table ────────────────────────────────────────
def optimise_silver():
    spark.sql(f"OPTIMIZE delta.`{SILVER_PATH}` ZORDER BY (store_id, product_id)")
    print("OPTIMIZE + ZORDER completed.")

# ── Run Pipeline ────────────────────────────────────────────────
clean_df   = check_quality(bronze_df)
silver_df  = transform_silver(clean_df)
upsert_to_silver(silver_df)
optimise_silver()

print(f"Silver record count: {silver_df.count():,}")
