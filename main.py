import threading,time,requests
from flask import Flask
import yfinance as yf
app=Flask(__name__)
TOPIC="coindcx-crypto-avais"
NTFY="https://ntfy.sh/"+TOPIC
def send(m):
  try:
    requests.post(
      NTFY,
      data=m.encode(),
      headers={"Title":"Alert"},
      timeout=15
    )
    print("Sent")
  except:
    pass
STOCKS=[
 "RELIANCE.NS","TCS.NS",
 "INFY.NS","HDFCBANK.NS",
 "ICICIBANK.NS","SBIN.NS"
]
CRYPTO=[
 "BTCUSDT","ETHUSDT",
 "SOLUSDT","BNBUSDT"
]
def scan_stocks():
  hits=[]
  for s in STOCKS:
    try:
      df=yf.download(
        s,period="2d",
        interval="15m",
        progress=False
      )
      if len(df)<20:
        continue
      last=df["Close"].iloc[-1]
      prev=df["High"].iloc[-20:-1].max()
      if last>prev:
        hits.append(s+" BO")
    except:
      pass
  return hits
def scan_crypto():
  hits=[]
  try:
    a="https://api.coindcx.com"
    b="/exchange/ticker"
    u=a+b
    r=requests.get(u,timeout=10).json()
    mp={}
    for x in r:
      try:
        mp[x["market"]]=x["last_price"]
      except:
        pass
    for c in CRYPTO:
      if c in mp:
        hits.append(c+" "+str(mp[c]))
  except:
    pass
  return hits[:5]
def loop():
  print("FULL STARTED")
  send("Full Scanner Live 15min")
  while True:
    try:
      print("Scan...")
      s=scan_stocks()
      c=scan_crypto()
      if s or c:
        m="STOCKS:\n"+"\n".join(s)
        m+="\n\nCRYPTO:\n"+"\n".join(c)
        send(m)
      time.sleep(900)
    except:
      time.sleep(60)
threading.Thread(
  target=loop,
  daemon=True
).start()
@app.route("/")
def home():
  return "Live"
if __name__=="__main__":
  app.run(
    host="0.0.0.0",
    port=10000
  )
