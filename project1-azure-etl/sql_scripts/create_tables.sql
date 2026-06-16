-- ============================================================
-- Azure ETL Pipeline — Table DDL
-- ============================================================

-- Cleansed Orders Table
CREATE TABLE dbo.orders_cleansed (
    order_id        VARCHAR(50)     NOT NULL PRIMARY KEY,
    customer_id     VARCHAR(50)     NOT NULL,
    order_date      DATETIME2       NOT NULL,
    product_id      VARCHAR(50)     NOT NULL,
    quantity        INT             NOT NULL,
    unit_price      DECIMAL(10,2)   NOT NULL,
    total_amount    DECIMAL(12,2)   NOT NULL,
    year_month      VARCHAR(7),
    etl_loaded_at   DATETIME2       DEFAULT GETUTCDATE()
);

-- ETL Watermark Table (tracks last load per entity)
CREATE TABLE dbo.etl_watermark (
    entity          VARCHAR(100)    NOT NULL PRIMARY KEY,
    last_load       DATETIME2       NOT NULL
);

-- Error Log Table
CREATE TABLE dbo.etl_error_log (
    error_id        INT             IDENTITY(1,1) PRIMARY KEY,
    source          VARCHAR(100),
    raw_data        NVARCHAR(MAX),
    logged_at       DATETIME2       DEFAULT GETUTCDATE()
);

-- Index for performance on date-range queries
CREATE NONCLUSTERED INDEX ix_orders_date
    ON dbo.orders_cleansed (order_date);

CREATE NONCLUSTERED INDEX ix_orders_customer
    ON dbo.orders_cleansed (customer_id);
