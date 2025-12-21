{{ config(materialized='table') }}

WITH fact_table_perday AS (
    SELECT 
        DATE(pickup_datetime) AS trip_date,
        taxi_color,
        COUNT(*) AS total_trips,
        ROUND(SUM(fare_amount_usd),2) AS total_fare_amount,
        ROUND(SUM(tip_amount_usd),2) AS total_tip_amount,
        ROUND(AVG(trip_distance_miles),2) AS avg_trip_distance,
        ROUND (AVG(passenger_count),2) AS avg_passenger_count
    FROM {{ ref('int_all_trips') }}
    WHERE trip_distance_miles > 0  -- optional filter to remove zero-distance trips
    GROUP BY trip_date, taxi_color
)

SELECT *
FROM fact_table_perday
ORDER BY trip_date, taxi_color
