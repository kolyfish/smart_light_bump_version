import yfinance as yf

def test_fetch():
    symbols = ["2330.TW", "^TWII"]
    for s in symbols:
        print(f"Testing {s}...")
        try:
            ticker = yf.Ticker(s)
            # Try fast_info
            print(f"Fast Info Price: {ticker.fast_info.get('last_price')}")
            # Try history
            hist = ticker.history(period="1d")
            if not hist.empty:
                print(f"History Price: {hist['Close'].iloc[-1]}")
            else:
                print("History is empty")
        except Exception as e:
            print(f"Error fetching {s}: {e}")

if __name__ == "__main__":
    test_fetch()
