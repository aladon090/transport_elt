"""
Load module for uploading data to Google Cloud Platform (GCS and BigQuery)
"""
import os
from pathlib import Path
from typing import Optional
from google.cloud import storage, bigquery

from ..utils.config import Config
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


def upload_to_gcs(local_path: str, gcs_path: str, bucket_name: str = None) -> None:
    """
    Upload a file to Google Cloud Storage

    Args:
        local_path: Local file path
        gcs_path: Destination path in GCS
        bucket_name: GCS bucket name (defaults to Config.GCS_BUCKET)
    """
    bucket_name = bucket_name or Config.GCS_BUCKET

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(gcs_path)
    blob.upload_from_filename(local_path)

    logger.info(f"Uploaded {local_path} to gs://{bucket_name}/{gcs_path}")


def upload_folder(folder_path: str, prefix: str, bucket_name: str = None) -> None:
    """
    Upload all parquet files from a folder to GCS

    Args:
        folder_path: Local folder path
        prefix: GCS path prefix
        bucket_name: GCS bucket name (defaults to Config.GCS_BUCKET)
    """
    folder_path = Path(folder_path)

    for file in folder_path.iterdir():
        if file.suffix in ['.csv', '.parquet'] or file.name.endswith('.csv.gz'):
            local_file = str(file)
            gcs_file = f"{prefix}/{file.name}"
            upload_to_gcs(local_file, gcs_file, bucket_name)


def load_to_bq(
    gcs_path: str,
    table_name: str,
    source_format: str = "PARQUET",
    project_id: str = None,
    dataset: str = None,
    bucket_name: str = None
) -> None:
    """
    Load data from GCS to BigQuery

    Args:
        gcs_path: Path to file in GCS (without gs://bucket prefix)
        table_name: Target BigQuery table name
        source_format: Source file format (PARQUET or CSV)
        project_id: GCP project ID (defaults to Config.PROJECT_ID)
        dataset: BigQuery dataset name (defaults to Config.BQ_DATASET)
        bucket_name: GCS bucket name (defaults to Config.GCS_BUCKET)
    """
    project_id = project_id or Config.PROJECT_ID
    dataset = dataset or Config.BQ_DATASET
    bucket_name = bucket_name or Config.GCS_BUCKET

    client = bigquery.Client(project=project_id)
    dataset_ref = client.dataset(dataset)
    table_ref = dataset_ref.table(table_name)

    if source_format == "CSV":
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,
            autodetect=True,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        )
    else:  # PARQUET
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.PARQUET,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        )

    uri = f"gs://{bucket_name}/{gcs_path}"
    load_job = client.load_table_from_uri(uri, table_ref, job_config=job_config)
    load_job.result()

    logger.info(f"Loaded {gcs_path} into {dataset}.{table_name}")


def run_load(
    base_path: str = None,
    credentials_path: str = None,
    data_dir: str = None
) -> None:
    """
    Main function to run the load process

    Args:
        base_path: Base project path (defaults to Config.PROJECT_ROOT)
        credentials_path: Path to GCP credentials file
        data_dir: Directory containing parquet files to upload
    """
    logger.info("Starting data load process")

    # Set credentials
    Config.set_gcp_credentials(credentials_path)

    # Set data directory
    if not data_dir:
        data_dir = Config.PROCESSED_DATA_DIR
    else:
        data_dir = Path(data_dir)

    # Upload parquet files to GCS
    logger.info("Uploading files to Google Cloud Storage...")

    for file in data_dir.iterdir():
        if file.suffix == ".parquet":
            local_file = str(file)
            gcs_file = f"raw_data/{file.name}"
            upload_to_gcs(local_file, gcs_file)

    # Load to BigQuery
    logger.info("\nLoading data to BigQuery...")
    load_to_bq("raw_data/yellow_taxi.parquet", "raw_yellow_taxi", "PARQUET")
    load_to_bq("raw_data/green_taxi.parquet", "raw_green_taxi", "PARQUET")
    load_to_bq("raw_data/taxi_zone.parquet", "raw_taxi_zone", "PARQUET")

    logger.info("Load to GCP completed successfully!")


if __name__ == "__main__":
    # When run directly, use legacy paths for backward compatibility
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    from src.utils.config import Config

    # Use raw_parquet for backward compatibility
    legacy_data_dir = Config.PROJECT_ROOT / "raw_parquet"

    run_load(data_dir=str(legacy_data_dir))
