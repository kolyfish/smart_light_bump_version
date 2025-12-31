import webview
import threading
import time
import sys
import os
from shared_config import SharedConfig
from tapo_controller import TapoController
from stock_monitor import StockMonitor
from web_server import WebServer
import subprocess

def cleanup_port(port=5001):
    """如果端口被佔用，強制關閉佔用該端口的程序 (Mac/Linux)"""
    try:
        # 查找佔用端口的 PID
        cmd = f"lsof -ti :{port}"
        pid = subprocess.check_output(cmd, shell=True).decode().strip()
        if pid:
            print(f"🧹 清理佔用端口 {port} 的舊程序 (PID: {pid})...")
            subprocess.run(f"kill -9 {pid}", shell=True)
            time.sleep(1) # 等待釋放
    except subprocess.CalledProcessError:
        # 沒有程序佔用端口
        pass
    except Exception as e:
        print(f"清理端口時發生錯誤: {e}")

def main():
    cleanup_port()
    print("🚀 Starting SmartStockLight GUI...")
    
    # Initialize Components
    shared_config = SharedConfig()
    tapo = TapoController(shared_config)
    
    # Start Logic Threads
    monitor = StockMonitor(shared_config, tapo)
    monitor.start()
    
    # Start Web Server (without auto-opening browser)
    server = WebServer(shared_config, tapo, monitor, open_browser=False)
    server.start()
    
    # Wait a bit for the server to spin up
    time.sleep(1)
    
    # Create the GUI window
    # Note: We point to localhost instead of passing the Flask app object directly
    # because passing the app object runs the server in the main thread which blocks pywebview.
    # We are running Flask in a separate thread already.
    webview.create_window(
        'Smart Stock Light', 
        'http://127.0.0.1:5001',
        width=1200,
        height=800,
        resizable=True
    )
    
    # Start the GUI loop
    # debug=True allows right-click inspect element
    print("🖥️  Opening GUI Window...")
    webview.start(debug=False)
    
    # Cleanup after window closes
    print("\n🛑 Shutting down...")
    monitor.stop()
    sys.exit(0)

if __name__ == "__main__":
    main()
