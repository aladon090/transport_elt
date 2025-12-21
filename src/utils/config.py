"""
Configuration management for the Transport ELT Pipeline
"""
import os
from pathlib import Path
from typing import Optional


class Config:
    """Centralized configuration for the ELT pipeline"""

    # Project paths
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    RAW_DATA_DIR = DATA_DIR / "raw"
    PROCESSED_DATA_DIR = DATA_DIR / "processed"
    STAGING_DATA_DIR = DATA_DIR / "staging"

    # GCP Configuration
    GCS_BUCKET = os.getenv("GCS_BUCKET", "transport-analytics")
    PROJECT_ID = os.getenv("GCP_PROJECT_ID", "taxi-transport-analytics")
    BQ_DATASET = os.getenv("BQ_DATASET", "new_york_analytic")
    CREDENTIALS_PATH = os.getenv(
        "GOOGLE_APPLICATION_CREDENTIALS",
        str(PROJECT_ROOT / "config" / "credentials" / "taxi-transport-analytics-fbfa6653d305.json")
    )

    # Data files
    YELLOW_TAXI_CSV = "yellow_tripdata_2019-12.csv"
    GREEN_TAXI_CSV = "green_tripdata_2019-12.csv"
    TAXI_ZONE_CSV = "taxi_zone_lookup (1).csv"

    # Processing configuration
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "100000"))
    COMPRESSION = "snappy"

    @classmethod
    def get_raw_data_path(cls, filename: str) -> Path:
        """Get path to raw data file"""
        return cls.RAW_DATA_DIR / filename

    @classmethod
    def get_processed_data_path(cls, filename: str) -> Path:
        """Get path to processed data file"""
        return cls.PROCESSED_DATA_DIR / filename

    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist"""
        cls.RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.STAGING_DATA_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def set_gcp_credentials(cls, credentials_path: Optional[str] = None):
        """Set GCP credentials environment variable"""
        path = credentials_path or cls.CREDENTIALS_PATH
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(path)
        return path
