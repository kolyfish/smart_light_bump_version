# 💻 如何在別人的電腦安裝 Smart Light Client

如果您要幫新夥伴安裝燈光聯動系統，請按照以下極簡流程製作。

---

## 📦 準備安裝包
最快的方式是將整個專案打包，或是只帶走核心檔案：
1. **必要檔案**：
   - `shared_config.py`, `tapo_controller.py`, `stock_monitor.py`
   - `mission_listener.py`, `web_server.py`, `market_trade_alert_light.py`
   - `license_manager.py`, `tapo_scanner.py`
   - `requirements.txt`
   - `scripts/install_and_run.command` (Mac) 或 `scripts/install_and_run.bat` (Windows)

---

## 🚀 安裝三步驟 (Mac)

1. **解壓縮**：將安裝包放到使用者的桌面或隨便一個資料夾。
2. **賦予權限**：如果是第一次在該電腦執行 .command 檔，系統可能會擋。
   - 右鍵點擊 `install_and_run.command` -> 「打開」。
   - 如果還是不行，開啟終端機輸入：`chmod +x [檔案路徑]`。
3. **一鍵啟動**：雙擊 `install_and_run.command`。
   - 程式會自動安裝虛擬環境與 Python 套件。
   - 安裝完成後會彈出一個 GUI 視窗並顯示 QR Code。

---

## 🚀 安裝三步驟 (Windows)

1. **安裝 Python**：確保電腦有安裝 Python 3.10+。
2. **啟動**：雙擊 `scripts/install_and_run.bat`。
3. **防火牆**：初次啟動如果跳出「 Windows 防火牆」提示，請務必點選**「允許存取」**，否則網頁控制台會連不上。

---

## ⚙️ 初始設定 (必做)
啟動後，使用手機掃描螢幕上的 **QR Code**：
1. 輸入該電腦所在環境的 **Tapo 帳號/密碼**。
2. 輸入 **Tapo 燈泡的 IP** (如果不知道，可以點擊掃描)。
3. 按下 **儲存並測試監控**。
4. **確認看板**：如果看到燈泡亮起黃色（或很暗的黃色），代表聯動成功！

---

## 🔵 測試連線
安裝完後，您可以請 BUMP 在中央控制台按一下 **ENGAGE**，確認該電腦的燈泡是否在一秒內同步變藍！
