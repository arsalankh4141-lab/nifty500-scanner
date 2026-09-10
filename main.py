import threading
import time
import requests
from flask import Flask

app = Flask(__name__)
TOPIC = "coindcx-crypto-avais"
NTFY_URL = "https://ntfy.sh/" + TOPIC

def send(msg):
    try:
        requests.post(NTFY_URL, data=msg.encode(), headers={"Title": "Scanner"}, timeout=15)
        print("Sent:", msg)
    except Exception as e:
        print("Send fail:", e)

STOCKS = ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","SBIN.NS"]
CRYPTO = ["BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT"]

def scan_loop():
    print("FULL STARTED")
    time.sleep(5)
    send("Full Scanner Live! 15min - Avais")
    while True:
        try:
            print("Scanning...")
            # Simple crypto price check
            hits = []
            try:
                base = "https://api.coindcx.com"
                end = "/exchange/ticker"
                url = base + end
                r = requests.get(url, timeout=10).json()
                mp = {}
                for x in r:
                    try:
                        mp[x["market"]] = x["last_price"]
                    except:
                        pass
                for c in CRYPTO:
                    if c in mp:
                        hits.append(c + " " + str(mp[c]))
            except Exception as e:
                print("Crypto err", e)

            if hits:
                msg = "CRYPTO UPDATE:\n" + "\n".join(hits[:5])
                send(msg)

            time.sleep(900)
        except Exception as e:
            print("Loop err", e)
            time.sleep(60)

threading.Thread(target=scan_loop, daemon=True).start()

@app.route("/")
def home():
    return "Live - Avais Scanner Running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
