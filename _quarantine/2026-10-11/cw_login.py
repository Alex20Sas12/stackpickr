import json, time, urllib.request, websocket
def tab(url):
    req = urllib.request.Request("http://localhost:9232/json/new?" + url, method="PUT")
    return json.loads(urllib.request.urlopen(req, timeout=10).read())
t = tab("https://unified.cloudways.com/login"); time.sleep(6)
ws = websocket.create_connection(t["webSocketDebuggerUrl"], timeout=30)
n=[0]
def send(m,p=None):
    n[0]+=1; ws.send(json.dumps({"id":n[0],"method":m,"params":p or {}}))
    while True:
        r=json.loads(ws.recv())
        if r.get("id")==n[0]: return r
def ev(js): return send("Runtime.evaluate",{"expression":js,"returnByValue":True})["result"]["result"].get("value")
ev("[...document.querySelectorAll('button,a,div[role=button]')].find(e=>(e.innerText||'').trim()==='Google')?.click()")
for _ in range(25):
    time.sleep(1.5)
    if "phone" in ev("location.href") or "cloudways.com/" in ev("location.href") and "login" not in ev("location.href"):
        break
time.sleep(3)
print("url:", ev("location.href"))
ws.close()
