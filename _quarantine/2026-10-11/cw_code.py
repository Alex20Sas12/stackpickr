import json, time, urllib.request, websocket, sys
code = sys.argv[1]
req = urllib.request.Request("http://localhost:9232/json/list")
tabs = json.loads(urllib.request.urlopen(req, timeout=10).read())
t = [x for x in tabs if "unified.cloudways.com/security" in x["url"]][0]
ws = websocket.create_connection(t["webSocketDebuggerUrl"], timeout=30)
n=[0]
def send(m,p=None):
    n[0]+=1; ws.send(json.dumps({"id":n[0],"method":m,"params":p or {}}))
    while True:
        r=json.loads(ws.recv())
        if r.get("id")==n[0]: return r
def ev(js): return send("Runtime.evaluate",{"expression":js,"returnByValue":True})["result"]["result"].get("value")
ev("(()=>{const i=document.querySelector('input'); i.focus(); return 1})()")
for ch in code:
    send("Input.dispatchKeyEvent",{"type":"keyDown","text":ch,"key":ch})
    send("Input.dispatchKeyEvent",{"type":"keyUp","key":ch})
    time.sleep(0.12)
time.sleep(0.5)
ev("[...document.querySelectorAll('button')].find(b=>/verify|submit|continue|confirm/i.test(b.innerText))?.click()")
time.sleep(7)
print("url:", ev("location.href"))
print("text:", (ev("document.body.innerText.slice(0,300)") or "").replace("\n"," | "))
ws.close()
