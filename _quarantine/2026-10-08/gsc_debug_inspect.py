# -*- coding: utf-8 -*-
"""Отладка: вводим один URL в проверку GSC и смотрим, что реально на странице."""
import json, asyncio, urllib.request
import websockets

PORT = 9229
U = "https://stackpickr.vercel.app/"

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
        print("ERROR: нет вкладки"); return
    async with websockets.connect(ws_url, max_size=20*1024*1024) as ws:
        _id = [0]
        async def call(method, params=None):
            _id[0] += 1
            await ws.send(json.dumps({"id": _id[0], "method": method, "params": params or {}}))
            while True:
                m = json.loads(await ws.recv())
                if m.get("id") == _id[0]:
                    return m.get("result", {})
        await call("Runtime.enable"); await call("Page.enable")
        await call("Page.navigate", {"url": "https://search.google.com/search-console?resource_id=https%3A%2F%2Fstackpickr.vercel.app%2F"})
        await asyncio.sleep(12)
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const inps = [...document.querySelectorAll('input')].filter(i =>
            i.offsetParent !== null && /проверка всех url/i.test(i.getAttribute('aria-label')||''));
          if (!inps.length) return 'none:' + [...document.querySelectorAll('input')].map(i=>i.getAttribute('aria-label')).join('|').slice(0,300);
          const inp = inps[0]; const rc = inp.getBoundingClientRect();
          return JSON.stringify({x: Math.round(rc.x + rc.width/2), y: Math.round(rc.y + rc.height/2)});
        })()""", "returnByValue": True})
        v = r.get("result", {}).get("value")
        print("INPUT:", v)
        if not v or v.startswith("none"): return
        b = json.loads(v)
        await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": b["x"], "y": b["y"], "button": "left", "clickCount": 1})
        await asyncio.sleep(0.05)
        await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": b["x"], "y": b["y"], "button": "left", "clickCount": 1})
        await asyncio.sleep(0.4)
        await call("Input.insertText", {"text": U})
        await asyncio.sleep(0.4)
        await call("Input.dispatchKeyEvent", {"type": "keyDown", "key": "Enter", "code": "Enter", "windowsVirtualKeyCode": 13})
        await call("Input.dispatchKeyEvent", {"type": "keyUp", "key": "Enter", "code": "Enter", "windowsVirtualKeyCode": 13})
        for i in range(8):
            await asyncio.sleep(6)
            st = await call("Runtime.evaluate", {"expression": """
            (() => document.body.innerText.replace(/\\s+/g,' ').slice(0, 1200))()""", "returnByValue": True})
            print(f"--- t={6*(i+1)}s URL:", (await call("Runtime.evaluate", {"expression": "location.href", "returnByValue": True})).get("result",{}).get("value",""))
            print(st.get("result", {}).get("value", ""))
            if i >= 3:
                # если уже есть результат — можно выйти
                txt = st.get("result", {}).get("value", "")
                if "google" in txt.lower() and ("индекс" in txt.lower() or "очеред" in txt.lower()):
                    break

asyncio.run(main())
