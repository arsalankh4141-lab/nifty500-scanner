import yfinance as yf
import pandas as pd
import time, requests
from datetime import datetime
from io import StringIO

def rsi(s,p=14):
    d=s.diff()
    g=d.where(d>0,0).ewm(
      alpha=1/p,adjust=False).mean()
    l=-d.where(d<0,0).ewm(
      alpha=1/p,adjust=False).mean()
    return 100-(100/(1+g/l))

def is_prd(df):
    try:
        df=df.tail(60).copy()
        df['RSI']=rsi(df['Close'])
        df=df.dropna()
        lows=[]
        for i in range(3,len(df)-3):
            if df['Low'].iloc[i] < df['Low'].iloc[i-1]:
                if df['Low'].iloc[i] < df['Low'].iloc[i+1]:
                    lows.append((
                      float(df['Low'].iloc[i]),
                      float(df['RSI'].iloc[i])))
        if len(lows)<2:
            return False,None
        p1,r1=lows[-2]
        p2,r2=lows[-1]
        cond=(p2 < p1*0.998) and (r2>r1)
        cond=cond and (38<=r2<=45)
        return cond,round(r2,2)
    except:
        return False,None

try:
    hdr={"User-Agent":"Mozilla/5.0"}
    url="https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
    txt=requests.get(url,headers=hdr,timeout=15).text
    nifty=pd.read_csv(StringIO(txt))
    STOCKS=[f"{s.strip()}.NS" for s in nifty['Symbol']]
except:
    fb=["RELIANCE","TCS","INFY","HDFCBANK",
        "ICICIBANK","SBIN","BHARTIARTL","ITC"]
    STOCKS=[f"{s}.NS" for s in fb]

result=[]
date_str=datetime.now().strftime('%d-%m-%Y')

for s in STOCKS:
    try:
        d=yf.download(s,period="1y",
          interval="1d",progress=False,
          auto_adjust=True)
        if len(d)<60:
            continue
        ok,rv=is_prd(d)
        if not ok:
            time.sleep(0.1)
            continue
        w=yf.download(s,period="2y",
          interval="1wk",progress=False,
          auto_adjust=True)
        m=yf.download(s,period="5y",
          interval="1mo",progress=False,
          auto_adjust=True)
        if len(w)<10 or len(m)<10:
            continue
        wr=rsi(w['Close']).iloc[-1]
        mr=rsi(m['Close']).iloc[-1]
        if wr>60 and mr>60:
            result.append({
              "Stock":s.replace(".NS",""),
              "Daily RSI":rv,
              "W RSI":round(float(wr),1),
              "M RSI":round(float(mr),1)})
    except:
        pass
    time.sleep(0.15)

if result:
    df_out=pd.DataFrame(result)
else:
    df_out=pd.DataFrame([{
      "Stock":"No PRD Today",
      "Daily RSI":0,"W RSI":0,"M RSI":0}])

df_out.to_excel(
  f"PRD_Nifty500_{date_str}.xlsx",
  index=False)
df_out.to_csv(
  f"PRD_Nifty500_{date_str}.csv",
  index=False)

with open("result.txt","w") as f:
    f.write(f"Date: {date_str}\n")
    f.write(f"Total: {len(result)}\n")
