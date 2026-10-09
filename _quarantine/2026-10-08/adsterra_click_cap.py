# -*- coding: utf-8 -*-
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
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const el = document.getElementById('cf-turnstile');
          const rc = el.getBoundingClientRect();
          return JSON.stringify({x: rc.x, y: rc.y, w: rc.width, h: rc.height});
        })()
        """, "returnByValue": True})
        pos = json.loads(r.get("result", {}).get("value", "{}"))
        cx = pos["x"] + 30
        cy = pos["y"] + pos["h"] / 2
        print(f"click {cx:.0f},{cy:.0f}")
        await call("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": cx, "y": cy})
        await asyncio.sleep(0.5)
        await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": cx, "y": cy, "button": "left", "clickCount": 1})
        await asyncio.sleep(0.15)
        await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": cx, "y": cy, "button": "left", "clickCount": 1})
        await asyncio.sleep(8)
        st = await call("Runtime.evaluate", {"expression": """
        (() => {
          const btn = [...document.querySelectorAll('button')].find(b => /^Log in$/i.test((b.textContent||'').trim()));
          const resp = document.querySelector('input[name="cf-turnstile-response"]');
          return JSON.stringify({url: location.href, btnDisabled: btn ? btn.disabled : null,
            hasResponse: resp ? !!resp.value : null});
        })()
        """, "returnByValue": True})
        print("STATE:", st.get("result", {}).get("value"))

asyncio.run(main())
