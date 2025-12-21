"""
Unit tests for data extraction module
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

from src.extract.extract_parquet import returnBatches, return_parquet, run_extraction


class TestExtractParquet:
    """Test cases for extract_parquet module"""

    def test_return_batches(self, tmp_path):
        """Test CSV chunked reading"""
        # Create a temporary CSV file
        csv_file = tmp_path / "test.csv"
        df = pd.DataFrame({
            'col1': range(1000),
            'col2': range(1000, 2000)
        })
        df.to_csv(csv_file, index=False)

        # Test batching
        chunk_size = 100
        batches = list(returnBatches(str(csv_file), chunk_size))

        assert len(batches) == 10  # 1000 rows / 100 chunk_size
        assert len(batches[0]) == chunk_size
        assert 'col1' in batches[0].columns
        assert 'col2' in batches[0].columns

    @patch('src.extract.extract_parquet.pq.ParquetWriter')
    @patch('src.extract.extract_parquet.pa.Table')
    def test_return_parquet(self, mock_table, mock_writer):
        """Test Parquet file writing"""
        # Mock data
        mock_chunks = [
            pd.DataFrame({'col1': [1, 2, 3]}),
            pd.DataFrame({'col1': [4, 5, 6]})
        ]

        mock_parquet_writer = MagicMock()
        mock_writer.return_value = mock_parquet_writer

        # Run function
        return_parquet(iter(mock_chunks), 'test.parquet')

        # Verify ParquetWriter was called
        assert mock_writer.called
        assert mock_parquet_writer.write_table.call_count == 2
        assert mock_parquet_writer.close.called

    @patch('src.extract.extract_parquet.returnBatches')
    @patch('src.extract.extract_parquet.return_parquet')
    @patch('src.extract.extract_parquet.Path.exists')
    def test_run_extraction(self, mock_exists, mock_return_parquet, mock_return_batches):
        """Test full extraction process"""
        mock_exists.return_value = True
        mock_return_batches.return_value = iter([pd.DataFrame({'col1': [1, 2, 3]})])

        # Run extraction
        run_extraction(
            base_path='/test/path',
            raw_data_dir='/test/raw',
            output_dir='/test/output'
        )

        # Verify functions were called
        assert mock_return_batches.called
        assert mock_return_parquet.called

    def test_run_extraction_missing_files(self, tmp_path, caplog):
        """Test extraction with missing files"""
        # Use non-existent directory
        non_existent_dir = tmp_path / "non_existent"

        run_extraction(
            base_path=str(tmp_path),
            raw_data_dir=str(non_existent_dir),
            output_dir=str(tmp_path / "output")
        )

        # Check that warnings were logged
        assert "MISSING" in caplog.text or "Skipping" in caplog.text
