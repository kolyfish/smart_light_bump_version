from shared_config import SharedConfig

def test_config_initialization():
    config = SharedConfig(default_symbol="2330.TW", default_target=900.0, default_stop_loss=800.0)
    data = config.get_config()
    assert data["symbol"] == "2330.TW"
    assert data["target_price"] == 900.0
    assert data["stop_loss_price"] == 800.0

def test_config_update():
    config = SharedConfig()
    config.update_config(symbol="2317.TW", target_price=200.0, stop_loss_price=180.0)
    data = config.get_config()
    assert data["symbol"] == "2317.TW"
    assert data["target_price"] == 200.0
    assert data["stop_loss_price"] == 180.0

def test_config_partial_update():
    config = SharedConfig(default_symbol="2330.TW", default_target=900.0)
    # 只更新目標價
    config.update_config(symbol=None, target_price=950.0)
    data = config.get_config()
    assert data["symbol"] == "2330.TW"
    assert data["target_price"] == 950.0

def test_config_invalid_target_price():
    config = SharedConfig(default_target=900.0)
    # 傳入非法字串，應該不被更新
    config.update_config(symbol=None, target_price="abc")
    data = config.get_config()
    assert data["target_price"] == 900.0
