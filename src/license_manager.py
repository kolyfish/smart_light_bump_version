import hashlib
import secrets
import os
import sys
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

LICENSE_FILE = "config/.license_key"
DEV_KEY = "DEV-8888"

# 必須與 generator 保持一致
# 優先讀取 .env 中的 SECRET_KEY，如果沒有則使用預設值
SECRET_KEY = os.getenv("SECRET_KEY", "SmartStockLight_Secret_Key_2025!")
ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
GROUP_SIZE = 4
NUM_GROUPS = 4

def sign_key(key_body: str) -> str:
    """計算校驗碼 (需與 generator 邏輯一致)"""
    data = f"{key_body}{SECRET_KEY}"
    hash_object = hashlib.sha256(data.encode())
    digest = hash_object.hexdigest().upper()
    
    checksum = ""
    for i in range(GROUP_SIZE):
        hex_chunk = digest[i*2 : i*2+2]
        val = int(hex_chunk, 16)
        checksum += ALPHABET[val % len(ALPHABET)]
    
    return checksum

def verify_license_key(key_string):
    """驗證 License Key 是否有效"""
    # 1. 檢查是否為開發者金鑰
    if key_string.strip() == DEV_KEY:
        return True

    # 2. 格式清理
    key_string = key_string.replace("-", "").strip().upper()
    
    # 長度檢查
    if len(key_string) != GROUP_SIZE * NUM_GROUPS:
        return False
    
    # 3. 演算法驗證
    body_length = GROUP_SIZE * (NUM_GROUPS - 1)
    body = key_string[:body_length]
    checksum = key_string[body_length:]
    
    expected_checksum = sign_key(body)
    return checksum == expected_checksum

def check_license():
    """
    Checks for a valid license key.
    If not found, prompts the user to verify via console input.
    Returns True if valid, False/Exits if invalid.
    """
    print("------------------------------------------")
    print("   🔒 授權驗證 / License Verification")
    print("------------------------------------------")

    # 1. 自動檢查既存的授權檔
    if os.path.exists(LICENSE_FILE):
        try:
            with open(LICENSE_FILE, "r", encoding="utf-8") as f:
                stored_key = f.read().strip()
                if verify_license_key(stored_key):
                    print("✅ 授權已驗證 (License Verified)")
                    return True
                else:
                    print("⚠️  儲存的授權無效 (Invalid stored license)")
        except Exception:
            pass 

    # 2. 提示輸入
    while True:
        print("\n請輸入產品序號 (例如: A1B2-C3D4-E5F6-7G8H)")
        print("Please enter your license key.")
        try:
            user_input = input("License Key: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n❌ 用戶取消。")
            sys.exit(1)

        if verify_license_key(user_input):
            print("✅ 序號正確！(Key Accepted)")
            try:
                # 儲存正確的序號到檔案，以便下次自動登入
                with open(LICENSE_FILE, "w", encoding="utf-8") as f:
                    f.write(user_input)
            except Exception as e:
                print(f"Warning: Could not save license file: {e}")
            return True
        else:
            print("❌ 序號錯誤，請重試。(Invalid Key)")

if __name__ == "__main__":
    check_license()
