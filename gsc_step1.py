# -*- coding: utf-8 -*-
"""GSC шаг 1: проверить состояние вкладки, открыть диалог добавления ресурса."""
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
    if not ws_url:
        # взять любую страницу
        for t in tabs:
            if t.get("type") == "page":
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
        await call("Page.navigate", {"url": "https://search.google.com/search-console"})
        await asyncio.sleep(10)
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const t = document.body.innerText.replace(/\\s+/g,' ').slice(0, 800);
          const hasAdd = (document.body.innerText||'').includes('Добавить сайт') || (document.body.innerText||'').includes('Add property');
          return JSON.stringify({url: location.href, title: document.title, hasAdd, text: t});
        })()
        """, "returnByValue": True})
        print("STATE:", r.get("result", {}).get("value"))

asyncio.run(main())
