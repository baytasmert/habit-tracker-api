"""
S3 Integration Tests
Test avatar upload/download functionality via LocalStack S3
"""
import pytest
from src.aws.s3_service import S3Service


class TestS3Basic:
    """Test basic S3 operations (upload/download)"""

    def test_s3_service_creation(self):
        """S3Service should initialize without errors"""
        s3 = S3Service()
        assert s3 is not None

    def test_s3_upload_file(self):
        """Should upload file to S3"""
        s3 = S3Service()
        test_data = b'Hello from Habit Tracker!'

        url = s3.upload_file('test.txt', test_data)

        # Check: URL returned and not empty
        assert url is not None
        assert len(url) > 0
        assert 's3' in url.lower() or 'test.txt' in url

    def test_s3_download_file(self):
        """Should download file from S3"""
        s3 = S3Service()
        test_data = b'Test download data'

        # Upload first
        s3.upload_file('download_test.txt', test_data)

        # Download
        downloaded_data = s3.download_file('download_test.txt')

        # Check: data matches
        assert downloaded_data == test_data

    def test_s3_upload_download_roundtrip(self):
        """Upload and download should preserve data integrity"""
        s3 = S3Service()
        test_data = b'Round trip test data 12345!'
        filename = 'roundtrip_test.bin'

        # Upload
        upload_url = s3.upload_file(filename, test_data)
        assert upload_url is not None

        # Download
        downloaded_data = s3.download_file(filename)
        assert downloaded_data == test_data

        # Verify content
        assert len(downloaded_data) == len(test_data)
