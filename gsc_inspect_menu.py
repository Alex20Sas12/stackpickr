# -*- coding: utf-8 -*-
"""Проверка одного URL через раздел 'Проверка URL' в меню."""
import json, asyncio, urllib.request
import websockets

PORT = 9229
U = "https://stackpickr.vercel.app/"

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
        # кликнуть пункт меню 'Проверка URL'
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const links = [...document.querySelectorAll('a')].filter(a => a.offsetParent !== null &&
            /проверка url/i.test(a.innerText||''));
          if (!links.length) return 'none';
          links[0].click();
          return 'clicked';
        })()
        """, "returnByValue": True})
        print("MENU:", r.get("result", {}).get("value"))
        await asyncio.sleep(6)
        # найти инпут проверки
        r2 = await call("Runtime.evaluate", {"expression": """
        (() => {
          const inps = [...document.querySelectorAll('input, textarea')].filter(i => i.offsetParent !== null && i.getBoundingClientRect().width > 300);
          return JSON.stringify(inps.map(i => ({x: Math.round(i.getBoundingClientRect().x + i.getBoundingClientRect().width/2),
            y: Math.round(i.getBoundingClientRect().y + i.getBoundingClientRect().height/2),
            aria: (i.getAttribute('aria-label')||'').slice(0,50), ph: i.placeholder.slice(0,50)})));
        })()
        """, "returnByValue": True})
        print("INPUTS:", r2.get("result", {}).get("value"))

asyncio.run(main())
