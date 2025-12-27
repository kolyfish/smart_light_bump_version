import subprocess
import time
import os
import sys

def run_e2e():
    print("🚀 正在啟動伺服器進行端到端測試...")
    
    # 設定環境變量
    env = os.environ.copy()
    env["SIMULATION_MODE"] = "true"
    
    # 啟動主程式 (在背景執行)
    # 我們直接執行 main_server.py 的邏輯，或者從 app.py 啟動
    # 這裡假設 ./setup_and_run.sh 中啟動的是 python main_gui.py 或 web_server
    # 實際上可以直接跑一個獨立的測試啟動腳本
    server_process = subprocess.Popen(
        [sys.executable, "app.py"],
        env=env
    )
    
    # 等待伺服器啟動
    time.sleep(10)
    
    try:
        print("🧪 正在執行 Playwright UI 測試...")
        # 執行 pytest 使用 sys.executable -m pytest 以確保環境一致
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/test_ui.py", "--browser", "chromium"],
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
            
        if result.returncode == 0:
            print("✅ 測試全部通過！")
        else:
            print("❌ 測試失敗！")
            sys.exit(1)
            
    finally:
        print("🛑 正在停止伺服器...")
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    run_e2e()
