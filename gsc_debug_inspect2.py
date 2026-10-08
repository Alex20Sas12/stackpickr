# -*- coding: utf-8 -*-
"""Отладка 2: прямой переход на inspect-URL."""
import json, asyncio, urllib.request, urllib.parse
import websockets

PORT = 9229
U = "https://stackpickr.vercel.app/hosting/"

async def main():
    with urllib.request.urlopen(f"http://localhost:{PORT}/json", timeout=5) as r:
        tabs = json.load(r)
    ws_url = None
    for t in tabs:
        if t.get("type") == "page" and "search.google.com" in t.get("url", ""):
            ws_url = t["webSocketDebuggerUrl"]; break
    async with websockets.connect(ws_url, max_size=20*1024*1024) as ws:
        _id = [0]
        async def call(method, params=None):
            _id[0] += 1
            await ws.send(json.dumps({"id": _id[0], "method": method, "params": params or {}}))
            while True:
                m = json.loads(await ws.recv())
                if m.get("id") == _id[0]:
                    return m.get("result", {})
        await call("Runtime.enable"); await call("Page.enable")
        target = ("https://search.google.com/search-console/inspect?resource_id="
                  + urllib.parse.quote("https://stackpickr.vercel.app/", safe="")
                  + "&id=" + urllib.parse.quote(U, safe="") + "&hl=ru")
        print("NAV:", target)
        await call("Page.navigate", {"url": target})
        for i in range(10):
            await asyncio.sleep(6)
            st = await call("Runtime.evaluate", {"expression": """
            (() => {
              const t = document.body.innerText.replace(/\\s+/g,' ');
              const reqBtn = [...document.querySelectorAll('*')].some(e => e.offsetParent !== null &&
                e.children.length === 0 && /запросить индексирование/i.test((e.innerText||'').trim()));
              return JSON.stringify({indexed: /url есть в google/i.test(t), reqBtn,
                quota: /квота превышена/i.test(t), snippet: t.slice(0, 500)});
            })()""", "returnByValue": True})
            print(f"--- t={6*(i+1)}s:", st.get("result", {}).get("value", "")[:700])
            sv = json.loads(st.get("result", {}).get("value", "{}"))
            if sv.get("reqBtn") or sv.get("indexed") or sv.get("quota"):
                break

asyncio.run(main())
