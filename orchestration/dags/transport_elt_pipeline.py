"""
Transport ELT Pipeline DAG
Runs every Sunday to extract, load, and transform taxi data
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
import sys
import os

# Add project root to Python path
PROJECT_ROOT = '/workspaces/transport_elt'
sys.path.insert(0, PROJECT_ROOT)

# Import from new src structure
from src.extract.extract_parquet import run_extraction
from src.load.load_to_gcp import run_load

# Default arguments for the DAG
default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2025, 1, 1),
}

# Define the DAG
dag = DAG(
    'transport_elt_pipeline',
    default_args=default_args,
    description='Weekly ELT pipeline for NYC taxi data',
    schedule_interval='0 0 * * 0',  # Run at midnight every Sunday (cron format)
    catchup=False,
    tags=['elt', 'taxi', 'weekly'],
)


def extract_to_parquet():
    """Extract CSV files and convert to Parquet format using src module"""
    # Use backward compatible paths
    raw_data_dir = f"{PROJECT_ROOT}/dbt/raw_data"
    output_dir = f"{PROJECT_ROOT}/raw_parquet"

    run_extraction(
        base_path=PROJECT_ROOT,
        raw_data_dir=raw_data_dir,
        output_dir=output_dir
    )


def load_to_gcp():
    """Load Parquet files to GCS and BigQuery using src module"""
    credentials_path = f"{PROJECT_ROOT}/config/credentials/taxi-transport-analytics-fbfa6653d305.json"
    data_dir = f"{PROJECT_ROOT}/raw_parquet"

    run_load(
        base_path=PROJECT_ROOT,
        credentials_path=credentials_path,
        data_dir=data_dir
    )


# Task 1: Extract CSV to Parquet
extract_task = PythonOperator(
    task_id='extract_csv_to_parquet',
    python_callable=extract_to_parquet,
    dag=dag,
)

# Task 2: Load to GCS and BigQuery
load_task = PythonOperator(
    task_id='load_to_gcp',
    python_callable=load_to_gcp,
    dag=dag,
)

# Task 3: Run dbt models (staging layer)
dbt_staging = BashOperator(
    task_id='dbt_run_staging',
    bash_command=f'cd {PROJECT_ROOT} && dbt run --models staging --profiles-dir {PROJECT_ROOT}/config/dbt --project-dir {PROJECT_ROOT}/dbt',
    dag=dag,
)

# Task 4: Run dbt models (intermediate layer)
dbt_intermediate = BashOperator(
    task_id='dbt_run_intermediate',
    bash_command=f'cd {PROJECT_ROOT} && dbt run --models intermediate --profiles-dir {PROJECT_ROOT}/config/dbt --project-dir {PROJECT_ROOT}/dbt',
    dag=dag,
)

# Task 5: Run dbt models (marts layer)
dbt_marts = BashOperator(
    task_id='dbt_run_marts',
    bash_command=f'cd {PROJECT_ROOT} && dbt run --models marts --profiles-dir {PROJECT_ROOT}/config/dbt --project-dir {PROJECT_ROOT}/dbt',
    dag=dag,
)

# Task 6: Run dbt tests
dbt_test = BashOperator(
    task_id='dbt_test',
    bash_command=f'cd {PROJECT_ROOT} && dbt test --profiles-dir {PROJECT_ROOT}/config/dbt --project-dir {PROJECT_ROOT}/dbt',
    dag=dag,
)

# Define task dependencies (pipeline flow)
extract_task >> load_task >> dbt_staging >> dbt_intermediate >> dbt_marts >> dbt_test
