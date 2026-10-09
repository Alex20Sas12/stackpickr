# -*- coding: utf-8 -*-
"""Клик по чекбоксу Turnstile координатами + ожидание разблокировки кнопки."""
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
        # найти iframe Turnstile и его чекбокс
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const ifs = [...document.querySelectorAll('iframe')];
          const info = ifs.map(f => ({src: (f.src||'').slice(0,80), rc: f.getBoundingClientRect()}));
          const btn = [...document.querySelectorAll('button')].find(b => /^Log in$/i.test((b.textContent||'').trim()));
          return JSON.stringify({iframes: info, btnDisabled: btn ? btn.disabled : null});
        })()
        """, "returnByValue": True})
        print("IFRAMES:", r.get("result", {}).get("value"))

asyncio.run(main())
