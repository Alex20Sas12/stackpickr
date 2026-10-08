# -*- coding: utf-8 -*-
"""Проверка обработки sitemap (перезагрузка страницы)."""
import json, asyncio, urllib.request
import websockets

PORT = 9229
SM_URL = "https://search.google.com/search-console/sitemaps?resource_id=https%3A%2F%2Fstackpickr.vercel.app%2F"

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
        await call("Page.enable")
        for i in range(4):
            await call("Page.reload")
            await asyncio.sleep(14)
            rows = await call("Runtime.evaluate", {"expression": """
            (() => {
              const trs = [...document.querySelectorAll('tr')].filter(tr => tr.offsetParent !== null);
              return JSON.stringify(trs.map(tr => (tr.innerText||'').replace(/\\s+/g,' ').slice(0,160)).filter(t => /sitemap/i.test(t)));
            })()
            """, "returnByValue": True})
            v = rows.get("result", {}).get("value", "[]")
            print(f"round {i}:", v)
            if "Успешно" in v or "Выявлено" in v and "Не получено" not in v:
                break

asyncio.run(main())
