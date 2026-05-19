from src.aws.s3_service import S3Service

print("🔧 S3 Service Test\n")

# 1. Service oluştur
print("1️⃣ Creating S3Service...")
s3 = S3Service()
print("✅ S3Service created (bucket auto-created)\n")

# 2. Dosya yükle
print("2️⃣ Uploading file...")
test_data = b'Hello from Habit Tracker!'
url = s3.upload_file('test.txt', test_data)
print(f"✅ File uploaded at: {url}\n")

# 4. Dosya indir
print("3️⃣ Downloading file...")
downloaded_data = s3.download_file('test.txt')
print(f"✅ Downloaded data: {downloaded_data}\n")

# 5. Kontrol et
print("4️⃣ Verification...")
if downloaded_data == test_data:
    print("✅ TEST PASSED! Data matches!\n")
else:
    print("❌ TEST FAILED! Data mismatch!\n")
