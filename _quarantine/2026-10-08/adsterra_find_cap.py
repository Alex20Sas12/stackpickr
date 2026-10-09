# -*- coding: utf-8 -*-
"""Поиск контейнера капчи: все ифреймы + любые элементы с 'turnstile|challenge|captcha'."""
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
          const out = [];
          for (const el of document.querySelectorAll('*')) {
            const cls = (el.className||'').toString ? (el.className||'').toString() : '';
            if (/turnstile|challenge|captcha|hcaptcha|recaptcha/i.test(cls + ' ' + (el.id||''))) {
              const rc = el.getBoundingClientRect();
              out.push({tag: el.tagName, id: el.id, cls: cls.slice(0,80), x: rc.x, y: rc.y, w: rc.width, h: rc.height});
            }
          }
          return JSON.stringify(out.slice(0, 15));
        })()
        """, "returnByValue": True})
        print("MATCHES:", r.get("result", {}).get("value"))
        # также все ифреймы с видимыми размерами
        r2 = await call("Runtime.evaluate", {"expression": """
        (() => {
          return JSON.stringify([...document.querySelectorAll('iframe')].map(f => {
            const rc = f.getBoundingClientRect();
            return {src: (f.src||'').slice(0,100), x: rc.x, y: rc.y, w: rc.width, h: rc.height, title: f.title||''};
          }).filter(f => f.w > 50));
        })()
        """, "returnByValue": True})
        print("VISIBLE IFRAMES:", r2.get("result", {}).get("value"))

asyncio.run(main())
