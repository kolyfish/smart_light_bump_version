import threading

class SharedConfig:
    def __init__(self, default_symbol="BTC-USD", default_target=88000.0, default_stop_loss=0.0):
        self._symbol = default_symbol
        self._target_price = default_target
        self._stop_loss_price = default_stop_loss
        self._lock = threading.Lock()

    @property
    def symbol(self):
        with self._lock:
            return self._symbol

    @symbol.setter
    def symbol(self, value):
        with self._lock:
            self._symbol = value.strip().upper()

    @property
    def target_price(self):
        with self._lock:
            return self._target_price

    @target_price.setter
    def target_price(self, value):
        with self._lock:
            try:
                self._target_price = float(value)
            except ValueError:
                print(f"Invalid target price: {value}. Ignoring.")

    def get_config(self):
        with self._lock:
            return {
                "symbol": self._symbol,
                "target_price": self._target_price,
                "stop_loss_price": self._stop_loss_price
            }

    def update_config(self, symbol, target_price, stop_loss_price=None):
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
