# -*- coding: utf-8 -*-
"""Ожидание верификации зоны + извлечение кода NativeBanner."""
import json, asyncio, urllib.request
import websockets

PORT = 9222
SITE_ID = 14781522

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

        for attempt in range(8):
            r = await call("Runtime.evaluate", {"expression": """
            (async () => {
              const r = await fetch('/api/sites', {credentials:'include', headers:{'Accept':'application/json'}});
              const d = await r.json();
              const site = (d.data.items||[]).find(s => s.id === %d);
              return JSON.stringify(site);
            })()
            """ % SITE_ID, "returnByValue": True, "awaitPromise": True})
            site = json.loads(r.get("result", {}).get("value") or "null")
            status = site.get("status") if site else None
            print(f"attempt {attempt}: status={status}")
            # status 2 = активен (как у витрины); 4 = в обработке
            if status == 2:
                print("SITE ACTIVE!")
                break
            if status not in (4,):
                print("UNEXPECTED STATUS:", json.dumps(site)[:300])
            await asyncio.sleep(15)

        # получить плейсменты с кодами
        r2 = await call("Runtime.evaluate", {"expression": """
        (async () => {
          const r = await fetch('/api/placements/%d/extended', {credentials:'include', headers:{'Accept':'application/json'}});
          return r.status + ' | ' + (await r.text()).slice(0, 2000);
        })()
        """ % SITE_ID, "returnByValue": True, "awaitPromise": True})
        print("PLACEMENTS:", r2.get("result", {}).get("value", "")[:2100])

asyncio.run(main())
