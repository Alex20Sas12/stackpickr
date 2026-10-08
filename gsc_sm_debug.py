# -*- coding: utf-8 -*-
"""Пошаговая диагностика: клик поля -> активный элемент -> ввод -> значение."""
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
        # клик по полю
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const inp = document.querySelector('input[aria-label="URL файла Sitemap"]');
          inp.scrollIntoView({block:'center'});
          const rc = inp.getBoundingClientRect();
          return JSON.stringify({x: Math.round(rc.x + rc.width/2), y: Math.round(rc.y + rc.height/2)});
        })()
        """, "returnByValue": True})
        inp = json.loads(r.get("result", {}).get("value"))
        await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": inp["x"], "y": inp["y"], "button": "left", "clickCount": 1})
        await asyncio.sleep(0.05)
        await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": inp["x"], "y": inp["y"], "button": "left", "clickCount": 1})
        await asyncio.sleep(0.6)
        st = await call("Runtime.evaluate", {"expression": """
        (() => {
          const ae = document.activeElement;
          return JSON.stringify({tag: ae.tagName, aria: (ae.getAttribute('aria-label')||'').slice(0,40),
            x: Math.round(ae.getBoundingClientRect().x), y: Math.round(ae.getBoundingClientRect().y)});
        })()
        """, "returnByValue": True})
        print("ACTIVE:", st.get("result", {}).get("value"))
        # ввести один символ
        await call("Input.dispatchKeyEvent", {"type": "char", "text": "s"})
        await asyncio.sleep(0.4)
        st2 = await call("Runtime.evaluate", {"expression": """
        (() => {
          const inp = document.querySelector('input[aria-label="URL файла Sitemap"]');
          return JSON.stringify({val: inp.value});
        })()
        """, "returnByValue": True})
        print("AFTER 1 CHAR:", st2.get("result", {}).get("value"))

asyncio.run(main())
