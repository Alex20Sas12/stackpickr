# -*- coding: utf-8 -*-
"""Точная позиция виджета внутри контейнера + повторные попытки клика."""
import json, asyncio, urllib.request
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
        # точная геометрия: все дочерние элементы контейнера
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const cont = document.getElementById('cf-turnstile');
          if (!cont) return 'no container';
          const inner = [...cont.querySelectorAll('*')].map(el => {
            const rc = el.getBoundingClientRect();
            return {tag: el.tagName, cls: ((el.className||'').toString||Object.prototype.toString).call(el.className).slice(0,50),
                    x: Math.round(rc.x), y: Math.round(rc.y), w: Math.round(rc.width), h: Math.round(rc.height)};
          }).filter(e => e.w > 20 && e.h > 20);
          return JSON.stringify(inner.slice(0, 12));
        })()
        """, "returnByValue": True})
        print("INNER:", r.get("result", {}).get("value"))

asyncio.run(main())
