# -*- coding: utf-8 -*-
"""Список зон + создание зоны для stackpickr через внутренний API."""
import json, asyncio, urllib.request
import websockets

PORT = 9222
NEW_SITE = "stackpickr.vercel.app"

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
        await call("Runtime.enable")

        # 1) текущие зоны
        r = await call("Runtime.evaluate", {"expression": """
        (async () => {
          const r = await fetch('/api/sites', {credentials:'include', headers:{'Accept':'application/json'}});
          return r.status + ' | ' + (await r.text()).slice(0, 1500);
        })()
        """, "returnByValue": True, "awaitPromise": True})
        print("SITES:", r.get("result", {}).get("value", "")[:1600])

asyncio.run(main())
