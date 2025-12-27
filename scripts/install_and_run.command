#!/bin/bash

# 取得腳本所在目錄並切換進去 (確保雙擊執行時路徑正確)
# 由於腳本被移動到了 scripts/ 資料夾，因此需要往上一層切換到專案根目錄
cd "$(dirname "$0")/.."

echo "=========================================="
echo "   MarketTradeAlertLight 自動安裝與啟動"
echo "=========================================="



# --- 環境檢查與安裝 ---

# 1. 檢查 Python
PYTHON_CMD="python3"
if command -v python3.13 &> /dev/null; then
    PYTHON_CMD="python3.13"
elif command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
elif command -v python3.10 &> /dev/null; then
    PYTHON_CMD="python3.10"
fi

if ! command -v $PYTHON_CMD &> /dev/null; then
    echo "❌ 錯誤: 未偵測到 Python3。請先安裝 Python (https://www.python.org/)"
    read -p "按任意鍵退出..."
    exit 1
fi
echo "使用 Python 版本: $($PYTHON_CMD --version)"

# 2. 建立虛擬環境 (若不存在)
if [ ! -d "venv" ]; then
    echo "📦 正在建立虛擬環境 (venv)..."
    $PYTHON_CMD -m venv venv
fi

# 3. 啟動並安裝依賴 (使用虛擬環境隔離，確保不影響系統其他設定)
echo "⬇️  正在檢查與安裝套件 (這可能會花一點時間)..."
source venv/bin/activate

# 升級 pip
pip install --upgrade pip > logs/install_log.txt 2>&1

# 安裝套件並記錄日誌
if pip install -r requirements.txt >> logs/install_log.txt 2>&1; then
    echo "✅ 套件安裝完成！環境配置成功。"
else
    echo "❌ 套件安裝失敗！"
    echo "請查看目錄下的 'install_log.txt' 了解詳細錯誤原因。"
    echo "常見原因：網路不穩、或是缺少系統開發工具 (xcode-select --install)"
    read -p "按任意鍵退出..."
    exit 1
fi


# 4. 啟動主程式
echo "🚀 啟動系統中..."
echo "------------------------------------------"
python market_trade_alert_light.py

# 結束處理
echo "應用程式已停止。"
read -p "按任意鍵關閉視窗..."
deactivate
