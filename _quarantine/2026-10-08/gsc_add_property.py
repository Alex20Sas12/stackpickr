# -*- coding: utf-8 -*-
"""Клик 'Добавить ресурс' в открытом попапе + ожидание диалога."""
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
        # сначала проверить, открыт ли попап; если нет — кликнуть селектор заново
        r0 = await call("Runtime.evaluate", {"expression": """
        (() => {
          const els = [...document.querySelectorAll('*')].filter(e =>
            e.offsetParent !== null && e.children.length === 0 &&
            (e.innerText||'').trim() === 'Добавить ресурс');
          return JSON.stringify(els.map(e => {
            const rc = e.getBoundingClientRect();
            return {x: Math.round(rc.x + rc.width/2), y: Math.round(rc.y + rc.height/2)};
          }));
        })()
        """, "returnByValue": True})
        hits = json.loads(r0.get("result", {}).get("value", "[]"))
        if not hits:
            # переоткрыть селектор
            await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": 153, "y": 98, "button": "left", "clickCount": 1})
            await asyncio.sleep(0.1)
            await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": 153, "y": 98, "button": "left", "clickCount": 1})
            await asyncio.sleep(3)
            r0 = await call("Runtime.evaluate", {"expression": """
            (() => {
              const els = [...document.querySelectorAll('*')].filter(e =>
                e.offsetParent !== null && e.children.length === 0 &&
                (e.innerText||'').trim() === 'Добавить ресурс');
              return JSON.stringify(els.map(e => {
                const rc = e.getBoundingClientRect();
                return {x: Math.round(rc.x + rc.width/2), y: Math.round(rc.y + rc.height/2)};
              }));
            })()
            """, "returnByValue": True})
            hits = json.loads(r0.get("result", {}).get("value", "[]"))
        print("ADD BTN:", hits)
        if not hits:
            print("NOT FOUND"); return
        h = hits[0]
        await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": h["x"], "y": h["y"], "button": "left", "clickCount": 1})
        await asyncio.sleep(0.1)
        await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": h["x"], "y": h["y"], "button": "left", "clickCount": 1})
        await asyncio.sleep(4)
        st = await call("Runtime.evaluate", {"expression": """
        (() => {
          const inps = [...document.querySelectorAll('input')].filter(i => i.offsetParent !== null);
          return JSON.stringify({
            url: location.href,
            title: document.title,
            h1: (document.querySelector('h1,h2')||{}).innerText || '',
            inps: inps.map(i => ({x: Math.round(i.getBoundingClientRect().x), y: Math.round(i.getBoundingClientRect().y),
                                   w: Math.round(i.getBoundingClientRect().width), ph: i.placeholder||''})),
            text: document.body.innerText.replace(/\\s+/g,' ').slice(0, 500)
          });
        })()
        """, "returnByValue": True})
        print("DIALOG:", st.get("result", {}).get("value"))

asyncio.run(main())
