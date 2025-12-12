import pandas as pd
import os
import pyarrow as pa
import pyarrow.parquet as pq


def returnBatches(path, CHUNK):
    """Return an iterator that yields CSV chunks."""
    return pd.read_csv(path, chunksize=CHUNK)


def return_parquet(df_iter, parquet_file):
    """Write CSV chunks to a Parquet file."""
    parquet_writer = None

    for i, chunk in enumerate(df_iter):
        print(f"Processing chunk {i}")

        if i == 0:
            # Guess schema from first chunk
            parquet_schema = pa.Table.from_pandas(chunk).schema
            parquet_writer = pq.ParquetWriter(
                parquet_file, parquet_schema, compression='snappy'
            )

        # Convert chunk to table and write
        table = pa.Table.from_pandas(chunk, schema=parquet_schema)
        parquet_writer.write_table(table)

    if parquet_writer:
        parquet_writer.close()
        print(f"Parquet file written: {parquet_file}")


if __name__ == "__main__":
    FILE_YELLOW_TAXI_PATH = "../raw_data/yellow_tripdata_2019-12.csv"
    FILE_GREEN_TAXI_PATH = "../raw_data/green_tripdata_2019-12.csv"
    TAXI_ZONE_PATH = "../raw_data/taxi_zone_lookup (1).csv"


    CHUNK = 100000

    paths = {
        "Yellow Taxi": FILE_YELLOW_TAXI_PATH,
        "Green Taxi": FILE_GREEN_TAXI_PATH,
         "Taxi Zone" : TAXI_ZONE_PATH
    }

    # Check files
    for name, path in paths.items():
        if os.path.exists(path):
            print(f"[OK] {name} file found at: {path}")
        else:
            print(f"[MISSING] {name} file NOT found at: {path}")

    # Convert each CSV to Parquet
    for name, path in paths.items():
        print(f"\n=== Converting {name} to Parquet ===")
        df_iter = returnBatches(path, CHUNK)
        parquet_file = f"{name.replace(' ', '_').lower()}.parquet"
        return_parquet(df_iter, parquet_file)
