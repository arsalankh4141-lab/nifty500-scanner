import os, threading, time, requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import yfinance as yf
import pytz

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Scanner Live - 34 INDEX")

def start_server():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
threading.Thread(target=start_server, daemon=True).start()

NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "stock-hourly-15min-5min")
INDICES_34 = ["^NSEI","^NSEBANK","^CNXIT","^CNXAUTO","^CNXPHARMA","^CNXFMCG","^CNXMETAL","^CNXENERGY","^CNXINFRA","^CNXREALTY","^CNXMEDIA","^CNXPSUBANK","^CNXPVTBNK","^NIFTYMID50","^NIFTYSML100","^CNX100","^CNX200","^CNX500","^INDIAVIX","NIFTY_FIN_SERVICE.NS","NIFTY_MIDCAP_150.NS","NIFTY_SMALLCAP_250.NS","NIFTY_MIDSMALLCAP_400.NS","NIFTY100_LOWVOL30.NS","NIFTY50_EQUAL_WEIGHT.NS","NIFTY100_EQUAL_WEIGHT.NS","NIFTY500_MULTICAP_50_25_25.NS","NIFTY_LARGEMID250.NS","NIFTY_MIDSML400.NS","NIFTY200MOMENTM30.NS","NIFTY_MIDCAP_50.NS","NIFTY_SMALLCAP_50.NS","NIFTY_MIDCAP_100.NS","NIFTY500.NS"]

def send_ntfy(msg):
    try:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode('utf-8'), headers={"Title": "34 Index Scanner"}, timeout=10)
    except: pass

IST = pytz.timezone('Asia/Kolkata')
def is_market_open():
    now = datetime.now(IST)
    if now.weekday() >= 5: return False
    return 9 <= now.hour < 16

send_ntfy(f"Scanner ON - 34 INDEX FIXED - {len(INDICES_34)} Indices")
print(f"Scanner ON with {len(INDICES_34)} indices")

while True:
    try:
        if not is_market_open():
            time.sleep(60)
            continue
        for symbol in INDICES_34:
            try:
                df = yf.download(symbol, period="1d", interval="5m", progress=False, auto_adjust=True)
                if df.empty: continue
                print(f"{symbol}: scanned")
            except: pass
            time.sleep(1)
        time.sleep(300)
    except:
        time.sleep(60)
