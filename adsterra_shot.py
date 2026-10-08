# -*- coding: utf-8 -*-
import json, asyncio, base64, urllib.request
import websockets

PORT = 9222

def get_tabs():
    with urllib.request.urlopen(f"http://localhost:{PORT}/json", timeout=5) as r:
        return json.load(r)

async def main():
    tabs = get_tabs()
    ws_url = None
    for t in tabs:
        if t.get("type") == "page" and "adsterra" in t.get("url", ""):
            ws_url = t["webSocketDebuggerUrl"]; break
    async with websockets.connect(ws_url, max_size=20*1024*1024) as ws:
        _id = [1]
        async def call(method, params=None):
            _id[0] += 1
            await ws.send(json.dumps({"id": _id[0], "method": method, "params": params or {}}))
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("id") == _id[0]:
                    return msg.get("result", {})
        await call("Runtime.enable")
        shot = await call("Page.captureScreenshot", {"format": "png"})
        with open(r"C:\Users\Admin\fabrika\cmpsite\adsterra-login-state.png", "wb") as f:
            f.write(base64.b64decode(shot["data"]))
        # координаты кнопки
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const b = [...document.querySelectorAll('button')].find(b => b.offsetParent !== null && /^Log in$/i.test((b.textContent||'').trim()));
          if (!b) return 'no btn';
          const rc = b.getBoundingClientRect();
          return JSON.stringify({x: rc.x + rc.width/2, y: rc.y + rc.height/2, disabled: b.disabled});
        })()
        """, "returnByValue": True})
        print("BTN:", r.get("result", {}).get("value"))
        print("SAVED")

asyncio.run(main())
