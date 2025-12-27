
import secrets
import hashlib
import argparse

# Configuration
SECRET_KEY = "SmartStockLight_Secret_Key_2025!"  # 改成你自己的密鑰
LICENSE_FILE = "generated_licenses.txt"
ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # 排除 I, O, 0, 1 避免混淆
GROUP_SIZE = 4
NUM_GROUPS = 4

def generate_key_string(length=12):
    """生成指定長度的隨機字串"""
    return ''.join(secrets.choice(ALPHABET) for _ in range(length))

def sign_key(key_body: str) -> str:
    """對 key_body 進行簽名，回傳最後的校驗碼段"""
    # 簡單的 HMAC 概念：hash(key + secret)
    data = f"{key_body}{SECRET_KEY}"
    hash_object = hashlib.sha256(data.encode())
    digest = hash_object.hexdigest().upper()
    
    # 取前 GROUP_SIZE 個字元轉換成我們的 ALPHABET
    # 這裡為求簡單，直接取 hex digest 的前幾碼，
    # 但為了保證字元在 ALPHABET 內，我們做一個簡單的轉換
    checksum = ""
    for i in range(GROUP_SIZE):
        # 拿兩個 hex char 轉 int，再 mod ALPHABET 長度
        hex_chunk = digest[i*2 : i*2+2]
        val = int(hex_chunk, 16)
        checksum += ALPHABET[val % len(ALPHABET)]
    
    return checksum

def generate_license_key():
    """產生一組完整的 License Key"""
    # 產生隨機部分 (前三個區塊)
    random_part_length = GROUP_SIZE * (NUM_GROUPS - 1)
    random_raw = generate_key_string(random_part_length)
    
    # 為了美觀，分組
    groups = [random_raw[i:i+GROUP_SIZE] for i in range(0, len(random_raw), GROUP_SIZE)]
    formatted_random_part = "".join(groups) # 這裡是用來算的，不含 dash
    
    # 產生校驗碼
    checksum = sign_key(formatted_random_part)
    
    # 組合
    final_key = "-".join(groups + [checksum])
    return final_key

def verify_license_key(key_string):
    """驗證 License Key (供測試用)"""
    key_string = key_string.replace("-", "").strip().upper()
    
    if len(key_string) != GROUP_SIZE * NUM_GROUPS:
        return False
    
    # 切分
    body_length = GROUP_SIZE * (NUM_GROUPS - 1)
    body = key_string[:body_length]
    checksum = key_string[body_length:]
    
    # 驗證
    expected_checksum = sign_key(body)
    return checksum == expected_checksum

def main():
    parser = argparse.ArgumentParser(description="SmartStockLight 序號產生器")
    parser.add_argument("-n", "--number", type=int, default=1, help="產生的序號數量")
    args = parser.parse_args()

    print(f"正在產生 {args.number} 組序號...")
    print("-" * 30)

    keys = []
    for _ in range(args.number):
        key = generate_license_key()
        keys.append(key)
        print(key)

    # 存檔
    with open(LICENSE_FILE, "a") as f:
        for k in keys:
            f.write(k + "\n")
            
    print("-" * 30)
    print(f"✅ 已完成！序號已附加至 {LICENSE_FILE}")
    
    # 測試驗證第一組
    if keys:
        print(f"驗證測試: {keys[0]} -> {verify_license_key(keys[0])}")

if __name__ == "__main__":
    main()
