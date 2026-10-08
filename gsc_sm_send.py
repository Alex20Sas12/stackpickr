# -*- coding: utf-8 -*-
"""Закрыть подсказку + клик ОТПРАВИТЬ координатами + проверить таблицу."""
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
        # закрыть подсказку
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const els = [...document.querySelectorAll('*')].filter(e =>
            e.offsetParent !== null && e.children.length === 0 &&
            (e.innerText||'').trim() === 'Закрыть');
          if (els.length) { els[els.length-1].click(); return 'closed'; }
          return 'none';
        })()
        """, "returnByValue": True})
        print("CLOSE:", r.get("result", {}).get("value"))
        await asyncio.sleep(1.5)
        # координаты кнопки ОТПРАВИТЬ заново
        r2 = await call("Runtime.evaluate", {"expression": """
        (() => {
          const spans = [...document.querySelectorAll('span')].filter(e =>
            (e.innerText||'').trim() === 'ОТПРАВИТЬ' && e.children.length === 0 && e.offsetParent !== null);
          if (!spans.length) return 'none';
          const rc = spans[0].getBoundingClientRect();
          return JSON.stringify({x: Math.round(rc.x + rc.width/2), y: Math.round(rc.y + rc.height/2)});
        })()
        """, "returnByValue": True})
        v = r2.get("result", {}).get("value")
        print("BTN:", v)
        if v == "none":
            return
        b = json.loads(v)
        await call("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": b["x"], "y": b["y"]})
        await asyncio.sleep(0.4)
        await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": b["x"], "y": b["y"], "button": "left", "clickCount": 1})
        await asyncio.sleep(0.1)
        await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": b["x"], "y": b["y"], "button": "left", "clickCount": 1})
        await asyncio.sleep(8)
        rows = await call("Runtime.evaluate", {"expression": """
        (() => {
          const trs = [...document.querySelectorAll('tr')].filter(tr => tr.offsetParent !== null);
          return JSON.stringify(trs.map(tr => (tr.innerText||'').replace(/\\s+/g,' ').slice(0,150)));
        })()
        """, "returnByValue": True})
        print("ROWS:", rows.get("result", {}).get("value"))

asyncio.run(main())
