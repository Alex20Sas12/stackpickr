# -*- coding: utf-8 -*-
"""Инспекция главной страницы через верхнюю строку + скриншоты каждого шага."""
import json, asyncio, base64, urllib.request
import websockets

PORT = 9229
U = "https://stackpickr.vercel.app/"
SHOT_DIR = r"C:\Users\Admin\fabrika\cmpsite"

def get_tabs():
    with urllib.request.urlopen(f"http://localhost:{PORT}/json", timeout=5) as r:
        return json.load(r)

async def shot(call, name):
    s = await call("Page.captureScreenshot", {"format": "png"})
    with open(f"{SHOT_DIR}\\{name}.png", "wb") as f:
        f.write(base64.b64decode(s["data"]))
    print(f"shot {name} saved")

async def main():
    tabs = get_tabs()
    ws_url = None
    for t in tabs:
        if t.get("type") == "page" and "search.google.com" in t.get("url", ""):
            ws_url = t["webSocketDebuggerUrl"]; break
    async with websockets.connect(ws_url, max_size=40*1024*1024) as ws:
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
        # вернуться на главную ресурса
        await call("Page.navigate", {"url": "https://search.google.com/search-console?resource_id=https%3A%2F%2Fstackpickr.vercel.app%2F"})
        await asyncio.sleep(11)
        await shot(call, "ins-step1")
        # верхняя строка
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const inp = document.querySelector('input[aria-label^="Проверка всех URL"]');
          if (!inp) return 'none';
          const rc = inp.getBoundingClientRect();
          return JSON.stringify({x: Math.round(rc.x + rc.width/2), y: Math.round(rc.y + rc.height/2)});
        })()
        """, "returnByValue": True})
        v = r.get("result", {}).get("value")
        print("BAR:", v)
        if v == "none":
            return
        b = json.loads(v)
        await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": b["x"], "y": b["y"], "button": "left", "clickCount": 1})
        await asyncio.sleep(0.05)
        await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": b["x"], "y": b["y"], "button": "left", "clickCount": 1})
        await asyncio.sleep(0.5)
        await call("Input.insertText", {"text": U})
        await asyncio.sleep(0.5)
        await call("Input.dispatchKeyEvent", {"type": "keyDown", "key": "Enter", "code": "Enter", "windowsVirtualKeyCode": 13})
        await call("Input.dispatchKeyEvent", {"type": "keyUp", "key": "Enter", "code": "Enter", "windowsVirtualKeyCode": 13})
        # ждать до 45 сек
        for i in range(9):
            await asyncio.sleep(5)
            st = await call("Runtime.evaluate", {"expression": """
            (() => {
              const t = document.body.innerText.replace(/\\s+/g,' ');
              return JSON.stringify({
                hasRequestBtn: [...document.querySelectorAll('*')].some(e => e.offsetParent !== null && e.children.length === 0 && /запросить индексирование/i.test((e.innerText||'').trim()) && (e.innerText||'').trim().length < 40),
                indexed: /url есть в google/i.test(t),
                snippet: t.slice(0, 300)
              });
            })()
            """, "returnByValue": True})
            sv = json.loads(st.get("result", {}).get("value", "{}"))
            print(f"t={5*(i+1)}s:", sv.get("hasRequestBtn"), "|", sv.get("snippet", "")[:150])
            if sv.get("hasRequestBtn") or sv.get("indexed"):
                break
        await shot(call, "ins-step2")

asyncio.run(main())
