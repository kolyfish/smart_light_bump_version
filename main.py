import sys
import os

# 將 src 目錄加入 path，讓 src 內部的 import shared_config 能夠運作
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    from src.market_trade_alert_light import main
    main()
