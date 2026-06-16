-- dbt model: fact_transactions
-- Grain: one row per financial transaction

{{
  config(
    materialized = 'incremental',
    unique_key   = 'transaction_key',
    incremental_strategy = 'merge'
  )
}}

WITH source AS (
    SELECT * FROM {{ ref('stg_transactions') }}
    {% if is_incremental() %}
        WHERE transaction_date > (SELECT MAX(transaction_date) FROM {{ this }})
    {% endif %}
),

dim_customer AS (
    SELECT customer_key, customer_id
    FROM {{ ref('dim_customer') }}
    WHERE is_current = 1
),

dim_account AS (
    SELECT account_key, account_id
    FROM {{ ref('dim_account') }}
    WHERE is_current = 1
),

dim_date AS (
    SELECT date_key, full_date
    FROM {{ ref('dim_date') }}
)

SELECT
    {{ dbt_utils.generate_surrogate_key(['t.transaction_id']) }}  AS transaction_key,
    t.transaction_id,
    c.customer_key,
    a.account_key,
    d.date_key                                                     AS transaction_date_key,
    t.transaction_date,
    t.transaction_type,
    t.amount,
    t.currency_code,
    t.amount * t.exchange_rate                                     AS amount_usd,
    t.channel,
    t.status,
    CURRENT_TIMESTAMP                                              AS etl_loaded_at

FROM source            t
LEFT JOIN dim_customer c ON t.customer_id = c.customer_id
LEFT JOIN dim_account  a ON t.account_id  = a.account_id
LEFT JOIN dim_date     d ON CAST(t.transaction_date AS DATE) = d.full_date
