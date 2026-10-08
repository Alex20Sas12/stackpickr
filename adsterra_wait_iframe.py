# -*- coding: utf-8 -*-
"""Долгое ожидание загрузки Turnstile iframe + клик по его реальному чекбоксу."""
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
        await call("Page.enable")
        await call("Page.navigate", {"url": "https://publishers.adsterra.com/login"})
        # ждём 20 секунд, периодически проверяая ифреймы
        target = None
        for wait_round in range(10):
            await asyncio.sleep(2)
            r = await call("Runtime.evaluate", {"expression": """
            (() => {
              const ifs = [...document.querySelectorAll('iframe')];
              return JSON.stringify(ifs.map(f => {
                const rc = f.getBoundingClientRect();
                return {src: f.src||'', x: rc.x, y: rc.y, w: rc.width, h: rc.height};
              }));
            })()
            """, "returnByValue": True})
            ifs = json.loads(r.get("result", {}).get("value", "[]"))
            cf = [f for f in ifs if "challenge" in f.get("src","") or "turnstile" in f.get("src","")]
            print(f"round {wait_round}: {len(ifs)} iframes, cf={len(cf)}")
            for f in cf:
                print("   CF:", f)
            if cf:
                target = cf[0]; break
        if not target:
            print("NO CF IFRAME after 20s")
            return
        # клик по чекбоксу в ифрейме (обычно ~28-32px слева, центр по вертикали)
        cx = target["x"] + 30
        cy = target["y"] + target["h"] / 2
        print(f"click {cx:.0f},{cy:.0f}")
        await call("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": cx, "y": cy})
        await asyncio.sleep(0.6)
        await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": cx, "y": cy, "button": "left", "clickCount": 1})
        await asyncio.sleep(0.15)
        await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": cx, "y": cy, "button": "left", "clickCount": 1})
        await asyncio.sleep(8)
        st = await call("Runtime.evaluate", {"expression": """
        (() => {
          const btn = [...document.querySelectorAll('button')].find(b => /log in|авторизоваться/i.test((b.textContent||'').trim()));
          const resp = document.querySelector('input[name="cf-turnstile-response"]');
          return JSON.stringify({btnDisabled: btn ? btn.disabled : null, hasResponse: resp ? !!resp.value : null, url: location.href});
        })()
        """, "returnByValue": True})
        print("STATE:", st.get("result", {}).get("value"))

asyncio.run(main())
