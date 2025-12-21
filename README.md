# NYC Taxi Trip Data Analysis Pipeline

## Project Summary
This project builds a **scalable and reproducible ELT (Extract, Load, Transform) pipeline** to analyze NYC taxi trip data. It turns large, messy raw datasets into **clean, easy-to-use data marts** ready for analysis and visualization.

The pipeline is fully built on **Google Cloud Platform (GCP)** using modern data engineering tools:
- **GCS** (Data Lake) to store raw data
- **BigQuery** (Data Warehouse) to store and query data at scale
- **dbt** (Transformations) to clean, structure, and aggregate data
- **Apache Airflow** (Orchestration) to automate and monitor the workflow

**GitHub Repository:** [https://github.com/aladon090/transport_elt](https://github.com/aladon090/transport_elt)

---

## Why This Matters
Working with NYC taxi trip data isn't easy — the datasets are huge, messy, and constantly updated. This pipeline helps:
- **Handle large volumes of data** efficiently using chunked processing
- **Ensure data quality** with automated transformations and testing
- **Generate actionable insights** for ridership, revenue, and geography
- **Automate the workflow** so the process is reproducible and reliable

---

## Pipeline Architecture
Here's how the data flows:

1. **Extract:** Raw CSV files (Yellow Taxi, Green Taxi, and Taxi Zone data) are converted to Parquet format for efficient storage and processing
2. **Load:** Parquet files are uploaded to **GCS** (Data Lake) and loaded into **BigQuery** staging tables
3. **Transform:** **dbt** runs SQL-based transformations in BigQuery to produce clean, analytical-ready tables across three layers:
   - **Staging:** Clean and standardize raw data
   - **Intermediate:** Combine and enrich datasets
   - **Marts:** Create aggregated analytics tables
4. **Orchestration:** **Apache Airflow** schedules and monitors the workflow, ensuring all steps run smoothly every Sunday at midnight
5. **Analysis:** Transformed data is visualized using **Looker Studio (Google Data Studio)** dashboards

**Architecture Diagram:**
![ELT Pipeline Architecture](https://github.com/user-attachments/assets/c35a12a0-3143-4e50-aa94-7957f921a931)
*Note: You can replace this with your own architecture diagram*

---

## Tech Stack

### Data Infrastructure
- **Google Cloud Storage (GCS):** Data Lake for raw and processed files
- **Google BigQuery:** Cloud Data Warehouse for analytics
- **Google Cloud Platform:** Cloud infrastructure

### Data Processing
- **Python 3.11:** Core programming language
- **pandas:** Data manipulation and processing
- **PyArrow:** Efficient Parquet file handling
- **dbt (Data Build Tool):** SQL-based transformations

### Orchestration & Automation
- **Apache Airflow 2.8.1:** Workflow orchestration
- **Docker & Docker Compose:** Containerization and deployment

### Data Visualization
- **Looker Studio:** Interactive dashboards and reports

---

## Project Structure

```
transport_elt/
├── README.md                          # Project documentation
├── .gitignore                         # Git ignore patterns
├── .env.example                       # Environment variables template
├── requirements.txt                   # Python dependencies
├── Makefile                          # Common command shortcuts
│
├── config/                           # Configuration files
│   ├── credentials/                  # GCP credentials (gitignored)
│   └── dbt/                         # dbt configuration
│       ├── profiles.yml             # dbt profiles
│       └── dbt_project.yml          # dbt project config
│
├── data/                             # Local data storage (gitignored)
│   ├── raw/                         # Raw CSV files
│   ├── processed/                   # Parquet files
│   └── staging/                     # Staging data
│
├── src/                              # Python source code
│   ├── extract/                     # Data extraction module
│   │   ├── __init__.py
│   │   └── extract_parquet.py       # CSV to Parquet conversion
│   ├── load/                        # Data loading module
│   │   ├── __init__.py
│   │   └── load_to_gcp.py           # Upload to GCS and BigQuery
│   └── utils/                       # Utility modules
│       ├── __init__.py
│       ├── config.py                # Centralized configuration
│       └── logger.py                # Logging setup
│
├── dbt/                              # dbt transformations
│   ├── models/
│   │   ├── staging/                 # Staging models (clean raw data)
│   │   ├── intermediate/            # Intermediate models (combine data)
│   │   └── marts/                   # Data marts (analytics tables)
│   ├── macros/                      # dbt macros
│   ├── tests/                       # dbt tests
│   └── analyses/                    # Ad-hoc analyses
│
├── orchestration/                    # Apache Airflow
│   ├── dags/                        # Airflow DAGs
│   │   └── transport_elt_pipeline.py
│   ├── plugins/                     # Airflow plugins
│   ├── docker-compose.yml           # Airflow Docker setup
│   └── requirements.txt             # Airflow dependencies
│
├── tests/                            # Unit and integration tests
│   ├── __init__.py
│   ├── test_extract.py
│   └── test_load.py
│
└── docs/                             # Documentation
    ├── architecture.md              # Architecture details
    ├── setup.md                     # Setup guide
    └── data_dictionary.md           # Data schema documentation
```

---

## Key Insights from the Data
Once the pipeline is running, you can uncover insights like:
- **Ridership:** Yellow taxis make up ~67% of trips, green taxis ~33%
- **Revenue:** Total fares exceed $100 million, covering over 11 million passengers
- **Geography:** Manhattan dominates trip origins (~87%)
- **Trip Patterns:** Analyze trends in trip distances, passenger counts, and fare/tip amounts
- **Hourly Revenue:** Track revenue breakdown by hour and taxi type
- **Zone Performance:** Identify top-performing pickup and dropoff zones

**Dashboard Example:**
![Dashboard Example](https://github.com/user-attachments/assets/40aca608-a63e-4b77-83ca-5935c1cc166f)
*Note: You can replace this with your own dashboard screenshot*

---

## Getting Started

### Prerequisites
- **GCP Account** with BigQuery and Storage API enabled
- **Docker** and **Docker Compose** installed
- **Python 3.11** or higher (for local development)
- **Git** for version control

### Step 1: Clone the Repository
```bash
git clone https://github.com/aladon090/transport_elt.git
cd transport_elt
```

### Step 2: Configure Environment Variables
```bash
# Copy the environment template
cp .env.example .env

# Edit .env with your GCP project details
nano .env
```

Update these variables in your `.env` file:
- `GCP_PROJECT_ID`: Your GCP project ID
- `GCS_BUCKET`: Your GCS bucket name
- `BQ_DATASET`: Your BigQuery dataset name
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to your GCP service account key

### Step 3: Set Up GCP Credentials
1. Create a GCP service account with the following roles:
   - BigQuery Admin
   - Storage Admin
2. Download the service account JSON key
3. Save it to `config/credentials/taxi-transport-analytics-fbfa6653d305.json`

### Step 4: Install Dependencies (Local Development)
```bash
# Install Python dependencies
make setup
# OR manually:
pip install -r requirements.txt
```

### Step 5: Prepare Your Data
Place your raw CSV files in one of these locations:
- `data/raw/` (new structure)
- `dbt/raw_data/` (legacy compatibility)

Required files:
- `yellow_tripdata_2019-12.csv`
- `green_tripdata_2019-12.csv`
- `taxi_zone_lookup (1).csv`

### Step 6: Start Apache Airflow
```bash
# Navigate to orchestration directory
cd orchestration

# Create required directories and set permissions
mkdir -p ./logs ./plugins ./config
echo -e "AIRFLOW_UID=$(id -u)" > .env

# Initialize and start Airflow
make airflow-up
# OR manually:
docker-compose up airflow-init
docker-compose up -d
```

### Step 7: Access Airflow UI
1. Open your browser and navigate to: http://localhost:8080
2. Login with default credentials:
   - **Username:** `airflow`
   - **Password:** `airflow`
3. Enable the `transport_elt_pipeline` DAG
4. The DAG will run automatically every Sunday at midnight, or you can trigger it manually

### Step 8: Monitor the Pipeline
- View task logs in the Airflow UI
- Check BigQuery for transformed tables
- Verify data quality with dbt tests

---

## Usage

### Running Individual Components

**Extract Data (CSV to Parquet):**
```bash
make extract
# OR
python -m src.extract.extract_parquet
```

**Load Data to GCP:**
```bash
make load
# OR
python -m src.load.load_to_gcp
```

**Run dbt Transformations:**
```bash
make dbt-run
# OR
cd dbt
dbt run --profiles-dir ../config/dbt
```

**Run dbt Tests:**
```bash
dbt test --profiles-dir ../config/dbt
```

### Airflow Commands

**Start Airflow:**
```bash
cd orchestration
docker-compose up -d
```

**Stop Airflow:**
```bash
cd orchestration
docker-compose down
```

**View Airflow Logs:**
```bash
docker-compose logs airflow-scheduler
docker-compose logs airflow-webserver
```

**Trigger DAG Manually:**
```bash
docker-compose exec airflow-webserver airflow dags trigger transport_elt_pipeline
```

---

## Pipeline Schedule

The ELT pipeline runs automatically **every Sunday at midnight (00:00 UTC)** via Apache Airflow.

**Cron Expression:** `0 0 * * 0`

To modify the schedule, edit the `schedule_interval` in `orchestration/dags/transport_elt_pipeline.py`.

---

## Data Models

### Staging Layer
- `stg_yellow_taxi`: Cleaned yellow taxi trip data
- `stg_green_taxi`: Cleaned green taxi trip data
- `stg_taxi_zones`: Taxi zone lookup data

### Intermediate Layer
- `int_all_trips`: Combined yellow and green taxi trips
- `int_yellow_taxi`: Enhanced yellow taxi data
- `int_green_taxi`: Enhanced green taxi data

### Marts Layer
- `fact_trip_summary_day`: Daily trip summaries by taxi type
- `fact_revenue_breakdown_hourly`: Hourly revenue breakdown
- `zone_performance_mart`: Geographic zone performance metrics

For detailed schema information, see [docs/data_dictionary.md](docs/data_dictionary.md).

---

## Testing

Run unit tests:
```bash
make test
# OR
pytest tests/
```

Run dbt tests:
```bash
cd dbt
dbt test --profiles-dir ../config/dbt
```

---

## Troubleshooting

### Common Issues

**1. Airflow DAG not appearing:**
- Check DAG syntax: `docker-compose exec airflow-webserver airflow dags list-import-errors`
- Verify file is in `orchestration/dags/`
- Check scheduler logs: `docker-compose logs airflow-scheduler`

**2. GCP Authentication errors:**
- Verify credentials file exists: `config/credentials/taxi-transport-analytics-fbfa6653d305.json`
- Check environment variable: `GOOGLE_APPLICATION_CREDENTIALS`
- Ensure service account has required permissions

**3. dbt model failures:**
- Check dbt logs: `dbt run --profiles-dir ../config/dbt --debug`
- Verify BigQuery dataset exists
- Ensure raw data is loaded

**4. Import errors in Airflow:**
- Verify project root is mounted: `..:/workspaces/transport_elt`
- Check Python path in DAG file
- Ensure all `__init__.py` files exist

