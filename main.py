import yfinance as yf, requests, os, time

NTFY = os.getenv("NTFY_TOPIC", "stock-hourly-15min-5min")

def rsi(tkr, per, inter):
    try:
        df = yf.download(tkr, period=per, interval=inter, progress=False, auto_adjust=True, timeout=10)
        if df is None or len(df) < 20: return 0
        if 'Close' not in df: return 0
        close = df['Close']
        # agar multi-index aaye to handle
        if hasattr(close, 'iloc'):
            if len(close.shape) > 1:
                close = close.iloc[:,0]
        d = close.diff()
        g = d.where(d > 0, 0).ewm(alpha=1/14, min_periods=14).mean()
        l = -d.where(d < 0, 0).ewm(alpha=1/14, min_periods=14).mean()
        rs = g / l
        rsi_val = 100 - (100 / (1 + rs))
        return float(rsi_val.iloc[-1])
    except Exception as e:
        print(f"RSI Error {tkr}: {e}")
        return 0

def send(msg):
    try:
        requests.post(f"https://ntfy.sh/{NTFY}", data=msg.encode(), headers={"Title":"Scanner 34 Index"}, timeout=10)
    except: pass

INDICES = ["^NSEI","^NSEBANK","^CNXAUTO","^CNXIT","^CNXFMCG","^CNXPHARMA","^CNXMETAL","^CNXREALTY","^CNXMEDIA","^CNXFINANCE","^CNXPSUBANK","^CNXPVTBANK","^CNXENERGY","^CNXINFRA","^CNXPSE","^CNXCONSUMDUR","^CNXHEALTH","^CNXOILGAS","^CNXCONSUMPTION","^CNXSERVICE","^CNX100","^CNX200","^CNX500"]

STOCKS = ["RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS","SBIN.NS","BHARTIARTL.NS","LT.NS","ITC.NS","KOTAKBANK.NS","AXISBANK.NS","MARUTI.NS","WIPRO.NS","SUNPHARMA.NS","TITAN.NS","TATAMOTORS.NS","M&M.NS","HCLTECH.NS","JSWSTEEL.NS","HINDALCO.NS"]

print("START 34 INDEX SCAN")
send("Scanner ON - 34 INDEX FIXED - Loop Active")

# Yahi loop tha jo missing tha isliye Failed deploy aaya
while True:
    try:
        for idx in INDICES:
            rm = rsi(idx,"5y","1mo"); rw = rsi(idx,"2y","1wk"); rd = rsi(idx,"1y","1d")
            print(f"{idx} M:{rm:.0f} W:{rw:.0f} D:{rd:.0f}")
            if rm>60 and rw>60 and rd>60:
                print(f"PASS {idx}")
                for st in STOCKS:
                    sm=rsi(st,"5y","1mo"); sw=rsi(st,"2y","1wk")
                    if sm>60 and sw>60:
                        sh=rsi(st,"3mo","60m"); s15=rsi(st,"60d","15m")
                        if sh>60 and s15>60:
                            msg=f"🔥 {st} | {idx} | M:{sm:.0f} W:{sw:.0f} H:{sh:.0f} 15:{s15:.0f}"
                            print(msg); send(msg)
            time.sleep(1)
        print("Cycle complete, sleeping 15 min...")
        time.sleep(900) # 15 min wait
    except Exception as e:
        print(f"Loop Error: {e}")
        time.sleep(60)
