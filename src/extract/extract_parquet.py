"""
Extract module for converting CSV files to Parquet format
"""
import os
from pathlib import Path
from typing import Iterator, Dict
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from ..utils.config import Config
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


def returnBatches(path: str, chunk_size: int) -> Iterator[pd.DataFrame]:
    """
    Return an iterator that yields CSV chunks

    Args:
        path: Path to CSV file
        chunk_size: Number of rows per chunk

    Returns:
        Iterator of pandas DataFrames
    """
    return pd.read_csv(path, chunksize=chunk_size)


def return_parquet(df_iter: Iterator[pd.DataFrame], parquet_file: str) -> None:
    """
    Write CSV chunks to a Parquet file

    Args:
        df_iter: Iterator of pandas DataFrames
        parquet_file: Output parquet file path
    """
    parquet_writer = None

    for i, chunk in enumerate(df_iter):
        logger.info(f"Processing chunk {i}")

        if i == 0:
            # Guess schema from first chunk
            parquet_schema = pa.Table.from_pandas(chunk).schema
            parquet_writer = pq.ParquetWriter(
                parquet_file, parquet_schema, compression=Config.COMPRESSION
            )

        # Convert chunk to table and write
        table = pa.Table.from_pandas(chunk, schema=parquet_schema)
        parquet_writer.write_table(table)

    if parquet_writer:
        parquet_writer.close()
        logger.info(f"Parquet file written: {parquet_file}")


def run_extraction(
    base_path: str = None,
    raw_data_dir: str = None,
    output_dir: str = None
) -> None:
    """
    Main function to run the extraction process

    Args:
        base_path: Base project path (defaults to Config.PROJECT_ROOT)
        raw_data_dir: Directory containing raw CSV files
        output_dir: Directory for output Parquet files
    """
    logger.info("Starting data extraction process")

    # Set paths
    if base_path:
        base_path = Path(base_path)
    else:
        base_path = Config.PROJECT_ROOT

    if not raw_data_dir:
        raw_data_dir = Config.RAW_DATA_DIR
    else:
        raw_data_dir = Path(raw_data_dir)

    if not output_dir:
        output_dir = Config.PROCESSED_DATA_DIR
    else:
        output_dir = Path(output_dir)

    # Ensure directories exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Define file paths
    paths: Dict[str, Path] = {
        "Yellow Taxi": raw_data_dir / Config.YELLOW_TAXI_CSV,
        "Green Taxi": raw_data_dir / Config.GREEN_TAXI_CSV,
        "Taxi Zone": raw_data_dir / Config.TAXI_ZONE_CSV
    }

    # Check files exist
    for name, path in paths.items():
        if path.exists():
            logger.info(f"[OK] {name} file found at: {path}")
        else:
            logger.warning(f"[MISSING] {name} file NOT found at: {path}")

    # Convert each CSV to Parquet
    for name, path in paths.items():
        if not path.exists():
            logger.warning(f"Skipping {name} - file not found")
            continue

        logger.info(f"\n=== Converting {name} to Parquet ===")
        df_iter = returnBatches(str(path), Config.CHUNK_SIZE)
        parquet_file = output_dir / f"{name.replace(' ', '_').lower()}.parquet"
        return_parquet(df_iter, str(parquet_file))

    logger.info("Extraction completed successfully!")


if __name__ == "__main__":
    # When run directly, use legacy paths for backward compatibility
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    from src.utils.config import Config

    # Use dbt/raw_data for backward compatibility
    legacy_raw_data = Config.PROJECT_ROOT / "dbt" / "raw_data"
    legacy_output = Config.PROJECT_ROOT / "raw_parquet"

    run_extraction(
        raw_data_dir=str(legacy_raw_data),
        output_dir=str(legacy_output)
    )
