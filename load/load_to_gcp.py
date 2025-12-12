import os
from google.cloud import storage, bigquery
import pandas as pd

GCS_BUCKET = "transport-analytics"
PROJECT_ID = "taxi-transport-analytics"
BQ_DATASET = "new_york_analytic"
CREDENTIALS_PATH = "../taxi-transport-analytics-fbfa6653d305.json"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDENTIALS_PATH

def upload_to_gcs(local_path, gcs_path):
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET)
    blob = bucket.blob(gcs_path)
    blob.upload_from_filename(local_path)
    print(f"Uploaded {local_path} to gs://{GCS_BUCKET}/{gcs_path}")

def upload_folder(folder_path, prefix):
    for file in os.listdir(folder_path):
        if file.endswith(".csv") or file.endswith(".csv.gz") or file.endswith(".parquet"):
            local_file = os.path.join(folder_path, file)
            gcs_file = f"{prefix}/{file}"
            upload_to_gcs(local_file, gcs_file)

def load_to_bq(gcs_path, table_name):
    client = bigquery.Client(project=PROJECT_ID)
    dataset_ref = client.dataset(BQ_DATASET)
    table_ref = dataset_ref.table(table_name)

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    uri = f"gs://{GCS_BUCKET}/{gcs_path}"
    load_job = client.load_table_from_uri(uri, table_ref, job_config=job_config)
    load_job.result()
    print(f"Loaded {gcs_path} into {BQ_DATASET}.{table_name}")

if __name__ == "__main__":
    upload_folder("raw_parquet/yellow_taxi", "yellow")
    upload_folder("raw_parquet/green_taxi", "green")
    load_to_bq("yellow/*.parquet", "stg_yellow_taxi")
    load_to_bq("green/*.parquet", "stg_green_taxi")
