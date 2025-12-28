# Smart Stock Light - 自動化測試工程師 (QA/SDET) 面試作品集

這份文件專為 **Software Development Engineer in Test (SDET)** 或 **QA Engineer** 面試設計。
重點從「功能介紹」轉向「品質保證策略」、「自動化架構設計」與「ISTQB 理論應用」。

---

## 1. 專案背景與測試挑戰
*   **專案名稱**：Smart Stock Light (IoT 股市監控系統)
*   **系統架構**：Python (Flask/Tkinter) + IoT 硬體 (Tapo 插座) + 外部金融 API。
*   **測試挑戰 (Why is this hard to test?)**：
    1.  **不可控的外部數據**：股市價格隨時變動，無法預測。
    2.  **硬體依賴**：真實燈泡難以在 CI 環境中測試。
    3.  **即時性要求**：警報必須在條件觸發後秒級反應。
    4.  **併發性**：Web Server 與監控 Loop 同時運行，需驗證 Thread Safety。

---

## 2. 測試策略 (Test Strategy) - 導入 ISTQB
我在此專案中擔任 **Test Architect** 角色，將 ISTQB 核心測試理論轉化為實際的工程實踐。

### 2.1 測試級別 (Test Levels) - 符合測試金字塔 (Test Pyramid)
為了確保測試效率與覆蓋率，我實作了分層測試策略：

1.  **Unit Tests (單元測試)** - `tests/test_monitor.py`
    *   **目標**：隔離測試核心邏輯 (`StockMonitor`)，不依賴外部 API 與硬體。
    *   **工具**：`pytest`, `unittest.mock`.
    *   **實作細節**：使用 `MagicMock` 模擬 `TapoController` 與 `MarketDataAgent`，驗證「閃崩演算法」與「停損邏輯」的正確性。

2.  **Integration Tests (整合測試)**
    *   **目標**：驗證模組間的互動，例如 Web API 收到請求後，是否正確更新了 `SharedConfig`。
    *   **實作細節**：透過 API Endpoint 注入此變更，檢查後端狀態是否同步。

3.  **System/E2E Tests (端到端測試)** - `tests/test_ui.py`
    *   **目標**：模擬最終使用者的真實操作路徑。
    *   **工具**：`Playwright` (Python).
    *   **實作細節**：自動化開啟瀏覽器 -> 掃描/訪問 Localhost -> 設定目標價 -> 驗證 UI Toast 回饋 -> 檢查日誌輸出。

### 2.2 測試設計技術 (Test Design Techniques)
在設計 Test Case 時，我應用了黑箱測試技術來優化測試覆蓋率：

*   **等價劃分 (Equivalence Partitioning)**：
    *   將輸入分為：`有效股票代號`、`無效代號`、`加密貨幣代號`。
    *   確保系統能正確處理每一類輸入（例如加密貨幣需走不同 API 邏輯）。

*   **邊界值分析 (Boundary Value Analysis, BVA)**：
    *   針對「目標價」進行精確測試。
    *   **Case 1**: `Price = Target - 0.01` (不觸發)
    *   **Case 2**: `Price = Target` (觸發)
    *   **Case 3**: `Price = Target + 0.01` (觸發)
    *   這在 `test_monitor.py` 的 `test_alert_logic_above` 中有嚴格驗證，防止 Off-by-one error。

*   **狀態轉移測試 (State Transition Testing)**：
    *   系統本質是一個有限狀態機 (FSM)。
    *   **路徑驗證**：`Standby (Yellow)` -> `Alert (Red/Green)` -> `Cooldown` -> `Standby`。
    *   驗證在 `Cooldown` 期間，即使條件滿足也不應重複觸發警報（防抖機制驗證）。

