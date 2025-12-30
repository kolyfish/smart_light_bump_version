# 🛠️ Smart Light 系統維護手冊

這份文件提供給技術負責人，用於確保「中央司令部」與「終端設備」穩定運行的日常檢查與設定。

---

## 1. 中央司令部 (Render) 維護

### 🔑 修改管理金鑰 (ADMIN_KEY)
如果您覺得 `BUMP` 這個密鑰已洩漏，請按以下步驟修改：
1. 進入 [Render Dashboard](https://dashboard.render.com/)。
2. 找到您的 Service 並進入 **Environment** 選項。
3. 修改 `ADMIN_KEY` 的值並儲存。
4. Render 會自動重啟服務，新金鑰立即生效。

### 📡 檢查伺服器狀態
- **狀態網址**：`https://mission-smart-light.onrender.com/status`
- **觀察數據**：查看 `last_update` 是否正常更新。

### 🛏️ 睡眠問題排查
如果發生「首開網頁需等待 30 秒」的情況：
- 檢查 [UptimeRobot](https://dashboard.uptimerobot.com/monitors) 是否仍在正常「戳」您的 URL。
- 確認全台灣是否至少有一台電腦正在跑 `market_trade_alert_light.py`。

---

## 2. 終端設備 (使用者電腦) 維護

### 📝 查看日誌 (Logs)
程式運行期間的所有重要資訊會記錄在：
- **運行日誌**：`monitor.log` (包含股市更新、指令接收、燈泡連線)
- **安裝日誌**：`logs/install_log.txt` (如果環境裝不起來，請看這)

### 🚨 常見故障排除

| 現象 | 可能原因 | 解決方法 |
| :--- | :--- | :--- |
| **燈泡沒反應** | IP 變動、密碼錯誤、Wi-Fi 不同網段 | 手動掃描 QR Code 進入設定頁面重新設定 Tapo 資訊。 |
| **語音沒聲音** | 系統音量過低、或是 Python `pyttsx3` 損毀 | 檢查電腦音量，程式會自動嘗試呼叫系統原生 `say` 指令作為後備。 |
| **沒接收到藍燈** | 網路斷線、或是偵測到 `OFFLINE` | 重新啟動程式，檢查 `MISSION_CONTROL_URL` 是否正確。 |

---

## 3. 重要安全性提醒
- **不要把 `.env` 或 `.license_key` 上傳到公開 Repo**。
- **定期備份 `config.json`**，這是使用者的燈泡連線記憶。
