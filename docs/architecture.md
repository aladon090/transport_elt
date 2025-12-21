# Transport ELT Pipeline - Architecture Documentation

## Overview

The Transport ELT (Extract, Load, Transform) pipeline is a scalable data engineering solution designed to process NYC taxi trip data. The architecture follows modern data engineering best practices with clear separation of concerns and modular design.

## System Architecture

### High-Level Architecture

```
┌─────────────────┐
│   Raw CSV Data  │
│  (NYC Taxi TLC) │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│                   EXTRACT LAYER                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Python (pandas + PyArrow)                       │  │
│  │  • CSV to Parquet conversion                     │  │
│  │  • Chunked processing (100k rows)                │  │
│  │  • Snappy compression                             │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│                    LOAD LAYER                            │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Google Cloud Storage (Data Lake)                 │  │
│  │  • Stores Parquet files                          │  │
│  │  • Centralized raw data repository               │  │
│  └──────────────────┬───────────────────────────────┘  │
│                     │                                    │
│  ┌──────────────────▼───────────────────────────────┐  │
│  │  Google BigQuery (Data Warehouse)                 │  │
│  │  • Raw staging tables                            │  │
│  │  • Columnar storage                               │  │
│  │  • SQL-based querying                            │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│                TRANSFORM LAYER (dbt)                     │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Staging Models                                   │  │
│  │  • stg_yellow_taxi                               │  │
│  │  • stg_green_taxi                                │  │
│  │  • stg_taxi_zones                                │  │
│  │  (Clean & standardize raw data)                  │  │
│  └──────────────────┬───────────────────────────────┘  │
│                     │                                    │
│  ┌──────────────────▼───────────────────────────────┐  │
│  │  Intermediate Models                              │  │
│  │  • int_all_trips                                 │  │
│  │  • int_yellow_taxi                               │  │
│  │  • int_green_taxi                                │  │
│  │  (Join & enrich datasets)                        │  │
│  └──────────────────┬───────────────────────────────┘  │
│                     │                                    │
│  ┌──────────────────▼───────────────────────────────┐  │
│  │  Marts (Analytics-Ready Tables)                   │  │
│  │  • fact_trip_summary_day                         │  │
│  │  • fact_revenue_breakdown_hourly                 │  │
│  │  • zone_performance_mart                         │  │
│  │  (Aggregated business metrics)                   │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│              VISUALIZATION LAYER                         │
│  • Looker Studio Dashboards                             │
│  • Business Intelligence Reports                        │
│  • Real-time Analytics                                  │
└─────────────────────────────────────────────────────────┘

         ┌─────────────────────────────────────┐
         │   ORCHESTRATION (Apache Airflow)    │
         │  • Workflow scheduling (Every Sunday)│
         │  • Task dependency management        │
         │  • Error handling & retry logic     │
         │  • Monitoring & logging              │
         └─────────────────────────────────────┘
```

## Technology Stack

### Data Storage & Processing
- **Google Cloud Storage (GCS)**: Object storage for raw and processed data files
- **Google BigQuery**: Cloud data warehouse for analytics
- **Parquet Format**: Columnar storage format for efficient data compression and querying

### Data Transformation
- **dbt (Data Build Tool)**: SQL-based data transformation framework
  - Version control for data models
  - Automated testing and documentation
  - Incremental model building

### Orchestration & Automation
- **Apache Airflow**: Workflow orchestration platform
  - DAG-based task scheduling
  - Retry logic and error handling
  - Web-based monitoring UI

### Application Layer
- **Python 3.11**: Core programming language
- **pandas**: Data manipulation and analysis
- **PyArrow**: High-performance Parquet file handling
- **Docker**: Containerization for consistent deployment

## Data Flow

### 1. Extract Phase
```python
Raw CSV Files
  └─> Chunked Reading (100k rows)
      └─> Pandas DataFrames
          └─> PyArrow Tables
              └─> Parquet Files (Snappy compressed)
```

