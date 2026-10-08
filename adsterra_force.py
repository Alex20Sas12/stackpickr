# -*- coding: utf-8 -*-
"""Форс-рендер Turnstile виджета + клик по чекбоксу."""
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
        # есть ли глобальный turnstile объект?
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const w = window.turnstile;
          const el = document.getElementById('cf-turnstile');
          return JSON.stringify({
            hasTurnstile: !!w,
            methods: w ? Object.keys(w).slice(0,10) : [],
            elExists: !!el,
            elDataSitekey: el ? (el.getAttribute('data-sitekey')||'none') : 'no-el',
            elHTML: el ? el.innerHTML.slice(0,300) : ''
          });
        })()
        """, "returnByValue": True})
        print("CHECK:", r.get("result", {}).get("value"))

asyncio.run(main())
