import os
import subprocess
from dotenv import load_dotenv

# 加載 .env
load_dotenv()

class AutoUpdater:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.user = os.getenv("GITHUB_USER")
        self.repo = os.getenv("GITHUB_REPO")
        self.remote_url = f"https://{self.token}@github.com/{self.user}/{self.repo}.git"

    def check_for_updates(self):
        """檢查是否有新版本可用。"""
        if self.user == "YOUR_GITHUB_USERNAME":
            return False, "尚未設定 GitHub 帳號資訊"

        try:
            # 確保有遠端分支資訊
            subprocess.run(["git", "fetch", "origin"], check=True, capture_output=True)
            
            # 比較本地與遠端分支
            local_hash = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
            remote_hash = subprocess.check_output(["git", "rev-parse", "origin/main"]).decode().strip()
            
            if local_hash != remote_hash:
                return True, f"有新版本可用 (Remote: {remote_hash[:7]})"
            else:
                return False, "目前已是最新版本"
        except Exception as e:
            return False, f"檢查更新失敗: {str(e)}"

    def apply_update(self):
        """拉取最新程式碼並重啟系統。"""
        try:
            # 設定遠端 URL (包含 Token)
            subprocess.run(["git", "remote", "set-url", "origin", self.remote_url], check=True)
            
            # 強制拉取
            subprocess.run(["git", "pull", "origin", "main"], check=True, capture_output=True)
            
            return True, "更新成功！系統將在下次啟動時生效（或自動重啟中）。"
        except Exception as e:
            return False, f"嘗試更新時發生錯誤: {str(e)}"

    def setup_remote_if_missing(self):
        """如果沒有 origin，嘗試自動建立。"""
        if self.user == "YOUR_GITHUB_USERNAME":
            return
            
        try:
            subprocess.run(["git", "remote", "get-url", "origin"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print("正在設定 Git 遠端來源...")
            subprocess.run(["git", "remote", "add", "origin", self.remote_url], check=True)

if __name__ == "__main__":
    updater = AutoUpdater()
    has_update, msg = updater.check_for_updates()
    print(f"狀態: {msg}")
