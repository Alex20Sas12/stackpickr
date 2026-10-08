# -*- coding: utf-8 -*-
"""Диагностика: куда попал ввод на странице sitemap."""
import json, asyncio, urllib.request
import websockets

PORT = 9229

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
        st = await call("Runtime.evaluate", {"expression": """
        (() => {
          const inps = [...document.querySelectorAll('input')].filter(i => i.offsetParent !== null);
          return JSON.stringify(inps.map(i => {
            const rc = i.getBoundingClientRect();
            return {x: Math.round(rc.x), y: Math.round(rc.y), w: Math.round(rc.width),
                    val: i.value.slice(0,60), ph: i.placeholder.slice(0,40),
                    aria: (i.getAttribute('aria-label')||'').slice(0,40)};
          }));
        })()
        """, "returnByValue": True})
        print("INPUTS:", st.get("result", {}).get("value"))

asyncio.run(main())
