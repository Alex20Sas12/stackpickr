# -*- coding: utf-8 -*-
"""Переход в ресурс + отправка sitemap.xml."""
import json, asyncio, base64, urllib.request
import websockets

PORT = 9229
URL = "https://search.google.com/search-console?resource_id=https%3A%2F%2Fstackpickr.vercel.app%2F"

def get_tabs():
    with urllib.request.urlopen(f"http://localhost:{PORT}/json", timeout=5) as r:
        return json.load(r)

async def main():
    tabs = get_tabs()
    ws_url = None
    for t in tabs:
        if t.get("type") == "page" and "search.google.com" in t.get("url", ""):
            ws_url = t["webSocketDebuggerUrl"]; break
    async with websockets.connect(ws_url, max_size=40*1024*1024) as ws:
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
        await call("Page.navigate", {"url": URL})
        await asyncio.sleep(12)
        st = await call("Runtime.evaluate", {"expression": """
        (() => JSON.stringify({url: location.href, snippet: document.body.innerText.replace(/\\s+/g,' ').slice(0, 250)}))()
        """, "returnByValue": True})
        print("OVERVIEW:", st.get("result", {}).get("value"))

asyncio.run(main())
