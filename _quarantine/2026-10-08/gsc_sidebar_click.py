# -*- coding: utf-8 -*-
"""Клик селектора ресурса в сайдбаре (коорд. со скриншота: центр ~131,138)."""
import json, asyncio, urllib.request
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
        await call("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": 131, "y": 138})
        await asyncio.sleep(0.3)
        await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": 131, "y": 138, "button": "left", "clickCount": 1})
        await asyncio.sleep(0.1)
        await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": 131, "y": 138, "button": "left", "clickCount": 1})
        await asyncio.sleep(3)
        r3 = await call("Runtime.evaluate", {"expression": """
        (() => {
          const els = [...document.querySelectorAll('*')].filter(e =>
            e.offsetParent !== null && e.children.length === 0 &&
            /добавить ресурс|добавить сайт|выбрать ресурс|выбрать сайт|все ресурсы|управление ресурсами|управление свойствами|выбрать свойство/.test(e.innerText||''));
          return JSON.stringify(els.slice(0,8).map(e => {
            const rc = e.getBoundingClientRect();
            return {tag: e.tagName, text: (e.innerText||'').trim().slice(0,60),
                    x: Math.round(rc.x + rc.width/2), y: Math.round(rc.y + rc.height/2)};
          }));
        })()
        """, "returnByValue": True})
        print("MENU:", r3.get("result", {}).get("value"))

asyncio.run(main())
