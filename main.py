import threading,time,requests,datetime
from flask import Flask
app=Flask(__name__)
TOPIC="coindcx-crypto-avais"
def send(m):
  try:
    url="https://ntfy.sh/"+TOPIC
    requests.post(url,data=m.encode())
    print("Sent")
  except Exception as e:
    print(e)
def loop():
  print("SCANNER STARTED")
  send("Scanner Live! Ab 15min me scan hoga")
  while True:
    try:
      n=datetime.datetime.now()
          print("Scan running...")
      print("Crypto scanning...")
      time.sleep(900)
    except Exception as e:
      print(f"Err {e}")
      time.sleep(60)
threading.Thread(target=loop,daemon=True).start()
@app.route('/')
def home():
  return "Scanner Running OK"
if __name__=="__main__":
  app.run(host='0.0.0.0',port=10000)
