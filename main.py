import os, threading, time, requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import yfinance as yf
import pytz

# --- 1. RENDER PORT FIX (Isse Timed Out nahi hoga) ---
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Scanner Live - 34 INDEX")

def start_server():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()

threading.Thread(target=start_server, daemon=True).start()
print("Port server started...")

# --- 2. SCANNER CONFIG ---
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "stock-hourly-15min-5min")
# 34 NSE Indices
INDICES = [
    "^NSEI", "^NSEBANK", "^CNXIT", "^CNXAUTO", "^CNXPHARMA", "^CNXFMCG",
    "^CNXMETAL", "^CNXENERGY", "^CNXINFRA", "^CNXREALTY", "^CNXMEDIA",
    "^CNXPSUBANK", "^CNXPVTBNK", "^NIFTYMID50", "^NIFTYSML100", "^CNX100",
    "^CNX200", "^CNX500", "^INDIAVIX", "NIFTY_FIN_SERVICE.NS", "NIFTY_MIDCAP_150.NS",
    "NIFTY_SMALLCAP_250.NS", "NIFTY_MIDSMALLCAP_400.NS", "NIFTY100_LOWVOL30.NS",
    "NIFTY50_EQUAL_WEIGHT.NS", "NIFTY100_EQUAL_WEIGHT.NS", "NIFTY500_MULTICAP_50_25_25.NS",
    "NIFTY_LARGEMID250.NS", "NIFTY_MIDSML400.NS", "NIFTY200MOMENTM30.NS",
    "NIFTY_MIDCAP_50.NS", "NIFTY_SMALLCAP_50.NS", "NIFTY_MIDCAP_100.NS", "NIFTY500.NS"
]

def send_ntfy(msg):
    try:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode('utf-8'), headers={"Title": "Nifty Scanner"}, timeout=10)
        print(f"Sent: {msg}")
    except Exception as e:
        print(f"NTFY Error: {e}")

IST = pytz.timezone('Asia/Kolkata')

def is_market_open():
    now = datetime.now(IST)
    if now.weekday() >= 5: return False # Sat/Sun
    return 9 <= now.hour < 16 # 9 AM to 4 PM buffer

send_ntfy("Scanner ON - 34 INDEX FIXED - Render Live")

# --- 3. MAIN LOOP ---
while True:
    try:
        if not is_market_open():
            print(f"Market Closed - Sleeping... {datetime.now(IST)}")
            time.sleep(60)
            continue

        print(f"Scanning {len(INDICES)} indices... {datetime.now(IST)}")
        for symbol in INDICES:
            try:
                df = yf.download(symbol, period="1d", interval="5m", progress=False)
                if df.empty: continue
                # Simple example: High breakout logic
                last_close = float(df['Close'].iloc[-1])
                day_high = float(df['High'].max())
                # Add your 15min/5min logic here
                print(f"{symbol}: {last_close}")
            except Exception as e:
                print(f"Error {symbol}: {e}")
            time.sleep(1) # yfinance rate limit se bachne ke liye

        print("Scan done, waiting 5 min...")
        time.sleep(300) # 5 min

    except Exception as e:
        print(f"Loop Error: {e}")
        time.sleep(60)
