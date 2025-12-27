# ISTQB 測試理論於 Stock-to-Home Alert 之應用

本專案導入 ISTQB (International Software Testing Qualifications Board) 基礎測試理論，將開發經驗轉化為系統化的品質保證流程。

## 1. 測試設計技術 (Test Design Techniques) - 黑箱測試

### A. 等價劃分 (Equivalence Partitioning, EP)
將所有可能的輸入數據劃分為若干部分，從每一部分中選取少數具代表性的數據進行測試。
*   **有效分區**：如股價為正數、目標價設定在合理範圍。
*   **無效分區**：如股價為 0、負數、或非數字字串。系統應能攔截無效數據而不崩潰。

### B. 邊界值分析 (Boundary Value Analysis, BVA)
大量的錯誤發生在輸入範圍的「關鍵邊界」上。
*   **應用場景**：目標價為 500 元。
*   **測試點**：
    *   499.99 元 (未觸發)
    *   500.00 元 (觸發邊界)
    *   500.01 元 (觸發)

### C. 狀態轉移測試 (State Transition Testing)
監控系統行為隨時間或事件而改變。
*   **Initial (黃燈)** -> *跌破停損* -> **Red (停損)**
*   **Initial (黃燈)** -> *漲破目標* -> **Green (獲利)**
*   **Initial (黃燈)** -> *一分鐘大跌 1.5%* -> **Purple (閃崩)**

## 2. 測試等級 (Test Levels)
*   **單元測試 (Unit Testing)**：測試單一函數（如閃崩跌率計算法）。
*   **整合測試 (Integration Testing)**：測試 Web UI 傳送 Json 到 Backend，Backend 是否正確更新 `SharedConfig`。
*   **系統測試 (System Testing)**：模擬從 Yahoo 抓取數據到最後燈泡發光的完整流程（端到端）。

## 3. 測試類型 (Test Types)
*   **功能測試 (Functional Testing)**：確認報警功能是否如預期運作。
*   **回歸測試 (Regression Testing)**：每次修復 Bug (如 `AttributeError`) 後，執行舊有測試確保沒改壞其他地方。
*   **負載測試 (Load Testing)**：雖然本專案為單人使用，但仍需測試長時間（24H）掛機下的穩定性。

## 4. 軟體測試原則 (Seven Principles of Testing)
*   **測試顯示缺陷的存在**：我們透過測試發現 `TapoBulb` 沒有 `close` 方法。
*   **窮盡測試是不可能的**：我們無法測試全世界所有股票的所有價格變動，因此使用 EP 與 BVA。
*   **缺陷集群性 (Defect Clustering)**：通常大部份的錯誤會集中在特定的連線組件中。
