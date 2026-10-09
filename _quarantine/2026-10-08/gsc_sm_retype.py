# -*- coding: utf-8 -*-
"""Полный ввод sitemap.xml посимвольно после реального клика + принудительный клик кнопки."""
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
        # координаты поля
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const inp = document.querySelector('input[aria-label="URL файла Sitemap"]');
          inp.scrollIntoView({block:'center'});
          const rc = inp.getBoundingClientRect();
          return JSON.stringify({x: Math.round(rc.x + rc.width/2), y: Math.round(rc.y + rc.height/2), val: inp.value});
        })()
        """, "returnByValue": True})
        inp = json.loads(r.get("result", {}).get("value", "{}"))
        print("INPUT:", inp)
        # реальный клик по полю
        await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": inp["x"], "y": inp["y"], "button": "left", "clickCount": 3})
        await asyncio.sleep(0.05)
        await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": inp["x"], "y": inp["y"], "button": "left", "clickCount": 3})
        await asyncio.sleep(0.3)
        await call("Input.dispatchKeyEvent", {"type": "keyDown", "key": "Delete", "code": "Delete", "windowsVirtualKeyCode": 46})
        await call("Input.dispatchKeyEvent", {"type": "keyUp", "key": "Delete", "code": "Delete", "windowsVirtualKeyCode": 46})
        await asyncio.sleep(0.3)
        for ch in "sitemap.xml":
            await call("Input.dispatchKeyEvent", {"type": "char", "text": ch})
            await asyncio.sleep(0.05)
        await asyncio.sleep(1.2)
        st = await call("Runtime.evaluate", {"expression": """
        (() => {
          const inp = document.querySelector('input[aria-label="URL файла Sitemap"]');
          const spans = [...document.querySelectorAll('span')].filter(e =>
            (e.innerText||'').trim() === 'ОТПРАВИТЬ' && e.children.length === 0);
          for (const sp of spans) {
            let el = sp;
            for (let j = 0; j < 8 && el.parentElement; j++) {
              if (/U26fgb/.test(el.className || '')) {
                const rc = el.getBoundingClientRect();
                return JSON.stringify({val: inp.value, x: Math.round(rc.x + rc.width/2), y: Math.round(rc.y + rc.height/2),
                          cls: el.className.toString().slice(0,60),
                          disabled: /RDPZE/.test(el.className||'') || el.getAttribute('aria-disabled') === 'true'});
              }
              el = el.parentElement;
            }
          }
          return JSON.stringify({val: inp.value, btn: 'none'});
        })()
        """, "returnByValue": True})
        v = json.loads(st.get("result", {}).get("value", "{}"))
        print("STATE:", v)
        if v.get("btn") == "none":
            return
        # принудительный клик по кнопке независимо от состояния
        await call("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": v["x"], "y": v["y"]})
        await asyncio.sleep(0.3)
        await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": v["x"], "y": v["y"], "button": "left", "clickCount": 1})
        await asyncio.sleep(0.1)
        await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": v["x"], "y": v["y"], "button": "left", "clickCount": 1})
        await asyncio.sleep(6)
        rows = await call("Runtime.evaluate", {"expression": """
        (() => {
          const trs = [...document.querySelectorAll('tr')].filter(tr => tr.offsetParent !== null);
          return JSON.stringify(trs.map(tr => (tr.innerText||'').replace(/\\s+/g,' ').slice(0,140)));
        })()
        """, "returnByValue": True})
        print("ROWS:", rows.get("result", {}).get("value"))

asyncio.run(main())
