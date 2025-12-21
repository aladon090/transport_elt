# Transport ELT Pipeline - Setup Guide

This comprehensive guide will walk you through setting up the Transport ELT pipeline from scratch.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Google Cloud Platform Setup](#google-cloud-platform-setup)
4. [Local Development Setup](#local-development-setup)
5. [Apache Airflow Setup](#apache-airflow-setup)
6. [dbt Setup](#dbt-setup)
7. [Running the Pipeline](#running-the-pipeline)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- **Git**: Version control
- **Python 3.11+**: Core runtime
- **Docker Desktop**: For Airflow containerization
- **Make**: Build automation (optional but recommended)

### Required Accounts
- **Google Cloud Platform (GCP)** account with billing enabled
- **GitHub** account (for version control)

### System Requirements
- **OS**: Linux, macOS, or Windows with WSL2
- **RAM**: Minimum 8GB (16GB recommended)
- **Disk Space**: 10GB free space
- **CPU**: 2+ cores recommended

---

## Initial Setup

### 1. Clone the Repository

```bash
git clone https://github.com/aladon090/transport_elt.git
cd transport_elt
```

### 2. Create Python Virtual Environment

```bash
# Create virtual environment
python3.11 -m venv .venv

# Activate virtual environment
# On Linux/Mac:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Using Make (recommended)
make setup

# Or manually
pip install -r requirements.txt
```

---

## Google Cloud Platform Setup

### 1. Create a GCP Project

```bash
# Set your project ID
export PROJECT_ID="taxi-transport-analytics"

# Create project (via gcloud CLI)
gcloud projects create $PROJECT_ID
gcloud config set project $PROJECT_ID
```

### 2. Enable Required APIs

```bash
gcloud services enable bigquery.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable iam.googleapis.com
```

### 3. Create GCS Bucket

```bash
# Set bucket name
export GCS_BUCKET="transport-analytics"

# Create bucket
gsutil mb -p $PROJECT_ID gs://$GCS_BUCKET
```

### 4. Create BigQuery Dataset

```bash
# Create dataset
bq mk --dataset \
  --location=US \
  $PROJECT_ID:new_york_analytic
```

### 5. Create Service Account

```bash
# Create service account
gcloud iam service-accounts create airflow-sa \
  --display-name="Airflow Service Account"

# Get service account email
SA_EMAIL="airflow-sa@${PROJECT_ID}.iam.gserviceaccount.com"

# Grant necessary roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/bigquery.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/storage.admin"

# Create and download key
gcloud iam service-accounts keys create \
  config/credentials/taxi-transport-analytics.json \
  --iam-account=$SA_EMAIL
```

### 6. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file
nano .env
```

Update the following variables in `.env`:
```bash
GCP_PROJECT_ID=taxi-transport-analytics
GCS_BUCKET=transport-analytics
BQ_DATASET=new_york_analytic
GOOGLE_APPLICATION_CREDENTIALS=config/credentials/taxi-transport-analytics.json
```

---

## Local Development Setup

### 1. Prepare Data Files

Download NYC TLC Trip Record Data:

```bash
# Create data directory
mkdir -p data/raw

# Download sample data (December 2019)
# Yellow Taxi
wget -P data/raw \
  https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2019-12.parquet

# Green Taxi
wget -P data/raw \
  https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2019-12.parquet

# Taxi Zones
wget -P data/raw \
  https://d37ci6vzurychx.cloudfront.net/misc/taxi+_zone_lookup.csv
```

**Note**: The pipeline also supports legacy CSV format. Place CSV files in `dbt/raw_data/` for backward compatibility.

### 2. Test Extract Module

```bash
# Run extraction
make extract

# Or manually
python -m src.extract.extract_parquet

# Verify output
ls -lh data/processed/
```

### 3. Test Load Module

```bash
# Set GCP credentials
export GOOGLE_APPLICATION_CREDENTIALS=config/credentials/taxi-transport-analytics.json

# Run load
make load

# Or manually
python -m src.load.load_to_gcp

# Verify in BigQuery
bq ls new_york_analytic
```

---

## Apache Airflow Setup

### 1. Navigate to Orchestration Directory

```bash
cd orchestration
```

### 2. Create Required Directories

```bash
mkdir -p ./logs ./plugins ./config
```

### 3. Set Airflow UID

```bash
# On Linux/Mac
echo -e "AIRFLOW_UID=$(id -u)" > .env

# On Windows, create .env with:
echo "AIRFLOW_UID=50000" > .env
```

### 4. Initialize Airflow Database

```bash
docker-compose up airflow-init
```

Expected output:
```
airflow-init_1  | Database migrating done!
airflow-init_1  | User "airflow" created with role "Admin"
airflow-init_1  | 2.8.1
airflow-init_1 exited with code 0
```

### 5. Start Airflow Services

```bash
# Start in detached mode
docker-compose up -d

# Or use Make command
make airflow-up
```

### 6. Verify Airflow is Running

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs airflow-webserver
```

### 7. Access Airflow UI

1. Open browser: http://localhost:8080
2. Login credentials:
   - **Username**: `airflow`
   - **Password**: `airflow`

### 8. Enable the DAG

1. Navigate to DAGs page
2. Find `transport_elt_pipeline`
3. Toggle the switch to **ON**

---

## dbt Setup

### 1. Configure dbt Profile

The dbt profile is already configured in `config/dbt/profiles.yml`. Verify the settings:

```yaml
default:
  target: dev
  outputs:
    dev:
      type: bigquery
      method: service-account
      project: taxi-transport-analytics
      dataset: new_york_analytic
      keyfile: ../../config/credentials/taxi-transport-analytics.json
      threads: 4
      timeout_seconds: 300
```

### 2. Test dbt Connection

```bash
# Navigate to dbt directory
cd dbt

# Test connection
dbt debug --profiles-dir ../config/dbt

# Expected output:
# All checks passed!
```

### 3. Install dbt Packages (if any)

```bash
dbt deps --profiles-dir ../config/dbt
```

### 4. Run dbt Models

```bash
# Run all models
make dbt-run

# Or manually
cd dbt
dbt run --profiles-dir ../config/dbt

# Run specific layer
dbt run --models staging --profiles-dir ../config/dbt
```

### 5. Run dbt Tests

```bash
make dbt-test

# Or manually
cd dbt
dbt test --profiles-dir ../config/dbt
```

---

## Running the Pipeline

### Option 1: Using Airflow (Recommended)

1. Ensure Airflow is running
2. Navigate to http://localhost:8080
3. Trigger the DAG:
   - Click on `transport_elt_pipeline`
   - Click the **Play** button
   - Confirm trigger

4. Monitor execution:
   - View Graph View for task dependencies
   - Click on tasks to view logs
   - Check task duration and status

### Option 2: Manual Execution

```bash
# Run complete pipeline manually
make extract
make load
make dbt-run
make dbt-test
```

### Option 3: Individual Components

```bash
# Extract only
python -m src.extract.extract_parquet

# Load only
python -m src.load.load_to_gcp

# dbt transformations only
cd dbt && dbt run --profiles-dir ../config/dbt
```

---

## Troubleshooting

### Common Issues

#### 1. Import Errors in Airflow

**Error**: `ModuleNotFoundError: No module named 'src'`

**Solution**:
```python
# Verify in DAG file:
sys.path.insert(0, '/workspaces/transport_elt')
```

#### 2. GCP Authentication Errors

**Error**: `DefaultCredentialsError: Could not automatically determine credentials`

**Solution**:
```bash
# Verify credentials file exists
ls -la config/credentials/

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS=config/credentials/taxi-transport-analytics.json

# Test authentication
gcloud auth application-default login
```

#### 3. BigQuery Permission Errors

**Error**: `403 Forbidden: Access Denied`

**Solution**:
```bash
# Verify service account has correct roles
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:airflow-sa@*"

# Grant missing permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/bigquery.admin"
```

#### 4. Docker Memory Issues

**Error**: `Airflow containers keep restarting`

**Solution**:
- Increase Docker Desktop memory to 8GB+
- Settings → Resources → Memory
- Restart Docker

#### 5. dbt Connection Errors

**Error**: `Could not connect to BigQuery`

**Solution**:
```bash
# Verify dbt profile
cat config/dbt/profiles.yml

# Test connection
dbt debug --profiles-dir config/dbt

# Check service account permissions
bq ls --project_id=$PROJECT_ID
```

### Getting Help

If you encounter issues not covered here:

1. Check Airflow logs:
   ```bash
   docker-compose logs airflow-scheduler
   docker-compose logs airflow-webserver
   ```

2. Check dbt logs:
   ```bash
   cat dbt/logs/dbt.log
   ```

3. Enable debug mode:
   ```bash
   dbt run --profiles-dir config/dbt --debug
   ```

4. Open an issue:
   - GitHub: https://github.com/aladon090/transport_elt/issues

---

## Next Steps

After successful setup:

1. **Customize the Schedule**: Edit `orchestration/dags/transport_elt_pipeline.py`
2. **Add More Data**: Extend to include additional months/years
3. **Create Dashboards**: Connect Looker Studio to BigQuery
4. **Add Tests**: Expand unit tests in `tests/`
5. **Optimize Performance**: Implement incremental dbt models

## Additional Resources

- [dbt Best Practices](https://docs.getdbt.com/docs/guides/best-practices)
- [Airflow Production Deployment](https://airflow.apache.org/docs/apache-airflow/stable/production-deployment.html)
- [BigQuery Performance Guide](https://cloud.google.com/bigquery/docs/best-practices-performance-overview)
