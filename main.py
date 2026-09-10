import requests, threading, time
from flask import Flask

app = Flask(__name__)
TOPIC = "coindcx-crypto-avais"
NTFY_URL = f"https://ntfy.sh/{TOPIC}"

def send(msg):
    try:
        requests.post(NTFY_URL, data=msg.encode('utf-8'), headers={"Title": "Avais Scanner"}, timeout=20)
        print(f"SENT: {msg}")
    except Exception as e:
        print(f"FAILED: {e}")

def scanner():
    print("FULL STARTED")
    time.sleep(3)
    send("✅ FINAL LIVE! Scanner Start Ho Gaya Avais - 15min Active")
    while True:
        try:
            r = requests.get("https://api.coindcx.com/exchange/ticker", timeout=15).json()
            prices = {x['market']: x['last_price'] for x in r if 'market' in x}
            btc = prices.get('BTCUSDT','N/A')
            eth = prices.get('ETHUSDT','N/A')
            sol = prices.get('SOLUSDT','N/A')
            msg = f"📊 15min Update\nBTC: {btc}\nETH: {eth}\nSOL: {sol}\nTime: {time.strftime('%I:%M %p')}"
            send(msg)
        except Exception as e:
            print(f"Scan Error: {e}")
        time.sleep(900) # 15 min

# Background start
threading.Thread(target=scanner, daemon=True).start()

@app.route("/")
def home():
    # Page khulte hi turant NTFY bhejega - isse guarantee hai
    send(f"🔔 Wakeup! Tumne site khola - Scanner LIVE hai {time.strftime('%I:%M:%S %p')}")
    return "Live - Avais Scanner Running - FINAL"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
