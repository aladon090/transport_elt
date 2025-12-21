-- models/staging/stg_yellow_taxi.sql

{{ config(
    materialized='view',
    alias='stg_yellow_taxi'
) }}

WITH raw_yellow_data AS (
    SELECT * 
    FROM `taxi-transport-analytics.new_york_analytic.yellow_taxi`
),

final_yellow_stg AS (
    SELECT
        CAST(VendorID AS INT64) AS vendor_id,
        CAST(tpep_pickup_datetime AS TIMESTAMP) AS pickup_datetime,
        CAST(tpep_dropoff_datetime AS TIMESTAMP) AS dropoff_datetime,
        store_and_fwd_flag AS store_and_forward_flag,
        CAST(RatecodeID AS INT64) AS rate_code_id,
        CAST(PULocationID AS INT64) AS pickup_location_id,
        CAST(DOLocationID AS INT64) AS dropoff_location_id,
        CAST(passenger_count AS INT64) AS passenger_count,
        CAST(trip_distance AS FLOAT64) AS trip_distance_miles,
        CAST(fare_amount AS FLOAT64) AS fare_amount_usd,
        CAST(extra AS FLOAT64) AS extra_charges_usd,
        CAST(mta_tax AS FLOAT64) AS mta_tax_usd,
        CAST(tip_amount AS FLOAT64) AS tip_amount_usd,
        CAST(tolls_amount AS FLOAT64) AS tolls_amount_usd,
        CAST(improvement_surcharge AS FLOAT64) AS improvement_surcharge_usd,
        CAST(total_amount AS FLOAT64) AS total_amount_usd,
        CAST(payment_type AS INT64) AS payment_type_code,
        CAST(congestion_surcharge AS FLOAT64) AS congestion_surcharge_usd
    FROM raw_yellow_data
)

SELECT * 
FROM final_yellow_stg
