# -*- coding: utf-8 -*-
"""GSC шаг 2: найти и кликнуть 'Добавить сайт'."""
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
        # поиск кнопки добавить ресурс — слева сверху обычно селектор ресурса
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const els = [...document.querySelectorAll('button, div[role=button], a')]
            .filter(e => e.offsetParent !== null);
          const cands = els.filter(e => /добавить|выбрать|ресурс|селект|сайт|свойств|property/i.test(e.innerText||''));
          return JSON.stringify(cands.slice(0,10).map(e => {
            const rc = e.getBoundingClientRect();
            return {tag: e.tagName, text: (e.innerText||'').trim().slice(0,40),
                    x: Math.round(rc.x + rc.width/2), y: Math.round(rc.y + rc.height/2)};
          }));
        })()
        """, "returnByValue": True})
        print("CANDS:", r.get("result", {}).get("value"))

asyncio.run(main())
