# -*- coding: utf-8 -*-
"""Проверка: ресурс подтверждён? Открыть селектор ресурсов."""
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
        await call("Page.enable")
        # открыть селектор
        await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": 153, "y": 98, "button": "left", "clickCount": 1})
        await asyncio.sleep(0.1)
        await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": 153, "y": 98, "button": "left", "clickCount": 1})
        await asyncio.sleep(2.5)
        st = await call("Runtime.evaluate", {"expression": """
        (() => {
          const t = document.body.innerText.replace(/\\s+/g,' ');
          const idx = t.indexOf('stackpickr');
          return JSON.stringify({hasStackpickr: idx >= 0, snippet: idx >= 0 ? t.slice(Math.max(0,idx-100), idx+200) : t.slice(0,200)});
        })()
        """, "returnByValue": True})
        print("SELECTOR:", st.get("result", {}).get("value"))

asyncio.run(main())
