# -*- coding: utf-8 -*-
"""Найти точный iframe капчи внутри контейнера и кликнуть чекбокс по его геометрии."""
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
        # геометрия всех iframe с их позицией
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          return JSON.stringify([...document.querySelectorAll('iframe')].map(f => {
            const rc = f.getBoundingClientRect();
            return {src: f.src || '(blank)', x: rc.x, y: rc.y, w: rc.width, h: rc.height,
                    parent: f.parentElement ? (f.parentElement.id || f.parentElement.className.toString().slice(0,30)) : ''};
          }));
        })()
        """, "returnByValue": True})
        print("ALL IFRAMES:", json.dumps(json.loads(r.get("result", {}).get("value", "[]")), indent=1))

asyncio.run(main())
