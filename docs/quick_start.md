# 🚀 快速啟動指南 (Quick Start)

本專案分為「使用者端」與「司令部」兩個核心組件。

---

## 👨‍💻 1. 使用者端 (Client / Light End)
**用途**：安裝在個人電腦，負責監控股價、控制實體燈泡，並接收司令部指令。

### 啟動步驟：
1. **進入專案目錄**：
   ```bash
   cd smart_light_bump_version
   ```
2. **執行啟動程式**：
   - **方式 A (推薦)**：執行自動化腳本
     - macOS/Linux: `./scripts/install_and_run.command`
     - Windows: `scripts/install_and_run.bat`
   - **方式 B (手動)**：
     ```bash
     python3 main.py
     ```

---

## 👨‍✈️ 2. 司令部 (Commander / Bomber)
**用途**：集中控制中心，可下令全台燈具同步變色。

### A. 正式網頁版 (最簡單)
- **造訪網址**：[https://mission-smart-light.onrender.com](https://mission-smart-light.onrender.com)
- **登入序號**：`BUMP`

### B. 本地開發版 (開發者測試用)
- **執行命令**：
  ```bash
  python3 src/central_command_server.py
  ```
- **網址**：預設在 `http://127.0.0.1:5000`

---

## 🛠 其他說明庫
- [完整燈光顏色意義](./user_guide.md)
- [連線與設定疑難排解](./remoting_setup_guide.md)
- [開發者設計日誌](./technical/developer_design_log.md)
