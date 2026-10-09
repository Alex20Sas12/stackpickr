# -*- coding: utf-8 -*-
"""Клик селектора + скриншот результата."""
import json, asyncio, base64, urllib.request
import websockets

PORT = 9229

def get_tabs():
    with urllib.request.urlopen(f"http://localhost:{PORT}/json", timeout=5) as r:
        return json.load(r)

async def main():
    tabs = get_tabs()
    ws_url = None
    for t in tabs:
        if t.get("type") == "page" and "search.google.com" in t.get("url", ""):
            ws_url = t["webSocketDebuggerUrl"]; break
    async with websockets.connect(ws_url, max_size=40*1024*1024) as ws:
        _id = [1]
        async def call(method, params=None):
            _id[0] += 1
            await ws.send(json.dumps({"id": _id[0], "method": method, "params": params or {}}))
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("id") == _id[0]:
                    return msg.get("result", {})
        await call("Runtime.enable")
        await call("Page.enable")
        x, y = 153, 98
        await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": x, "y": y, "button": "left", "clickCount": 1})
        await asyncio.sleep(0.1)
        await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": x, "y": y, "button": "left", "clickCount": 1})
        await asyncio.sleep(3)
        # дамп всех видимых текстов (коротких) в верхней части экрана
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const els = [...document.querySelectorAll('*')].filter(e => {
            if (e.offsetParent === null || e.children.length > 0) return false;
            const rc = e.getBoundingClientRect();
            return rc.y < 500 && rc.width > 20 && (e.innerText||'').trim().length > 1 && (e.innerText||'').trim().length < 60;
          });
          return JSON.stringify(els.slice(0,40).map(e => {
            const rc = e.getBoundingClientRect();
            return {t: (e.innerText||'').trim(), x: Math.round(rc.x+rc.width/2), y: Math.round(rc.y+rc.height/2)};
          }));
        })()
        """, "returnByValue": True})
        items = json.loads(r.get("result", {}).get("value", "[]"))
        for it in items:
            print(f"({it['x']},{it['y']}) {it['t']}")
        shot = await call("Page.captureScreenshot", {"format": "png"})
        with open(r"C:\Users\Admin\fabrika\cmpsite\gsc-after-click.png", "wb") as f:
            f.write(base64.b64decode(shot["data"]))
        print("SHOT SAVED")

asyncio.run(main())
