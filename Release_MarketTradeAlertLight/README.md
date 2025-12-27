# MarketTradeAlertLight (股市亮燈提醒系統) 🟢

這是一個專為非工程師設計的股市監控系統。當您關注的股票跌破目標價時，系統會自動透過 **Tapo 智慧插座** 點亮家中綠燈，並發出語音提醒。

## ✨ 特色
- **一鍵啟動**：專為 Mac 使用者設計的簡易腳本。
- **手機操控**：掃描電腦螢幕上的 QR Code，即可直接用手機設定股票代號與目標價。
- **高品質界面**：全新升級的深色模式 Web UI，高端大氣且直覺。
- **語音警示**：跌破價格時會自動朗讀警報。

---

## 🚀 快速開始 (Mac 使用者)

## 🚀 快速開始 (Mac 使用者)

### 1. 取得開發者序號
本軟體目前處於開發階段，安裝時需輸入授權序號。
**開發專用序號**: `DEV-8888`

## 🚀 快速開始 (Quick Start)

### 1. 取得開發者序號 (License Key)
- **開發專用序號**: `DEV-8888`

### 2. 下載與安裝 (Installation)
請根據您的作業系統選擇：

####  macOS 使用者
1. 找到 `install_and_run.command` 檔案。
2. **直接雙擊** 執行。
3. 程式會自動安裝環境並啟動，首次啟動請輸入序號。

#### 🪟 Windows 使用者
1. 確保已安裝 [Python](https://www.python.org/downloads/) (記得勾選 "Add Python to PATH")。
2. 找到 `install_and_run.bat` 檔案。
3. **直接雙擊** 執行。
4. 程式會自動安裝環境並啟動，首次啟動請輸入序號。

---

## 📱 如何使用 Web 界面
1. 程式啟動後，電腦螢幕會出現一個 **QR Code**。
2. 使用手機相機掃描 QR Code。
3. 在手機網頁上輸入：
   - **股票代號** (例如台積電為 `2330.TW`)。
   - **目標價格** (當股價低於此數字時會觸發亮燈)。
4. 點擊 **"更新智慧監控"**。

---

## 🛠 硬體需求
- **TP-Link Tapo 智慧插座** (例如 P100/P110)。
- 插座需與電腦連接在同一個 Wi-Fi 環境下。
- 預設 IP: `192.168.100.150` (請在 `tapo_controller.py` 中視需求修改)。

---

## ⚠️ 注意事項
- 請確保您的電腦與手機在同一個 Wi-Fi 網路下，QR Code 才能正常連接。
- 此系統僅供參考，股市投資有風險，請謹慎操作。
            # 本檔案

## 技術架構

### 三層架構設計

1. **Hardware Layer** (`tapo_controller.py`)
   - 負責與 TP-Link Tapo L530E 溝通
   - 提供 Thread-safe 的同步介面

2. **Logic Layer** (`stock_monitor.py`)
   - 負責抓取股價與判斷邏輯
   - 實作 Debounce 機制（5 分鐘冷卻時間）
   - 整合 TTS 語音播報

3. **Presentation Layer** (`smart_stock_light.py`)
   - 使用 tkinter 建構 GUI
   - 管理背景監控 Thread
   - 提供即時日誌顯示

### 關鍵技術

- **Threading**：監控迴圈在背景 Thread 執行，不阻塞 GUI
- **Async/Await**：Tapo 控制使用 `plugp100` 的 Async API
- **Logging Handler**：自訂 Handler 將日誌輸出到 GUI
- **Config Persistence**：自動儲存/載入使用者設定

## 注意事項

- 確保 Mac 與 Tapo 燈泡連接到同一個 Wi-Fi 網路
- 首次使用時，建議先測試燈泡連接（可在程式中加入測試按鈕）
- 監控迴圈每 60 秒執行一次，避免過度頻繁的 API 請求
- 防抖動機制確保在 5 分鐘內不會重複觸發警報

## 授權

本專案為個人專案，僅供學習與研究使用。

