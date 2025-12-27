# Smart Light Bump Version 🔵

這是 **BUMP 特別版** 的智慧燈控軟體。
與原本的股票監控版本不同，這個版本增加了「中央任務控制」功能。

## 特色功能

1. **中央司令部聯動**：
   - 所有的客戶端都會監聽中央伺服器的指令。
   - 當中央下達 `mission` 指令時，全台灣的燈具都會**同步變成藍色**。

2. **優先權邏輯**：
   - **最高優先級**：中央指令 (藍燈 / 任務模式)
   - 次要優先級：股票閃崩 (紫燈)
   - 次要優先級：停損警報 (紅燈)
   - 次要優先級：獲利達標 (綠燈)
   - 一般狀態：黃燈監控中

## 檔案結構

- `mission_listener.py`: 客戶端監聽器，負責與中央伺服器溝通。
- `central_command_server.py`: 中央伺服器 (範例)，您需要將其部署在雲端。
- `mission_monitor.py`: 修改後的監控核心，整合了任務監聽邏輯。

## 如何執行

1. **啟動中央伺服器 (Commander)**:
   ```bash
   python central_command_server.py
   ```

2. **啟動客戶端 (Soldier)**:
   由於此版本依賴原本的 `market_trade_alert_light` 核心代碼，請確保環境變數正確。
   目前尚未提供獨立的 GUI 入口，您可以在代碼中引用 `MissionMonitor` 來取代原本的 `StockMonitor`。

## 下達指令 (給指揮官)

使用 Postman 或 curl 發送指令：

```bash
curl -X POST http://YOUR_SERVER_IP:5000/admin/command \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer BUMP_VERSION_SUPER_SECRET_KEY" \
     -d '{"mode": "mission", "color": "blue"}'
```

解除任務：
```bash
curl -X POST http://YOUR_SERVER_IP:5000/admin/command \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer BUMP_VERSION_SUPER_SECRET_KEY" \
     -d '{"mode": "normal"}'
```
