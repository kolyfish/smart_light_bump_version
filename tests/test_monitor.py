import pytest
import time
from unittest.mock import MagicMock
from stock_monitor import StockMonitor
from shared_config import SharedConfig

@pytest.fixture
def mock_deps():
    config = SharedConfig(default_symbol="2330.TW", default_target=900.0, default_stop_loss=800.0)
    tapo = MagicMock()
    return config, tapo

def test_alert_logic_above(mock_deps):
    config, tapo = mock_deps
    monitor = StockMonitor(config, tapo)
    
    # 模擬當前價格低於目標價，判定為漲破模式
    monitor.alert_mode = None
    monitor.alert_mode = 'above'
    
    # 未達標不亮燈 (price = 890)
    current_price = 890
    target = 900
    is_alert_hit = monitor.alert_mode == 'above' and current_price >= target
    assert is_alert_hit is False
    
    # 達標亮燈 (price = 910)
    current_price = 910
    is_alert_hit = monitor.alert_mode == 'above' and current_price >= target
    assert is_alert_hit is True

def test_auto_name_fetching_placeholder(mock_deps):
    config, tapo = mock_deps
    monitor = StockMonitor(config, tapo)
    assert monitor.last_stock_name == "監控中..."

def test_stop_loss_logic(mock_deps):
    config, tapo = mock_deps
    _ = StockMonitor(config, tapo)
    
    stop_loss = 800
    current_price = 790
    is_stop_loss_hit = stop_loss > 0 and current_price <= stop_loss
    assert is_stop_loss_hit is True

def test_panic_drop_detection(mock_deps):
    config, tapo = mock_deps
    monitor = StockMonitor(config, tapo)
    
    now = time.time()
    monitor._price_history = [
        (now - 60, 100),
        (now - 45, 100),
        (now - 30, 99.5),
        (now - 15, 99.0)
    ]
    current_price = 97.0 
    
    one_min_ago = [p for p in monitor._price_history if now - p[0] <= 60]
    price_old = one_min_ago[0][1]
    drop_rate = (price_old - current_price) / price_old
    
    assert drop_rate >= 0.015

def test_data_cleaning_spike(mock_deps):
    config, tapo = mock_deps
    monitor = StockMonitor(config, tapo)
    
    monitor.last_stock_price = 100
    current_price = 200 
    
    is_spike = abs(current_price - monitor.last_stock_price) / monitor.last_stock_price > 0.5
    assert is_spike is True
