# -*- coding: utf-8 -*-
"""Создание зоны для stackpickr + подключение NativeBanner."""
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

        # попытка 1: создать сайт с юнитом одним запросом (как в журнале завода)
        payload = {
            "zone": NEW_SITE,
            "ad_units": [49],  # NativeBanner (щадящий формат)
            "category_id": 3,  # Other (как у витрины)
            "b_feed_erotic_ads_exclude": True,
        }
        r = await call("Runtime.evaluate", {"expression": f"""
        (async () => {{
          const resp = await fetch('/api/site', {{
            method: 'POST', credentials: 'include',
            headers: {{'Content-Type': 'application/json', 'Accept': 'application/json', 'X-Requested-With': 'XMLHttpRequest'}},
            body: JSON.stringify({json.dumps(payload)})
          }});
          return resp.status + ' | ' + (await resp.text()).slice(0, 800);
        }})()
        """, "returnByValue": True, "awaitPromise": True})
        print("CREATE:", r.get("result", {}).get("value"))

asyncio.run(main())
