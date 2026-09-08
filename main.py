from flask import Flask
import yfinance as yf, time, datetime, pytz, threading, urllib.request, os, pandas as pd
app=Flask(__name__)
TOPIC=os.environ.get("NTFY_TOPIC","stock-hourly-15min-5min")
IST=pytz.timezone('Asia/Kolkata')
def send_ntfy(t,m):
 try: urllib.request.urlopen(urllib.request.Request(f"https://ntfy.sh/{TOPIC}",data=m.encode(),method='POST',headers={"Title":t}),timeout=10)
 except: pass
def is_market_open():
 n=datetime.datetime.now(IST); return n.weekday()<5 and datetime.time(9,15) <= n.time() <= datetime.time(15,30)
def rsi(s,p=14):
 d=s.diff(); g=d.clip(lower=0); l=-d.clip(upper=0); ag=g.ewm(com=p-1,adjust=False).mean(); al=l.ewm(com=p-1,adjust=False).mean(); return 100-(100/(1+ag/al))
def get_rsi(sym,i,p):
 try:
  df=yf.download(sym,period=p,interval=i,progress=False,auto_adjust=True)
  if len(df)<35: return None
  return float(rsi(df['Close']).iloc[-1])
 except: return None
def load_all():
 s=set()
 urls=["https://archives.nseindia.com/content/indices/ind_nifty500list.csv","https://archives.nseindia.com/content/indices/ind_niftyautolist.csv","https://archives.nseindia.com/content/indices/ind_niftybanklist.csv","https://archives.nseindia.com/content/indices/ind_niftyitlist.csv","https://archives.nseindia.com/content/indices/ind_niftypharmalist.csv","https://archives.nseindia.com/content/indices/ind_niftymetallist.csv","https://archives.nseindia.com/content/indices/ind_niftyinfralist.csv","https://archives.nseindia.com/content/indices/ind_niftyfinancelist.csv","https://archives.nseindia.com/content/indices/ind_niftyindiadefencelist.csv"]
 for u in urls:
  try:
   df=pd.read_csv(u); s.update([f"{x.strip()}.NS" for x in df['Symbol']])
  except: pass
 s.update(["HAL.NS","BEL.NS","BDL.NS","MAZDOCK.NS"])
 return list(s)
ALL=load_all()
def scan_one(sym):
 try:
  m=get_rsi(sym,"1mo","10y"); w=get_rsi(sym,"1wk","5y")
  if not(m and w and m>60 and w>60): return None
  h=get_rsi(sym,"1h","1y"); f15=get_rsi(sym,"15m","60d")
  if not(h and f15 and h>60 and f15>60): return None
  f5=get_rsi(sym,"5m","5d")
  if not(f5 and 38<=f5<=50): return None
  send_ntfy(f"{sym} FOUND",f"{sym} M:{m:.1f} W:{w:.1f} H:{h:.1f} 15M:{f15:.1f} 5M:{f5:.1f} Total:{len(ALL)}")
 except: pass
def loop():
 send_ntfy("Scanner ON",f"{len(ALL)} Stocks - Nifty500+8 Index")
 from concurrent.futures import ThreadPoolExecutor
 while True:
  if not is_market_open(): time.sleep(300); continue
  with ThreadPoolExecutor(max_workers=15) as ex: list(ex.map(scan_one,ALL))
  time.sleep(300)
threading.Thread(target=loop,daemon=True).start()
@app.route('/')
def home(): return f"Total {len(ALL)} Stocks Scanning - {datetime.datetime.now(IST)}"
if __name__=="__main__": app.run(host='0.0.0.0',port=int(os.environ.get("PORT",10000)))
