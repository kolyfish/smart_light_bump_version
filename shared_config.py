import threading
import json
import os

class SharedConfig:
    def __init__(self, default_symbol="BTC-USD", default_target=88000.0, default_stop_loss=0.0):
        self._config_file = "config.json"
        self._symbol = default_symbol
        self._target_price = default_target
        self._stop_loss_price = default_stop_loss
        self._tapo_email = ""
        self._tapo_password = ""
        self._tapo_ip = "192.168.100.150" # Default for current user
        self._lock = threading.Lock()
        self._load_config() # 嘗試讀取存檔

    def _load_config(self):
        """從檔案讀取設定"""
        if os.path.exists(self._config_file):
            try:
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._symbol = data.get("symbol", self._symbol)
                    self._target_price = data.get("target_price", self._target_price)
                    self._stop_loss_price = data.get("stop_loss_price", self._stop_loss_price)
                    self._tapo_email = data.get("tapo_email", "")
                    self._tapo_password = data.get("tapo_password", "")
                    self._tapo_ip = data.get("tapo_ip", self._tapo_ip)
                    print(f"✅ 已讀取設定檔: {self._symbol}, 目標 {self._target_price}")
            except Exception as e:
                print(f"⚠️ 讀取設定檔失敗: {e}")

    def _save_config(self):
        """寫入設定到檔案"""
        data = {
            "symbol": self._symbol,
            "target_price": self._target_price,
            "stop_loss_price": self._stop_loss_price,
            "tapo_email": self._tapo_email,
            "tapo_password": self._tapo_password,
            "tapo_ip": self._tapo_ip
        }
        try:
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"❌ 儲存設定檔失敗: {e}")

    @property
    def symbol(self):
        with self._lock:
            return self._symbol

    @symbol.setter
    def symbol(self, value):
        with self._lock:
            self._symbol = value.strip().upper()
            self._save_config()

    @property
    def target_price(self):
        with self._lock:
            return self._target_price

    @target_price.setter
    def target_price(self, value):
        with self._lock:
            try:
                self._target_price = float(value)
                self._save_config()
            except ValueError:
                print(f"Invalid target price: {value}. Ignoring.")

    @property
    def tapo_email(self):
        with self._lock:
            return self._tapo_email

    @property
    def tapo_password(self):
        with self._lock:
            return self._tapo_password

    @property
    def tapo_ip(self):
        with self._lock:
            return self._tapo_ip

    def get_config(self):
        with self._lock:
            return {
                "symbol": self._symbol,
                "target_price": self._target_price,
                "stop_loss_price": self._stop_loss_price,
                "tapo_email": self._tapo_email,
                "tapo_ip": self._tapo_ip,
                # 為了安全，不回傳密碼到前端，或者只回傳是否有設定
                "tapo_password_set": bool(self._tapo_password)
            }

    def update_config(self, symbol, target_price, stop_loss_price=None, tapo_email=None, tapo_password=None, tapo_ip=None):
        with self._lock:
            if symbol:
                self._symbol = symbol.strip().upper()
            if target_price is not None:
                try:
                    self._target_price = float(target_price)
                except ValueError:
                    pass
            if stop_loss_price is not None:
                try:
                    self._stop_loss_price = float(stop_loss_price)
                except ValueError:
                    pass
            
            if tapo_email is not None:
                self._tapo_email = tapo_email.strip()
            
            if tapo_ip is not None:
                self._tapo_ip = tapo_ip.strip()
            
            # 只有當密碼不為空時才更新 (避免前端送空字串覆蓋掉舊密碼)
            if tapo_password and tapo_password.strip():
                self._tapo_password = tapo_password.strip()

            self._save_config()
