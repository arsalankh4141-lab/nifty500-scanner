import yfinance as yf, pandas as pd, time, requests
from datetime import datetime
from io import StringIO

def rsi(s,p=14):
    d=s.diff()
    g=d.where(d>0,0).ewm(alpha=1/p, adjust=False).mean()
    l=-d.where(d<0,0).ewm(alpha=1/p, adjust=False).mean()
    return 100-(100/(1+g/l))

def is_prd(df):
    try:
        df=df.tail(60).copy()
        df['RSI']=rsi(df['Close'])
        df=df.dropna()
        lows=[]
        for i in range(3,len(df)-3):
            if df['Low'].iloc[i] < df['Low'].iloc[i-1] and df['Low'].iloc[i] < df['Low'].iloc[i+1]:
                lows.append((float(df['Low'].iloc[i]), float(df['RSI'].iloc[i])))
        if len(lows)<2: return False, None
        p1,r1=lows[-2]; p2,r2=lows[-1]
        cond = (p2 < p1*0.998) and (r2 > r1) and (38 <= r2 <= 45)
        return cond, round(r2,2)
    except: return False, None

try
