import os
import sys

LICENSE_FILE = ".license_key"
DEV_KEY = "DEV-8888"

def check_license():
    """
    Checks for a valid license key.
    If not found, prompts the user to enter it via the console.
    Returns True if valid, False/Exits if invalid.
    """
    print("------------------------------------------")
    print("   🔒 授權驗證 / License Verification")
    print("------------------------------------------")

    # 1. Check if license file exists
    if os.path.exists(LICENSE_FILE):
        try:
            with open(LICENSE_FILE, "r", encoding="utf-8") as f:
                stored_key = f.read().strip()
                if stored_key == "VERIFIED":
                    print("✅ 授權已驗證 (License Verified)")
                    return True
        except Exception:
            pass # File read error, treat as invalid

    # 2. Prompt for key
    while True:
        print("\n本軟體為開發測試版，請輸入授權序號。")
        print("Please enter the license key.")
        try:
            user_input = input("Key: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n用戶取消。")
            sys.exit(1)

        if user_input == DEV_KEY:
            print("✅ 序號正確！(Key Accepted)")
            try:
                with open(LICENSE_FILE, "w", encoding="utf-8") as f:
                    f.write("VERIFIED")
            except Exception as e:
                print(f"Warning: Could not save license file: {e}")
            return True
        else:
            print("❌ 序號錯誤，請重試。(Invalid Key)")
            
if __name__ == "__main__":
    check_license()
