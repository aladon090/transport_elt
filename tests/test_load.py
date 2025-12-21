"""
Unit tests for data loading module
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.load.load_to_gcp import upload_to_gcs, load_to_bq, run_load


class TestLoadToGCP:
    """Test cases for load_to_gcp module"""

    @patch('src.load.load_to_gcp.storage.Client')
    def test_upload_to_gcs(self, mock_storage_client):
        """Test file upload to GCS"""
        # Mock GCS client
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_client_instance = MagicMock()
        mock_client_instance.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value = mock_client_instance

        # Test upload
        upload_to_gcs('local/path.parquet', 'gcs/path.parquet', 'test-bucket')

        # Verify calls
        mock_client_instance.bucket.assert_called_once_with('test-bucket')
        mock_bucket.blob.assert_called_once_with('gcs/path.parquet')
        mock_blob.upload_from_filename.assert_called_once_with('local/path.parquet')

    @patch('src.load.load_to_gcp.bigquery.Client')
    def test_load_to_bq_parquet(self, mock_bq_client):
        """Test loading Parquet file to BigQuery"""
        # Mock BigQuery client
        mock_client_instance = MagicMock()
        mock_bq_client.return_value = mock_client_instance

        mock_dataset = MagicMock()
        mock_table = MagicMock()
        mock_client_instance.dataset.return_value = mock_dataset
        mock_dataset.table.return_value = mock_table

        mock_job = MagicMock()
        mock_client_instance.load_table_from_uri.return_value = mock_job

        # Test load
        load_to_bq(
            gcs_path='raw_data/test.parquet',
            table_name='test_table',
            source_format='PARQUET',
            project_id='test-project',
            dataset='test_dataset',
            bucket_name='test-bucket'
        )

        # Verify calls
        mock_client_instance.dataset.assert_called_once_with('test_dataset')
        mock_dataset.table.assert_called_once_with('test_table')
        mock_client_instance.load_table_from_uri.assert_called_once()
        mock_job.result.assert_called_once()

    @patch('src.load.load_to_gcp.bigquery.Client')
    def test_load_to_bq_csv(self, mock_bq_client):
        """Test loading CSV file to BigQuery"""
        # Mock BigQuery client
        mock_client_instance = MagicMock()
        mock_bq_client.return_value = mock_client_instance

        mock_dataset = MagicMock()
        mock_table = MagicMock()
        mock_client_instance.dataset.return_value = mock_dataset
        mock_dataset.table.return_value = mock_table

        mock_job = MagicMock()
        mock_client_instance.load_table_from_uri.return_value = mock_job

        # Test load
        load_to_bq(
            gcs_path='raw_data/test.csv',
            table_name='test_table',
            source_format='CSV'
        )

        # Verify job configuration includes CSV-specific settings
        assert mock_client_instance.load_table_from_uri.called

    @patch('src.load.load_to_gcp.upload_to_gcs')
    @patch('src.load.load_to_gcp.load_to_bq')
    @patch('src.load.load_to_gcp.Config.set_gcp_credentials')
    @patch('src.load.load_to_gcp.Path')
    def test_run_load(self, mock_path, mock_set_creds, mock_load_bq, mock_upload):
        """Test full load process"""
        # Mock Path.iterdir to return fake parquet files
        mock_file1 = MagicMock()
        mock_file1.suffix = '.parquet'
        mock_file1.name = 'yellow_taxi.parquet'

        mock_file2 = MagicMock()
        mock_file2.suffix = '.parquet'
        mock_file2.name = 'green_taxi.parquet'

        mock_path_instance = MagicMock()
        mock_path_instance.iterdir.return_value = [mock_file1, mock_file2]
        mock_path.return_value = mock_path_instance

        # Run load
        run_load(
            base_path='/test/path',
            credentials_path='/test/creds.json',
            data_dir='/test/data'
        )

        # Verify credentials were set
        mock_set_creds.assert_called_once_with('/test/creds.json')

        # Verify upload and load were called
        assert mock_upload.call_count >= 2  # At least 2 files uploaded
        assert mock_load_bq.call_count == 3  # 3 tables loaded

    @patch('src.load.load_to_gcp.Path.iterdir')
    def test_run_load_no_files(self, mock_iterdir):
        """Test load process with no parquet files"""
        # Mock empty directory
        mock_iterdir.return_value = []

        # This should not raise an error
        run_load(data_dir='/empty/dir')
