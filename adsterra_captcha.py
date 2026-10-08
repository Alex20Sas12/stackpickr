# -*- coding: utf-8 -*-
"""Клик по чекбоксу Turnstile через Input.dispatchMouseEvent."""
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
        # позиция turnstile-контейнера
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const el = document.querySelector('.cf-turnstile') || document.querySelector('[data-sitekey]');
          if (!el) return JSON.stringify({err: 'no turnstile el'});
          const rc = el.getBoundingClientRect();
          return JSON.stringify({x: rc.x, y: rc.y, w: rc.width, h: rc.height});
        })()
        """, "returnByValue": True})
        pos = json.loads(r.get("result", {}).get("value", "{}"))
        print("TURNSTILE:", pos)
        if "err" in pos:
            return
        # чекбокс обычно в левой части виджета, по вертикали в центре
        cx = pos["x"] + 28
        cy = pos["y"] + pos["h"] / 2
        print(f"CLICK at {cx}, {cy}")
        await call("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": cx, "y": cy})
        await asyncio.sleep(0.4)
        await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": cx, "y": cy, "button": "left", "clickCount": 1})
        await asyncio.sleep(0.12)
        await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": cx, "y": cy, "button": "left", "clickCount": 1})
        await asyncio.sleep(7)
        st = await call("Runtime.evaluate", {"expression": """
        (() => {
          const btn = [...document.querySelectorAll('button')].find(b => /^Log in$/i.test((b.textContent||'').trim()));
          const resp = document.querySelector('input[name="cf-turnstile-response"]');
          return JSON.stringify({btnDisabled: btn ? btn.disabled : null, url: location.href,
            hasResponse: resp ? !!resp.value : null});
        })()
        """, "returnByValue": True})
        print("STATE:", st.get("result", {}).get("value"))

asyncio.run(main())
