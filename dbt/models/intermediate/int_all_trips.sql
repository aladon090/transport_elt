{{ config(materialized='view') }}

-- Union of Green and Yellow taxi trips
SELECT
    vendor_id,
    pickup_datetime,
    dropoff_datetime,
    store_and_forward_flag,
    rate_code_id,
    pickup_location_id,
    dropoff_location_id,
    passenger_count,
    trip_distance_miles,
    fare_amount_usd,
    extra_charges_usd,
    mta_tax_usd,
    tip_amount_usd,
    tolls_amount_usd,
    improvement_surcharge_usd,
    total_amount_usd,
    payment_type_code,
    trip_type_code,
    congestion_surcharge_usd,
    ehail_fee_usd,
    pickup_zone,
    pickup_borough,
    pickup_service_zone,
    dropoff_zone,
    dropoff_borough,
    dropoff_service_zone,
    'green' AS taxi_color
FROM {{ ref('int_green_taxi') }}

UNION ALL

SELECT
    vendor_id,
    pickup_datetime,
    dropoff_datetime,
    store_and_forward_flag,
    rate_code_id,
    pickup_location_id,
    dropoff_location_id,
    passenger_count,
    trip_distance_miles,
    fare_amount_usd,
    extra_charges_usd,
    mta_tax_usd,
    tip_amount_usd,
    tolls_amount_usd,
    improvement_surcharge_usd,
    total_amount_usd,
    payment_type_code,
    NULL AS trip_type_code,        -- Yellow taxi missing trip_type
    congestion_surcharge_usd,
    NULL AS ehail_fee_usd,         -- Yellow taxi missing ehail_fee
    pickup_zone,
    pickup_borough,
    pickup_service_zone,
    dropoff_zone,
    dropoff_borough,
    dropoff_service_zone,
    'yellow' AS taxi_color
FROM {{ ref('int_yellow_taxi') }}
