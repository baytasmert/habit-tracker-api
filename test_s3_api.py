import requests
import time

BASE_URL = "http://localhost:8001"
timestamp = str(int(time.time()))

print("[*] S3 Avatar API Test\n")

# 1. Kullanıcı oluştur
print("[1] Creating user...")
user_response = requests.post(
    f"{BASE_URL}/users",
    data={"username": f"testuser_{timestamp}", "email": f"test_{timestamp}@example.com"}
)
print(f"Status: {user_response.status_code}")
user_data = user_response.json()
user_id = user_data["id"]
print(f"[OK] User created: {user_data}\n")

# 2. Avatar yukle
print("[2] Uploading avatar...")
test_file_content = b"Test avatar image data"
files = {"file": ("test_avatar.jpg", test_file_content)}
upload_response = requests.post(
    f"{BASE_URL}/users/{user_id}/avatar",
    files=files
)
print(f"Status: {upload_response.status_code}")
upload_data = upload_response.json()
print(f"[OK] Avatar uploaded: {upload_data}\n")

# 3. Avatar indir
print("[3] Downloading avatar...")
download_response = requests.get(f"{BASE_URL}/users/{user_id}/avatar")
print(f"Status: {download_response.status_code}")
print(f"[OK] Avatar downloaded ({len(download_response.content)} bytes)\n")

print("[OK] TEST COMPLETED!")

