import threading,time,requests
from flask import Flask
app=Flask(__name__)
def send(m):
  try:
    t="coindcx-crypto-avais"
    h="https://ntfy.sh/"
    u=h+t
    requests.post(u,data=m.encode())
  except:
    pass
def loop():
  print("STARTED")
  send("Scanner Live!")
  while True:
    try:
      print("Scan")
      time.sleep(900)
    except:
      time.sleep(60)
threading.Thread(target=loop,daemon=True).start()
@app.route('/')
def home():
  return "OK"
if __name__=="__main__":
  app.run(host='0.0.0.0',port=10000)
