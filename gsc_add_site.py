# -*- coding: utf-8 -*-
"""Клик 'Добавить сайт' в диалоге выбора типа ресурса."""
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
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const els = [...document.querySelectorAll('*')].filter(e =>
            e.offsetParent !== null && e.children.length === 0 &&
            (e.innerText||'').trim() === 'Добавить сайт');
          if (!els.length) return JSON.stringify([]);
          const e = els[0];
          const rc = e.getBoundingClientRect();
          return JSON.stringify([{x: Math.round(rc.x + rc.width/2), y: Math.round(rc.y + rc.height/2)}]);
        })()
        """, "returnByValue": True})
        hits = json.loads(r.get("result", {}).get("value", "[]"))
        print("BTN:", hits)
        if not hits:
            return
        h = hits[0]
        await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": h["x"], "y": h["y"], "button": "left", "clickCount": 1})
        await asyncio.sleep(0.1)
        await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": h["x"], "y": h["y"], "button": "left", "clickCount": 1})
        await asyncio.sleep(4)
        st = await call("Runtime.evaluate", {"expression": """
        (() => {
          const inps = [...document.querySelectorAll('input')].map(i => {
            const rc = i.getBoundingClientRect();
            return {x: Math.round(rc.x), y: Math.round(rc.y), w: Math.round(rc.width), visible: i.offsetParent !== null};
          }).filter(i => i.visible && i.w > 50);
          return JSON.stringify({text: document.body.innerText.replace(/\\s+/g,' ').slice(0, 600), inps});
        })()
        """, "returnByValue": True})
        print("AFTER:", st.get("result", {}).get("value"))

asyncio.run(main())
