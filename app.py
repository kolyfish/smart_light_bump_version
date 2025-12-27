import time
import sys
from shared_config import SharedConfig
from tapo_controller import TapoController
from stock_monitor import StockMonitor
from web_server import WebServer

def main():
    print("🚀 Starting SmartStockLight in Headless Mode...")
    
    # Initialize Components
    shared_config = SharedConfig()
    tapo = TapoController(shared_config)
    
    # Start Threads
    monitor = StockMonitor(shared_config, tapo)
    monitor.start()
    
    server = WebServer(shared_config, tapo, monitor)
    # WebServer is a daemon thread, so it won't block or need manual stopping
    server.start()
    
    print("✅ System is up and running. Press Ctrl+C to stop.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        monitor.running = False
        sys.exit(0)

if __name__ == "__main__":
    main()
