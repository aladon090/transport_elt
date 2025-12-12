{{ config(materialized="table") }}

with
    fact_table_per_hour as (
        select
            date(pickup_datetime) as trip_date,
            extract(hour from pickup_datetime) as trip_hour,
            taxi_color,

            count(*) as total_trips,

            -- Revenue (use total_amount_usd; it already includes fare + extras +
            -- tolls + tip)
            round(sum(total_amount_usd), 2) as total_amount_usd,
            round(sum(fare_amount_usd), 2) as total_fare_amount_usd,
            round(sum(tip_amount_usd), 2) as total_tip_amount_usd,

            round(avg(trip_distance_miles), 2) as avg_trip_distance_miles,
            round(avg(passenger_count), 2) as avg_passenger_count
        from {{ ref("int_all_trips") }}

        where trip_distance_miles > 0

        group by trip_date, trip_hour, taxi_color
    )

select *
from fact_table_per_hour
