# 🔵 Smart Light - BUMP 聯動系統 (指揮官版)

這是一個專為 **BUMP** 打造的遠端連線系統。讓 BUMP 可以在自己的電腦上，透過一個網頁按鈕，瞬間控制全台灣所有安裝此軟體的電腦，讓大家的燈光同步變色並播放語音。

---

## 👨‍✈️ 給 BUMP 的操作指南 (免程式環境)

BUMP，你不需要開啟任何程式碼視窗，只需像平時上網一樣操作。

### 1. 如何打開控制台？
👉 **[進入 BUMP 專屬指揮部](https://mission-smart-light.onrender.com)**
使用 Chrome、Safari 或手機瀏覽器打開。

### 2. 登入與下令
- **登入**：輸入專屬金鑰 **`BUMP`**。
- **任務簡報**：在框中輸入你想對大家說的話。
- **發動 (ENGAGE)**：按下藍色大按鈕。全台燈具 1 秒內變藍並播放語音。
- **解散 (STAND DOWN)**：按下解除按鈕。恢復正常監控模式。

---

## 🚀 使用者端安裝 (安裝在電腦/燈泡端)

### 1. 取得開發專用序號
- **序號**: `DEV-8888`

### 2. 下載與安裝 (初次使用)
- **macOS**: 直接雙擊執行 `install_and_run.command`。
- **Windows**: 直接雙擊執行 `install_and_run.bat`。

### ⚡️ 日常啟動 (開機後使用)
對於完全不會程式的使用者，**開機後只需重複雙擊上述同一個檔案即可**。
- 腳本會自動偵測已安裝環境並執行，不會重複安裝。
- **懶人祕技**：建議將該檔案「製作成捷徑」放到**桌面**，以後開機點一下桌面圖示就能啟動監控。

### 3. 指向司令部 (必要步驟)
確保執行前已設定環境變數：
```bash
export MISSION_CONTROL_URL=https://mission-smart-light.onrender.com
python market_trade_alert_light.py
```

---

## 🛠 硬體需求
- **TP-Link Tapo 智慧彩光燈泡** (推薦型號：L530E)。
- **為什麼需要？**：為了透過實體燈光的顏色（藍、綠、紅、紫、黃）提供視覺化警報。智慧插座僅能控制開關，無法變色。
- **網路環境**：燈泡需與電腦連接在同一個 Wi-Fi 環境下。
- **預設 IP**：程式會嘗試自動掃描，亦可在設定頁面手動輸入。

---

## 🛠 開發者部署說明 (技術細節)

### 1. 雲端伺服器 (Render)
- **Repo**: 控制台代碼位於 `central_command_server.py`。
- **密鑰管理**: 請在 Render 後台或建立 `.env` 設定：
  - `ADMIN_KEY=BUMP`
  - `SECRET_KEY=隨機長字串`
- **追蹤連線**: [Render Dashboard](https://dashboard.render.com/web/srv-d57ur7ali9vc739o2pc0)

### 2. 防睡眠機制 (消除 30s 延遲)
利用 **[UptimeRobot](https://dashboard.uptimerobot.com/monitors)**。
- 每 10 分鐘「戳」一次網址：`https://mission-smart-light.onrender.com`
- 保持 24 小時清醒，確保 BUMP 隨叫隨到。

---

## 🎨 燈號邏輯與優先權

1. 🔵 **藍色**：司令部任務 (最高優先權，無視睡眠模式)。
2. 🟣 **紫色**：市場閃崩偵測。
3. 🔴 **紅色**：股價跌破停損。
4. 🟢 **綠色**：獲利目標達成。
5. 🟡 **黃色**：正常待機監控。

---

## 🧠 技術文件庫 (學習紀錄)

- [開發者設計精華日誌](./docs/technical/developer_design_log.md)：專案架構與硬體優化細節。
- [Render 部署指南](./docs/technical/render_deployment_notes.md)：關於免費版伺服器的運行與限制。
- [完整燈光指南](./docs/user_guide.md)：詳細的顏色定義與觸發條件。
