{{ config(
    materialized='view',
    alias='stg_taxi_zones'
) }}


WITH raw_taxi_data AS( 

    SELECT * 
    FROM `taxi-transport-analytics.new_york_analytic.taxi_zone`
)
,
final_taxizone  AS (

SELECT
    CAST(COALESCE(LocationID, -1) AS INT64) AS location_id,
    COALESCE(Borough, 'UNKNOWN') AS borough,
    COALESCE(Zone, 'UNKNOWN') AS zone,
    COALESCE(service_zone, 'UNKNOWN') AS service_zone
FROM raw_taxi_data

)

SELECT * FROM final_taxizone