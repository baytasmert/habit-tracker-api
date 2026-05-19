"""
Unit Tests for Auth Functions
Test Type: Unit Testing - isolated function testing
"""
import pytest
from jose import JWTError
from src.auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token
)


class TestPasswordHashing:
    """Unit tests for password hashing"""

    def test_hash_password_not_plain(self):
        """Hashed password should not be plain text"""
        plain = "mypassword123"
        hashed = hash_password(plain)

        assert hashed != plain
        assert len(hashed) > len(plain)

    def test_verify_correct_password(self):
        """verify_password should return True for correct password"""
        plain = "correctpassword"
        hashed = hash_password(plain)

        assert verify_password(plain, hashed) is True

    def test_verify_wrong_password(self):
        """verify_password should return False for wrong password"""
        plain = "correctpassword"
        wrong = "wrongpassword"
        hashed = hash_password(plain)

        assert verify_password(wrong, hashed) is False

    def test_same_password_different_hash(self):
        """Same password should produce different hashes (bcrypt salting)"""
        password = "samepassword"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTToken:
    """Unit tests for JWT token operations"""

    def test_create_token_format(self):
        """Created token should be valid JWT format (3 parts)"""
        token = create_access_token(user_id=5)

        parts = token.split(".")
        assert len(parts) == 3

    def test_verify_valid_token(self):
        """verify_token should return user_id from valid token"""
        user_id = 42
        token = create_access_token(user_id=user_id)

        retrieved_id = verify_token(token)
        assert retrieved_id == user_id

    def test_verify_invalid_token(self):
        """verify_token should raise exception for invalid token"""
        invalid_token = "invalid.token.here"

        with pytest.raises(Exception):
            verify_token(invalid_token)

    def test_verify_corrupted_token(self):
        """verify_token should raise exception for corrupted token"""
        token = create_access_token(user_id=5)
        corrupted = token[:-5] + "xxxxx"  # Corrupt signature

        with pytest.raises(Exception):
            verify_token(corrupted)

    def test_verify_different_user_ids(self):
        """Tokens for different users should return different user_ids"""
        token1 = create_access_token(user_id=1)
        token2 = create_access_token(user_id=2)

        assert verify_token(token1) == 1
        assert verify_token(token2) == 2
