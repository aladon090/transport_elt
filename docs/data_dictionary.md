# Data Dictionary - NYC Taxi Trip Data

This document provides detailed information about the data schema at each layer of the ELT pipeline.

## Table of Contents
1. [Source Data](#source-data)
2. [Staging Layer](#staging-layer)
3. [Intermediate Layer](#intermediate-layer)
4. [Marts Layer](#marts-layer)
5. [Data Quality Rules](#data-quality-rules)

---

## Source Data

### Raw Yellow Taxi Data
Source: NYC TLC Yellow Taxi Trip Records

| Column Name | Data Type | Description | Example |
|------------|-----------|-------------|---------|
| `VendorID` | INTEGER | Provider identifier (1=Creative, 2=VeriFone) | 2 |
| `tpep_pickup_datetime` | TIMESTAMP | Pick-up date and time | 2019-12-01 00:00:00 |
| `tpep_dropoff_datetime` | TIMESTAMP | Drop-off date and time | 2019-12-01 00:15:00 |
| `passenger_count` | INTEGER | Number of passengers | 1 |
| `trip_distance` | FLOAT | Trip distance in miles | 1.50 |
| `RatecodeID` | INTEGER | Rate code (1=Standard, 2=JFK, etc.) | 1 |
| `store_and_fwd_flag` | STRING | Trip record held in memory (Y/N) | N |
| `PULocationID` | INTEGER | Pick-up location ID | 161 |
| `DOLocationID` | INTEGER | Drop-off location ID | 239 |
| `payment_type` | INTEGER | Payment method (1=Credit, 2=Cash, etc.) | 1 |
| `fare_amount` | FLOAT | Meter fare | 7.50 |
| `extra` | FLOAT | Extra charges | 0.50 |
| `mta_tax` | FLOAT | MTA tax | 0.50 |
| `tip_amount` | FLOAT | Tip amount | 1.65 |
| `tolls_amount` | FLOAT | Tolls | 0.00 |
| `improvement_surcharge` | FLOAT | Improvement surcharge | 0.30 |
| `total_amount` | FLOAT | Total charge | 10.45 |
| `congestion_surcharge` | FLOAT | Congestion surcharge | 0.00 |

### Raw Green Taxi Data
Source: NYC TLC Green Taxi Trip Records

Similar schema to Yellow Taxi with additional fields:

| Column Name | Data Type | Description | Example |
|------------|-----------|-------------|---------|
| `lpep_pickup_datetime` | TIMESTAMP | Pick-up date and time | 2019-12-01 00:00:00 |
| `lpep_dropoff_datetime` | TIMESTAMP | Drop-off date and time | 2019-12-01 00:15:00 |
| `ehail_fee` | FLOAT | E-hail fee | 0.00 |
| `trip_type` | INTEGER | 1=Street-hail, 2=Dispatch | 1 |

### Taxi Zone Lookup
Source: NYC TLC Taxi Zone Lookup

| Column Name | Data Type | Description | Example |
|------------|-----------|-------------|---------|
| `LocationID` | INTEGER | Taxi zone location ID | 1 |
| `Borough` | STRING | NYC borough | Manhattan |
| `Zone` | STRING | Zone name | Newark Airport |
| `service_zone` | STRING | Service zone type | EWR |

---

## Staging Layer

### stg_yellow_taxi

Cleaned and standardized yellow taxi trip data.

| Column Name | Data Type | Description | Transformation |
|------------|-----------|-------------|----------------|
| `trip_id` | STRING | Unique trip identifier | Generated |
| `vendor_id` | INTEGER | Provider identifier | Cleaned |
| `pickup_datetime` | TIMESTAMP | Pick-up timestamp | Renamed from tpep_pickup_datetime |
| `dropoff_datetime` | TIMESTAMP | Drop-off timestamp | Renamed from tpep_dropoff_datetime |
| `passenger_count` | INTEGER | Number of passengers | Validated (1-6) |
| `trip_distance` | FLOAT | Trip distance in miles | Validated (>0) |
| `pickup_location_id` | INTEGER | Pick-up zone | Renamed from PULocationID |
| `dropoff_location_id` | INTEGER | Drop-off zone | Renamed from DOLocationID |
| `rate_code_id` | INTEGER | Rate code | Cleaned |
| `payment_type` | INTEGER | Payment method | Cleaned |
| `fare_amount` | FLOAT | Base fare | Validated (>=0) |
| `extra` | FLOAT | Extra charges | Validated (>=0) |
| `mta_tax` | FLOAT | MTA tax | Validated (>=0) |
| `tip_amount` | FLOAT | Tip | Validated (>=0) |
| `tolls_amount` | FLOAT | Tolls | Validated (>=0) |
| `total_amount` | FLOAT | Total charge | Validated (>0) |
| `taxi_type` | STRING | Taxi type | Constant: 'yellow' |

**Data Quality Rules:**
- Filter invalid passenger counts (< 1 or > 6)
- Remove trips with distance <= 0
- Remove trips with negative amounts
- Remove trips with pickup = dropoff

### stg_green_taxi

Cleaned and standardized green taxi trip data. Similar schema to `stg_yellow_taxi` with `taxi_type = 'green'`.

### stg_taxi_zones

Taxi zone dimension table.

| Column Name | Data Type | Description | Transformation |
|------------|-----------|-------------|----------------|
| `location_id` | INTEGER | Zone identifier | Renamed from LocationID |
| `borough` | STRING | NYC borough | Cleaned |
| `zone_name` | STRING | Zone name | Renamed from Zone |
| `service_zone` | STRING | Service type | Cleaned |

---

## Intermediate Layer

### int_all_trips

Combined yellow and green taxi trips with enrichments.

| Column Name | Data Type | Description | Source |
|------------|-----------|-------------|---------|
| `trip_id` | STRING | Unique trip identifier | Generated |
| `taxi_type` | STRING | yellow or green | stg_* |
| `pickup_datetime` | TIMESTAMP | Pick-up time | stg_* |
| `dropoff_datetime` | TIMESTAMP | Drop-off time | stg_* |
| `trip_duration_minutes` | FLOAT | Trip duration | Calculated |
| `trip_distance` | FLOAT | Trip distance | stg_* |
| `passenger_count` | INTEGER | Passengers | stg_* |
| `pickup_zone` | STRING | Pick-up zone name | Joined from stg_taxi_zones |
| `pickup_borough` | STRING | Pick-up borough | Joined from stg_taxi_zones |
| `dropoff_zone` | STRING | Drop-off zone name | Joined from stg_taxi_zones |
| `dropoff_borough` | STRING | Drop-off borough | Joined from stg_taxi_zones |
| `fare_amount` | FLOAT | Base fare | stg_* |
| `total_amount` | FLOAT | Total charge | stg_* |
| `tip_amount` | FLOAT | Tip | stg_* |
| `tip_percentage` | FLOAT | Tip % of fare | Calculated |

**Calculated Fields:**
- `trip_duration_minutes = TIMESTAMP_DIFF(dropoff_datetime, pickup_datetime, MINUTE)`
- `tip_percentage = (tip_amount / fare_amount) * 100`

### int_yellow_taxi

Enhanced yellow taxi data with additional metrics.

### int_green_taxi

Enhanced green taxi data with additional metrics.

---

## Marts Layer

### fact_trip_summary_day

Daily aggregated trip metrics by taxi type.

| Column Name | Data Type | Description | Aggregation |
|------------|-----------|-------------|-------------|
| `trip_date` | DATE | Trip date | GROUP BY |
| `taxi_type` | STRING | yellow or green | GROUP BY |
| `total_trips` | INTEGER | Total trips | COUNT(*) |
| `total_passengers` | INTEGER | Total passengers | SUM(passenger_count) |
| `total_distance` | FLOAT | Total miles | SUM(trip_distance) |
| `avg_distance` | FLOAT | Average miles | AVG(trip_distance) |
| `avg_duration_minutes` | FLOAT | Average duration | AVG(trip_duration_minutes) |
| `total_fare` | FLOAT | Total fares | SUM(fare_amount) |
| `total_tips` | FLOAT | Total tips | SUM(tip_amount) |
| `total_revenue` | FLOAT | Total revenue | SUM(total_amount) |
| `avg_fare` | FLOAT | Average fare | AVG(fare_amount) |
| `avg_tip_percentage` | FLOAT | Average tip % | AVG(tip_percentage) |

**Business Metrics:**
- Daily ridership trends
- Revenue per taxi type
- Average trip characteristics

### fact_revenue_breakdown_hourly

Hourly revenue breakdown by taxi type.

| Column Name | Data Type | Description | Aggregation |
|------------|-----------|-------------|-------------|
| `trip_datetime` | TIMESTAMP | Hour timestamp | DATE_TRUNC(pickup_datetime, HOUR) |
| `taxi_type` | STRING | yellow or green | GROUP BY |
| `hour_of_day` | INTEGER | Hour (0-23) | EXTRACT(HOUR FROM pickup_datetime) |
| `trip_count` | INTEGER | Trips in hour | COUNT(*) |
| `total_revenue` | FLOAT | Hourly revenue | SUM(total_amount) |
| `total_fares` | FLOAT | Hourly fares | SUM(fare_amount) |
| `total_tips` | FLOAT | Hourly tips | SUM(tip_amount) |
| `avg_revenue_per_trip` | FLOAT | Avg revenue | AVG(total_amount) |

**Business Metrics:**
- Peak hour identification
- Hourly revenue patterns
- Operational insights

### zone_performance_mart

Geographic zone performance metrics.

| Column Name | Data Type | Description | Aggregation |
|------------|-----------|-------------|-------------|
| `zone_id` | INTEGER | Zone identifier | GROUP BY |
| `zone_name` | STRING | Zone name | Dimension |
| `borough` | STRING | Borough | Dimension |
| `total_pickups` | INTEGER | Pickup count | COUNT(*) |
| `total_dropoffs` | INTEGER | Dropoff count | COUNT(*) |
| `avg_trip_distance_from_zone` | FLOAT | Avg outbound distance | AVG(trip_distance) |
| `total_revenue_from_zone` | FLOAT | Revenue from pickups | SUM(total_amount) |
| `top_destination_zone` | STRING | Most common destination | MODE(dropoff_zone) |

**Business Metrics:**
- High-demand zones
- Geographic revenue distribution
- Popular routes

---

## Data Quality Rules

### Validation Rules

**Trip-Level Validations:**
- `passenger_count` BETWEEN 1 AND 6
- `trip_distance` > 0
- `trip_duration_minutes` > 0 AND < 1440 (24 hours)
- `fare_amount` >= 0
- `total_amount` > 0
- `pickup_location_id` != `dropoff_location_id`

**Amount Validations:**
- `total_amount` approximately equals `fare_amount + extra + mta_tax + tip_amount + tolls_amount + surcharges`
- All amount fields >= 0

**Temporal Validations:**
- `dropoff_datetime` > `pickup_datetime`
- `pickup_datetime` <= CURRENT_TIMESTAMP

### Data Tests (dbt)

```sql
-- Example dbt test
-- tests/assert_positive_fares.sql
SELECT *
FROM {{ ref('stg_yellow_taxi') }}
WHERE fare_amount < 0
```

Common dbt tests applied:
- `unique`: Trip IDs are unique
- `not_null`: Required fields are populated
- `accepted_values`: Categorical fields have valid values
- `relationships`: Foreign keys exist in dimension tables

---

## Data Lineage

```
Source Data (CSV)
  └─> Raw BigQuery Tables
      └─> Staging Models (stg_*)
          └─> Intermediate Models (int_*)
              └─> Marts Models (fact_*, dim_*)
                  └─> BI Dashboards
```

---

## Update Frequency

- **Source Data**: Monthly (NYC TLC releases)
- **Pipeline Execution**: Weekly (Every Sunday at midnight)
- **Data Refresh**: Full refresh for staging, incremental for marts (future)

---

## Contact

For questions about the data schema:
- **GitHub Issues**: [transport_elt/issues](https://github.com/aladon090/transport_elt/issues)
- **Data Source**: [NYC TLC Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)
