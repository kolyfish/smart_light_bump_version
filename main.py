import sys
import os

# 將 src 目錄加入 path，讓 src 內部的 import shared_config 能夠運作
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def is_already_running():
    """檢查是否有另一個實例正在運行 (使用文件鎖)"""
    import fcntl
    lock_file_path = os.path.join(os.path.dirname(__file__), 'config', 'app.lock')
    
    # 確保 config 目錄存在
    os.makedirs(os.path.dirname(lock_file_path), exist_ok=True)
    
    # 開啟鎖定文件 (這組變數必須保持存在才能鎖住)
    global lock_file
    lock_file = open(lock_file_path, 'w')
    
    try:
        # 嘗試取得排他鎖，非阻塞模式
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return False
    except IOError:
        return True

if __name__ == "__main__":
    if is_already_running():
        print("\n" + "="*50)
        print("⚠️  錯誤：SmartStockLight 已經在運行中！")
        print("為避免硬體控制衝突，本程式將自動退出。")
        print("="*50 + "\n")
        sys.exit(1)
        
    from src.market_trade_alert_light import main
    main()
