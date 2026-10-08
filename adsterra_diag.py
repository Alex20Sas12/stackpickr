# -*- coding: utf-8 -*-
"""Диагностика: все src ифреймов + доступность challenges.cloudflare.com."""
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
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          return JSON.stringify([...document.querySelectorAll('iframe')].map(f => f.src || '(empty)'));
        })()
        """, "returnByValue": True})
        print("IFRAME SRCS:", r.get("result", {}).get("value"))
        # тест доступности turnstile API
        r2 = await call("Runtime.evaluate", {"expression": """
        (async () => {
          try {
            const resp = await fetch('https://challenges.cloudflare.com/turnstile/v0/api.js', {method: 'GET'});
            return 'HTTP ' + resp.status;
          } catch(e) { return 'FETCH ERR: ' + String(e); }
        })()
        """, "returnByValue": True, "awaitPromise": True})
        print("CF API:", r2.get("result", {}).get("value"))
        # ошибки консоли
        errs = await call("Runtime.evaluate", {"expression": """
        (() => {
          return JSON.stringify(window.__pageErrors || 'no collector');
        })()
        """, "returnByValue": True})
        print("ERRORS:", errs.get("result", {}).get("value"))

asyncio.run(main())
