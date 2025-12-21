{{ config(materialized='table') }}

WITH popular_zone AS (
    SELECT 
        COUNT(*) AS total_trips,
        pickup_zone,
        dropoff_zone,
        ROUND(SUM(fare_amount_usd), 2) AS total_fare_amount,
        ROUND(SUM(tip_amount_usd), 2) AS total_tip_amount,
        ROUND(AVG(trip_distance_miles), 2) AS avg_trip_distance,
        ROUND(AVG(passenger_count), 2) AS avg_passenger_count,
        taxi_color
    FROM {{ ref('int_all_trips') }}
    GROUP BY pickup_zone, dropoff_zone, taxi_color
)

SELECT * FROM popular_zone