**Key Features:**
- Memory-efficient chunked processing
- Schema inference from first chunk
- Snappy compression for optimal storage/performance balance

### 2. Load Phase
```python
Parquet Files
  └─> Upload to GCS (Data Lake)
      └─> Load to BigQuery (Raw Tables)
          - WRITE_TRUNCATE mode (full refresh)
          - Auto-schema detection
```

**Key Features:**
- Idempotent loading (safe to re-run)
- Automatic schema detection
- Separate raw and transformed layers

### 3. Transform Phase (dbt)
```sql
Staging Layer (stg_*)
  └─> Clean column names
  └─> Cast data types
  └─> Filter invalid records
      ↓
Intermediate Layer (int_*)
  └─> Combine datasets
  └─> Add calculated fields
  └─> Enrich with dimensional data
      ↓
Marts Layer (fact_*, dim_*)
  └─> Business-level aggregations
  └─> Daily/hourly summaries
  └─> Analytics-ready tables
```

**Key Features:**
- Incremental materialization support
- Built-in data quality tests
- Self-documenting models

## Project Structure

```
transport_elt/
├── src/                    # Python source code
│   ├── extract/           # Data extraction logic
│   ├── load/              # Data loading to GCP
│   └── utils/             # Shared utilities (config, logging)
│
├── dbt/                   # dbt transformation models
│   ├── models/
│   │   ├── staging/      # Raw data cleaning
│   │   ├── intermediate/ # Data enrichment
│   │   └── marts/        # Business metrics
│   └── tests/            # Data quality tests
│
├── orchestration/         # Airflow DAGs
│   └── dags/             # Pipeline definitions
│
├── config/               # Configuration files
│   ├── credentials/      # GCP service accounts
│   └── dbt/             # dbt profiles
│
├── data/                 # Local data storage
│   ├── raw/             # Raw CSV files
│   ├── processed/       # Parquet files
│   └── staging/         # Temporary data
│
└── tests/               # Unit & integration tests
```

## Scalability Considerations

### Current Architecture
- **Data Volume**: ~11M trips/month
- **File Size**: 100-500 MB per file
- **Processing Time**: ~5-10 minutes end-to-end
- **Schedule**: Weekly on Sundays

### Scaling Strategies

**Horizontal Scaling:**
- Partition data by date/region
- Parallel processing of multiple files
- Distributed dbt model execution

**Vertical Scaling:**
- Increase chunk size for larger files
- Optimize BigQuery table partitioning
- Enable BigQuery clustering on key columns

**Performance Optimization:**
- Incremental dbt models for large tables
- BigQuery result caching
- Parquet file columnar pruning

## Security & Compliance

### Data Security
- GCP Service Account with least-privilege access
- Credentials stored in `config/credentials/` (gitignored)
- Environment-based configuration (`.env` files)
- No hardcoded secrets in code

### Access Control
- BigQuery dataset-level permissions
- GCS bucket IAM policies
- Airflow RBAC for workflow management

## Monitoring & Observability

### Logging
- Python logging framework with structured logs
- Airflow task logs (per execution)
- dbt run logs with model statistics

### Monitoring
- Airflow UI for DAG execution status
- BigQuery execution statistics
- dbt test results for data quality

### Alerting (Future Enhancement)
- Email notifications on Airflow failures
- Slack integration for critical errors
- Data quality threshold monitoring

## Future Enhancements

1. **Incremental Loading**: Switch from full refresh to incremental loads
2. **Data Quality**: Integrate Great Expectations for advanced testing
3. **Real-time Processing**: Add streaming pipeline for real-time data
4. **CI/CD**: Automated testing and deployment pipeline
5. **Cost Optimization**: Implement data lifecycle policies and archival strategies
6. **Multi-environment**: Separate dev/staging/prod environments

## References

- [dbt Documentation](https://docs.getdbt.com/)
- [Apache Airflow Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
- [BigQuery Best Practices](https://cloud.google.com/bigquery/docs/best-practices)
- [NYC TLC Trip Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)
