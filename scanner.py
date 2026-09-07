import yfinance as yf, pandas as pd, time
from datetime import datetime

def rsi(s,p=14):
    d=s.diff(); g=d.where(d>0,0).ewm(alpha=1/p, adjust=False).mean(); l=-d.where(d<0,0).ewm(alpha=1/p, adjust=False).mean(); return 100-(100/(1+g/l))
def is_prd(df):
    try:
        df=df.tail(60).copy(); df['RSI']=rsi(df['Close']); df=df.dropna(); lows=[]
        for i in range(3,len(df)-3):
            if df['Low'].iloc[i] < df['Low'].iloc[i-1] and df['Low'].iloc[i] < df['Low'].iloc[i+1]: lows.append((df['Low'].iloc[i], df['RSI'].iloc[i]))
        if len(lows)<2: return False
        p1,r1=lows[-2]; p2,r2=lows[-1]; return (p2 < p1*0.998) and (r2 > r1) and (38 <= r2 <= 45)
    except: return False

nifty=pd.read_csv("https://archives.nseindia.com/content/indices/ind_nifty500list.csv")
STOCKS=[f"{s.strip()}.NS" for s in nifty['Symbol'].tolist()]
result=[]
for s in STOCKS:
    try:
        d=yf.download(s, period="1y", interval="1d", progress=False, auto_adjust=True)
        w=yf.download(s, period="2y", interval="1wk", progress=False, auto_adjust=True)
        m=yf.download(s, period="5y", interval="1mo", progress=False, auto_adjust=True)
        if len(d)<50: continue
        if rsi(w['Close']).iloc[-1]>60 and rsi(m['Close']).iloc[-1]>60 and is_prd(d):
            result.append(s.replace(".NS",""))
    except: pass
    time.sleep(0.2)

pd.DataFrame(result, columns=["Stock"]).to_csv(f"PRD_Nifty500_{datetime.now().strftime('%d-%m-%Y')}.csv", index=False)
pd.DataFrame(result, columns=["Stock"]).to_excel(f"PRD_Nifty500_{datetime.now().strftime('%d-%m-%Y')}.xlsx", index=False)
with open("result.txt","w") as f:
    f.write(f"Date: {datetime.now().strftime('%d-%m-%Y')}\nTotal: {len(result)}\n\n" + "\n".join(result))
