# -*- coding: utf-8 -*-
"""Раскрыть секцию 'Тег HTML' и извлечь метатег верификации."""
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
        # кликнуть заголовок секции 'Тег HTML'
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const els = [...document.querySelectorAll('*')].filter(e =>
            e.offsetParent !== null && e.children.length === 0 &&
            (e.innerText||'').trim() === 'Тег HTML');
          if (!els.length) return JSON.stringify({err: 'not found'});
          const el = els[0];
          const rc = el.getBoundingClientRect();
          return JSON.stringify({x: Math.round(rc.x + rc.width/2), y: Math.round(rc.y + rc.height/2)});
        })()
        """, "returnByValue": True})
        hit = json.loads(r.get("result", {}).get("value", "{}"))
        print("TAG SECTION:", hit)
        if "err" in hit:
            return
        await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": hit["x"], "y": hit["y"], "button": "left", "clickCount": 1})
        await asyncio.sleep(0.1)
        await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": hit["x"], "y": hit["y"], "button": "left", "clickCount": 1})
        await asyncio.sleep(2)
        # извлечь метатег
        r2 = await call("Runtime.evaluate", {"expression": """
        (() => {
          const codes = [...document.querySelectorAll('code, textarea, pre')]
            .map(e => (e.innerText || e.value || '').trim())
            .filter(x => /google/.test(x));
          return JSON.stringify(codes.slice(0, 5));
        })()
        """, "returnByValue": True})
        print("META TAGS:", r2.get("result", {}).get("value"))

asyncio.run(main())
