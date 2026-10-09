# -*- coding: utf-8 -*-
"""Вывести вкладку Adsterra вперёд + свежая загрузка логина."""
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
    if not ws_url:
        print("NO TAB"); return
    async with websockets.connect(ws_url, max_size=20*1024*1024) as ws:
        _id = [1]
        async def call(method, params=None):
            _id[0] += 1
            await ws.send(json.dumps({"id": _id[0], "method": method, "params": params or {}}))
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("id") == _id[0]:
                    return msg.get("result", {})
        await call("Page.enable")
        await call("Page.bringToFront")
        await call("Page.navigate", {"url": "https://publishers.adsterra.com/login"})
        await asyncio.sleep(12)
        r = await call("Runtime.evaluate", {"expression": "JSON.stringify({url: location.href, title: document.title})", "returnByValue": True})
        print("TAB:", r.get("result", {}).get("value"))

asyncio.run(main())
