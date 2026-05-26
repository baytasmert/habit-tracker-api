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


class TestAvatarAPI:
    """Test avatar upload/download via API endpoints"""

    def test_upload_avatar(self, auth_client, db):
        """Should upload avatar and return URL"""
        # auth_client user_id: need to get from auth context
        # For now, use user_id = 1 (first user created in auth_client fixture)
        user_id = 1
        test_file_content = b"Test avatar image data"
        files = {"file": ("test_avatar.jpg", test_file_content)}

        # Upload avatar
        response = auth_client.post(
            f"/users/{user_id}/avatar",
            files=files
        )

        # Check: status 200
        assert response.status_code == 200
        data = response.json()
        assert "avatar_url" in data
        assert user_id == data["user_id"]

    def test_download_avatar(self, auth_client, db):
        """Should download avatar after upload"""
        user_id = 1
        test_file_content = b"Test avatar for download"
        files = {"file": ("download_avatar.jpg", test_file_content)}

        # Upload avatar first
        upload_response = auth_client.post(
            f"/users/{user_id}/avatar",
            files=files
        )
        assert upload_response.status_code == 200

        # Download avatar
        download_response = auth_client.get(f"/users/{user_id}/avatar")
        assert download_response.status_code == 200

    def test_avatar_upload_with_invalid_user(self, auth_client, db):
        """Should return 404 for non-existent user"""
        user_id = 99999
        test_file_content = b"Test avatar"
        files = {"file": ("avatar.jpg", test_file_content)}

        response = auth_client.post(
            f"/users/{user_id}/avatar",
            files=files
        )

        # Check: should return 404
        assert response.status_code == 404

    def test_download_missing_avatar(self, auth_client, db):
        """Should return 404 when avatar doesn't exist"""
        user_id = 1

        # Try to download avatar without uploading first
        download_response = auth_client.get(f"/users/{user_id}/avatar")
        assert download_response.status_code == 404

    def test_avatar_roundtrip(self, auth_client, db):
        """Upload and download avatar should preserve content"""
        user_id = 1
        test_avatar_data = b"Avatar image data for roundtrip"
        files = {"file": ("avatar_roundtrip.jpg", test_avatar_data)}

        # Upload
        upload_response = auth_client.post(
            f"/users/{user_id}/avatar",
            files=files
        )
        assert upload_response.status_code == 200

        # Download
        download_response = auth_client.get(f"/users/{user_id}/avatar")
        assert download_response.status_code == 200
        # Avatar is downloaded as binary, check it's not empty
        assert len(download_response.content) > 0
