import json, time, urllib.request, websocket
req = urllib.request.Request("http://localhost:9232/json/new?https://unified.cloudways.com/account/referral", method="PUT")
t = json.loads(urllib.request.urlopen(req, timeout=10).read())
time.sleep(7)
ws = websocket.create_connection(t["webSocketDebuggerUrl"], timeout=30)
n = [0]
def send(m, p=None):
    n[0] += 1
    ws.send(json.dumps({"id": n[0], "method": m, "params": p or {}}))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == n[0]:
            return r
r = send("Runtime.evaluate", {"expression": "location.href + ' || ' + document.body.innerText.slice(0,900)", "returnByValue": True})
print(r["result"]["result"].get("value"))
ws.close()