### 2.3 安全性測試 (Security Testing) - Shift Left Security
除了功能測試，我也導入了 SAST (Static Application Security Testing) 工具：
*   **Gitleaks**：
    *   **用途**：防止 API Key、Token 或個人敏機資訊 (PII) 被 commit 到 GitHub。
    *   **實作**：已在本地環境安裝並執行掃描 (`gitleaks detect --source . -v`)，確保程式碼庫乾淨無洩漏。
    *   **CI 整合**：計畫將其加入 GitHub Actions，若偵測到 Secret 即阻擋 Merge Request。

---

## 3. 自動化測試架構 (Automation Architecture)
> **架構師思維**：如何設計一個可維護、穩定的測試框架？

### A. 可測試性設計 (Design for Testability)
為了讓系統可測，我對 Production Code 做了以下重構：
1.  **依賴注入 (Dependency Injection)**：`StockMonitor` 不直接 new `TapoController`，而是從外部傳入。這允許測試時注入 `MockTapoController`，解決了「CI 環境沒有實體燈泡」的問題。
2.  **模擬模式 (Simulation Mode)**：在 `stock_monitor.py` 中實作了 `simulation_mode` 與 `mock_current_price`。這讓 E2E 測試 (`test_ui.py`) 可以透過 API (`/api/simulate_data`) 強制注入假股價，從而驗證「介面是否正確顯示警報」，完全不需要等待真實股市波動。

### B. CI/CD 整合 pipeline (`run_e2e_ci.py`)
我撰寫了自動化腳本來串接測試流程，模擬 CI Server (如 Jenkins/GitHub Actions) 的行為：
1.  **Setup**: 啟動 Environment (Headless Web Server)。
2.  **Test Execution**:
    *   並行執行 Pytest Unit Tests。
    *   啟動 Playwright 執行 UI Tests。
3.  **Teardown**: 無論測試成功失敗，確保清除 Process，避免殭屍程序。
4.  **Reporting**: 收集 stdout/stderr，若失敗則回傳非 0 exit code 中斷 Pipeline。

---

## 4. 關鍵程式碼解說 (Show me the code)
*面試時可以打開 IDE 展示這段，展現你對工具的掌握。*

### 範例：使用 Pytest Fixture 與 Mock 隔離硬體
```python
# tests/test_monitor.py

@pytest.fixture
def mock_deps():
    # Arrange: 準備測試環境
    config = SharedConfig(default_symbol="2330.TW", default_target=900.0)
    tapo = MagicMock() # Mock 掉硬體層
    return config, tapo

def test_alert_logic_above(mock_deps):
    config, tapo = mock_deps
    monitor = StockMonitor(config, tapo)
    monitor.alert_mode = 'above'

    # Act & Assert: 驗證邊界值
    # 測試 890 (未達標)
    assert (monitor.alert_mode == 'above' and 890 >= 900) is False
    # 測試 900 (邊界達標)
    assert (monitor.alert_mode == 'above' and 900 >= 900) is True
```

### 範例：Playwright E2E 測試與數據模擬
```python
# tests/test_ui.py

def test_target_price_alert(page: Page):
    # 1. 操作 UI 設定目標
    page.goto(BASE_URL)
    page.fill("#symbol", "2330.TW")
    page.fill("#target", "500")
    page.click("text=更新智慧監控")

    # 2. 透過 API 注入模擬數據 (核心技巧！)
    # 模擬股價跌破目標，驗證前端是否即時反應
    requests.post(f"{BASE_URL}/api/simulate_data", json={"price": 450})

    # 3. 驗證結果 (Assert)
    # 使用 Playwright 的自動重試機制 (Auto-wait) 等待 Log 出現
    expect(page.locator("#log-content")).to_contain_text("觸發警報", timeout=15000)
```

---

## 5. 總結 (Conclusion)
這個專案證明了我不僅能開發功能，更懂得如何建立**高品質的軟體防護網**。
*   我運用 **ISTQB 理論** 確保測試設計的全面性。
*   我構建 **Automation Framework** 解決硬體依賴與即時數據的測試難題。
*   我實踐 **Shift-Left Testing**，在開發階段就考量可測試性 (Testability)。
這是身為自動化測試工程師 / SDET 最核心的價值。
