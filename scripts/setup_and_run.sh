#!/bin/bash

# SmartStockLight 一鍵安裝與執行腳本
# 適用於 macOS

# 切換到專案根目錄
cd "$(dirname "$0")/.."

echo "------------------------------------------"
echo "   SmartStockLight 啟動中..."
echo "------------------------------------------"

# 1. 檢查 Python 是否安裝
PYTHON_CMD="python3"
if command -v python3.13 &> /dev/null; then
    PYTHON_CMD="python3.13"
elif command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
elif command -v python3.10 &> /dev/null; then
    PYTHON_CMD="python3.10"
fi

echo "使用 Python 版本: $($PYTHON_CMD --version)"

if ! command -v $PYTHON_CMD &> /dev/null
then
    echo "錯誤: 未偵測到 Python3。請先安裝 Python (https://www.python.org/)"
    exit 1
fi

# 2. 建立虛擬環境 (若不存在)
if [ ! -d "venv" ]; then
    echo "正在建立虛擬環境 (venv)..."
    $PYTHON_CMD -m venv venv
fi

# 3. 啟動虛擬環境並安裝依賴
echo "正在安裝/更新必要套件..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 4. 啟動主程式
echo "啟動伺服器與監控系統..."
python market_trade_alert_light.py

# 結束後離開點
deactivate
