import pytest
import time
import requests
from playwright.sync_api import Page, expect

# 注意：執行此測試前，系統必須已經啟動 (./setup_and_run.sh)
# 預設網址為 http://localhost:5001

BASE_URL = "http://localhost:5001"

@pytest.fixture(scope="module", autouse=True)
def ensure_server_is_clean():
    """在測試開始前清除模擬數據"""
    requests.post(f"{BASE_URL}/api/simulate_data", json={"price": None})
    yield
    requests.post(f"{BASE_URL}/api/simulate_data", json={"price": None})

def test_ui_elements_visibility(page: Page):
    """測試網頁核心元素是否正常顯示"""
    page.goto(BASE_URL)
    expect(page.locator("text=監控設定")).to_be_visible()
    expect(page.locator("text=台股大盤")).to_be_visible()
    expect(page.locator("#symbol")).to_be_visible()
    expect(page.locator("#target")).to_be_visible()

def test_buttons_clickability(page: Page):
    """測試各項功能按鈕是否可點擊並有回應 (Toast)"""
    page.goto(BASE_URL)
    
    # 測試「全功能演示」
    page.click("text=完整演示")
    # 雖然無法偵測實體燈光，但可以偵測日誌是否更新
    time.sleep(1)
    expect(page.locator("#log-container")).to_contain_text("演示")

    # 測試「更新智慧監控」腳本
    page.fill("#symbol", "2330.TW")
    page.fill("#target", "999")
    page.click("text=更新監控設定")
    expect(page.locator(".toast")).to_be_visible()
    expect(page.locator(".toast")).to_contain_text("設定已更新")

def test_target_price_alert(page: Page):
    """測試到達目標價格時，日誌是否出現警報 (利用模擬數據)"""
    page.goto(BASE_URL)
    
    # 設定目標價為 500
    page.fill("#symbol", "2330.TW")
    page.fill("#target", "500")
    page.click("text=更新監控設定")
    time.sleep(2)

    # 模擬現價 600 (高於目標) -> 進入監控跌破
    requests.post(f"{BASE_URL}/api/simulate_data", json={"price": 600})
    time.sleep(3)
    
    # 模擬現價 450 (觸發跌破)
    requests.post(f"{BASE_URL}/api/simulate_data", json={"price": 450})
    
    # 檢查日誌內容 (等待最多 15 秒以涵蓋前端 polling)
    expect(page.locator("#log-container")).to_contain_text("觸發警報", timeout=15000)

def test_panic_drop_alert(page: Page):
    """測試閃崩偵測是否正常運作"""
    page.goto(BASE_URL)
    
    # 模擬連續下跌數據 (引入些微波動以免標準差為 0)
    prices = [100.1, 99.9, 100.2, 99.8, 100.0, 100.1, 90.0]
    for p in prices:
        requests.post(f"{BASE_URL}/api/simulate_data", json={"price": p})
        time.sleep(1.2)
        
    expect(page.locator("#log-container")).to_contain_text("偵測到閃崩", timeout=15000)

def test_stop_loss_alert(page: Page):
    """測試停損警報"""
    page.goto(BASE_URL)
    
    page.fill("#symbol", "2330.TW")
    page.fill("#stop_loss", "100")
    page.click("text=更新監控設定")
    
    # 模擬現價跌破停損線
    requests.post(f"{BASE_URL}/api/simulate_data", json={"price": 95})
    
    expect(page.locator("#log-container")).to_contain_text("觸發停損警報", timeout=15000)
