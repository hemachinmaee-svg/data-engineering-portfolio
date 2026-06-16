-- dbt model: dim_customer (SCD Type 2)
-- Tracks full history of customer attribute changes

{{
  config(
    materialized = 'table',
    unique_key   = 'customer_key'
  )
}}

WITH source AS (
    SELECT * FROM {{ ref('stg_customers') }}
),

-- Detect changed records from existing dimension
changes AS (
    SELECT
        s.customer_id,
        s.first_name,
        s.last_name,
        s.email,
        s.phone,
        s.segment,
        s.country,
        s.city,
        CASE
            WHEN d.customer_id IS NULL THEN 'NEW'
            WHEN d.email    <> s.email
              OR d.segment  <> s.segment
              OR d.country  <> s.country THEN 'CHANGED'
            ELSE 'UNCHANGED'
        END AS change_type
    FROM source s
    LEFT JOIN {{ this }} d
        ON s.customer_id = d.customer_id AND d.is_current = 1
),

-- Build SCD Type 2 output
scd2 AS (
    SELECT
        {{ dbt_utils.generate_surrogate_key(['customer_id', 'CURRENT_TIMESTAMP']) }} AS customer_key,
        customer_id,
        first_name,
        last_name,
        email,
        phone,
        segment,
        country,
        city,
        CURRENT_TIMESTAMP   AS effective_from,
        CAST('9999-12-31' AS DATE) AS effective_to,
        1                   AS is_current
    FROM changes
    WHERE change_type IN ('NEW', 'CHANGED')
)

SELECT * FROM scd2
