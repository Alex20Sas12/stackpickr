# -*- coding: utf-8 -*-
"""Дамп верхних 60 видимых элементов страницы с координатами (сайдбар)."""
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
          const els = [...document.querySelectorAll('*')].filter(e => {
            if (e.offsetParent === null) return false;
            const rc = e.getBoundingClientRect();
            return rc.x < 280 && rc.y > 80 && rc.y < 220 && rc.width > 100;
          });
          return JSON.stringify(els.slice(0, 25).map(e => {
            const rc = e.getBoundingClientRect();
            return {tag: e.tagName, cls: (e.className||'').toString().slice(0,40),
                    aria: (e.getAttribute('aria-label')||'').slice(0,40),
                    text: (e.innerText||'').trim().replace(/\\s+/g,' ').slice(0,50),
                    x: Math.round(rc.x), y: Math.round(rc.y), w: Math.round(rc.width), h: Math.round(rc.height)};
          }));
        })()
        """, "returnByValue": True})
        items = json.loads(r.get("result", {}).get("value", "[]"))
        for it in items:
            print(it)

asyncio.run(main())
