import os, threading, time, requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import yfinance as yf
import pytz

# --- ALAG-ALAG TOPIC ---
STOCK_TOPIC = "stock-hourly-15min-5min"
CRYPTO_TOPIC = "coindcx-crypto-avais"
IST = pytz.timezone('Asia/Kolkata')

def send_ntfy(topic, title, msg):
    try:
        requests.post(
            f"https://ntfy.sh/{topic}",
            data=msg.encode('utf-8'),
            headers={"Title": title, "Priority": "high", "Tags": "rocket"},
            timeout=10
        )
        print(f"[{topic}] {title}")
    except Exception as e:
        print(f"NTFY Error: {e}")

# --- RENDER KE LIYE SERVER ---
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Scanner Live - Stock + Crypto")

def start_server():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()

threading.Thread(target=start_server, daemon=True).start()

# --- STOCK MARKET TIME CHECK ---
def is_stock_open():
    now = datetime.now(IST)
    if now.weekday() >= 5: # Saturday, Sunday
        return False
    if now.hour < 9 or now.hour > 15:
        return False
    if now.hour == 9 and now.minute < 15:
        return False
    if now.hour == 15 and now.minute > 35:
        return False
    return True

# --- 1. STOCK SCANNER ---
def scan_stocks():
    stocks = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "BHARTIARTL.NS"]
    for sym in stocks:
        try:
            df = yf.download(sym, period="2d", interval="15m", progress=False, auto_adjust=True)
            if len(df) < 20:
                continue
            last_close = float(df['Close'].iloc[-1])
            prev_high = float(df['High'].iloc[-21:-1].max())
            if last_close > prev_high:
                send_ntfy(STOCK_TOPIC, f"{sym} Breakout", f"{sym} 15MIN High Break!\nPrice: {last_close:.2f}\nPrev High: {prev_high:.2f}")
            time.sleep(0.5)
        except:
            continue

# --- 2. CRYPTO SCANNER ---
def scan_crypto():
    coins = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "DOGEUSDT", "SHIBUSDT"]
    for coin in coins:
        try:
            url = f"https://public.coindcx.com/market_data/candles?pair=I-{coin}&interval=5m&limit=20"
            r = requests.get(url, timeout=10).json()
            if not r or len(r) < 10:
                continue
            last_close = float(r[-1][4])
            prev_high = max([float(c[2]) for c in r[:-1]])
            if last_close > prev_high:
                send_ntfy(CRYPTO_TOPIC, f"{coin} 5MIN Breakout", f"{coin} 5MIN High Break!\nPrice: {last_close}\nPrev High: {prev_high}\nTime: {datetime.now(IST).strftime('%I:%M %p')}")
            time.sleep(0.5)
        except Exception as e:
            print(f"Crypto Error {coin}: {e}")
            continue

# --- MAIN LOOP DONO EK SATH ---
print("Scanner Started...")
while True:
    try:
        now_str = datetime.now(IST).strftime('%d-%m %H:%M:%S')
        print(f"Checking at {now_str}")
        scan_crypto() # Crypto hamesha chalega

        if is_stock_open():
            print("Market OPEN - Scanning Stocks")
            scan_stocks()
        else:
            print("Market CLOSED - Only Crypto")

        time.sleep(300) # Har 5 min
    except Exception as e:
        print(f"Loop Error: {e}")
        time.sleep(60)
