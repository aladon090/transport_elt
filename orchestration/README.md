# Transport ELT Airflow Pipeline

This directory contains Apache Airflow configuration to schedule and orchestrate the transport ELT pipeline.

## Pipeline Overview

The pipeline runs **every Sunday at midnight** and performs the following tasks:

1. **Extract**: Converts CSV files to Parquet format (uses [../extract/extractParquet.py](../extract/extractParquet.py))
2. **Load**: Uploads Parquet files to Google Cloud Storage and loads them into BigQuery (uses [../load/load_to_gcp.py](../load/load_to_gcp.py))
3. **Transform**: Runs dbt models in the following order:
   - Staging layer
   - Intermediate layer
   - Marts layer
4. **Test**: Runs dbt tests to validate data quality

## Schedule

- **Cron Expression**: `0 0 * * 0`
- **Frequency**: Weekly, every Sunday at 00:00 (midnight)
- **Timezone**: UTC (can be configured in the DAG)

## Tech Stack

- **Apache Airflow**: 2.8.1
- **Python**: 3.11
- **Database**: PostgreSQL 13
- **Executor**: LocalExecutor

## Prerequisites

- Docker and Docker Compose installed
- Google Cloud credentials file: `taxi-transport-analytics-fbfa6653d305.json` in the project root
- Raw CSV data files in `/dbt/raw_data/` directory

## Setup Instructions

### 1. Navigate to Airflow Directory

```bash
cd airflow
```

### 2. Create Required Directories

```bash
mkdir -p ./logs ./plugins ./config
```

### 3. Set the Airflow UID

**For Linux/Mac:**

```bash
echo -e "AIRFLOW_UID=$(id -u)" > .env
```

**For Windows:**

Create a `.env` file with:

```
AIRFLOW_UID=50000
```

### 4. Start Airflow

Initialize the database and start services:

```bash
docker-compose up airflow-init
docker-compose up -d
```

Wait a few moments for all services to start.

### 5. Access Airflow UI

- **URL**: http://localhost:8080
- **Username**: `airflow`
- **Password**: `airflow`

### 6. Enable the DAG

1. Log into the Airflow UI
2. Find the DAG named `transport_elt_pipeline`
3. Toggle the switch to enable it
4. The DAG will run automatically every Sunday at midnight

## Manual Execution

To trigger the pipeline manually:

**Option 1: Using the UI**
1. Go to the Airflow UI
2. Click on the `transport_elt_pipeline` DAG
3. Click the "Play" button (Trigger DAG)
4. Confirm the execution

**Option 2: Using the CLI**

```bash
docker-compose exec airflow-webserver airflow dags trigger transport_elt_pipeline
```

## DAG Structure

```
extract_csv_to_parquet
        ↓
   load_to_gcp
        ↓
  dbt_run_staging
        ↓
dbt_run_intermediate
        ↓
  dbt_run_marts
        ↓
    dbt_test
```

## Task Descriptions

### `extract_csv_to_parquet`
- Calls `run_extraction()` from [../extract/extractParquet.py](../extract/extractParquet.py)
- Reads CSV files from `/dbt/raw_data/`
- Converts them to Parquet format in chunks
- Saves to `/raw_parquet/` directory

### `load_to_gcp`
- Calls `run_load()` from [../load/load_to_gcp.py](../load/load_to_gcp.py)
- Uploads Parquet files to Google Cloud Storage bucket
- Loads data into BigQuery raw tables

### `dbt_run_staging`
- Runs dbt staging models
- Creates views for initial data cleaning

### `dbt_run_intermediate`
- Runs dbt intermediate models
- Combines and transforms data

### `dbt_run_marts`
- Runs dbt mart models
- Creates final analytical tables

### `dbt_test`
- Runs all dbt tests
- Validates data quality and constraints

## Configuration

### Modify Schedule

To change the schedule, edit the `schedule_interval` in [dags/transport_elt_pipeline.py](dags/transport_elt_pipeline.py):

```python
schedule_interval='0 0 * * 0',  # Current: Every Sunday at midnight
```

Common cron patterns:
- Daily: `'0 0 * * *'`
- Weekly (Monday): `'0 0 * * 1'`
- Monthly: `'0 0 1 * *'`
- Every 6 hours: `'0 */6 * * *'`

### Update GCP Credentials

If you need to use different GCP credentials:

1. Update the credentials path in the DAG file
2. Update the volume mount in `docker-compose.yml`
3. Restart Airflow services

## Monitoring

### View Logs

Check logs for specific tasks:

```bash
docker-compose logs airflow-scheduler
docker-compose logs airflow-webserver
```

Or view task logs in the Airflow UI:
1. Click on the DAG
2. Click on a task
3. Click "Log" button

### Check DAG Status

```bash
docker-compose exec airflow-webserver airflow dags list
docker-compose exec airflow-webserver airflow dags state transport_elt_pipeline
```

## Troubleshooting

### DAG Not Showing Up

1. Check DAG file syntax:
   ```bash
   docker-compose exec airflow-webserver airflow dags list-import-errors
   ```

2. Verify file is in the correct location: `airflow/dags/`

3. Check scheduler logs:
   ```bash
   docker-compose logs airflow-scheduler
   ```

### Tasks Failing

1. View task logs in the Airflow UI
2. Check that all file paths are correct
3. Verify GCP credentials are properly mounted
4. Ensure all dependencies are installed

### Module Import Errors

If you see errors about missing modules, the DAG is configured to add the project paths to Python's sys.path:
- `/workspaces/transport_elt`
- `/workspaces/transport_elt/extract`
- `/workspaces/transport_elt/load`

### Reset Airflow

To completely reset Airflow:

```bash
docker-compose down -v
rm -rf logs/*
docker-compose up airflow-init
docker-compose up -d
```

## Stopping Airflow

To stop all services:

```bash
docker-compose down
```

To stop and remove all data:

```bash
docker-compose down -v
```

## Using Your Existing Scripts

The DAG now uses your existing Python scripts:
- **Extract**: Imports and calls `run_extraction()` from [extractParquet.py](../extract/extractParquet.py)
- **Load**: Imports and calls `run_load()` from [load_to_gcp.py](../load/load_to_gcp.py)

You can continue to run these scripts standalone or modify them as needed. The changes made are backward compatible:
- Both scripts still work when run directly
- New `run_*()` functions accept `base_path` parameter for Airflow integration

## Additional Resources

- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [Airflow DAG Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
- [dbt Documentation](https://docs.getdbt.com/)
