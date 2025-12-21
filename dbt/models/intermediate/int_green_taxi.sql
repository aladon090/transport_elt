-- models/intermediate/int_green_trips.sql

{{ config(materialized='view') }}

SELECT
    t.*,
    COALESCE(pu.zone, 'UNKNOWN') AS pickup_zone,
    COALESCE(pu.borough, 'UNKNOWN') AS pickup_borough,
    COALESCE(pu.service_zone, 'UNKNOWN') AS pickup_service_zone,
    COALESCE(do.zone, 'UNKNOWN') AS dropoff_zone,
    COALESCE(do.borough, 'UNKNOWN') AS dropoff_borough,
    COALESCE(do.service_zone, 'UNKNOWN') AS dropoff_service_zone
FROM {{ ref('stg_green_taxi') }} t
LEFT JOIN {{ ref('stg_taxi_zones') }} pu
    ON t.pickup_location_id = pu.location_id
LEFT JOIN {{ ref('stg_taxi_zones') }} do
    ON t.dropoff_location_id = do.location_id
