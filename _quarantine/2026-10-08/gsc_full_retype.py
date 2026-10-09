# -*- coding: utf-8 -*-
"""Полный перезапуск ввода: тройной клик, стирание, посимвольный ввод, Enter."""
import json, asyncio, urllib.request
import websockets

PORT = 9229
URL = "https://stackpickr.vercel.app"  # без хвостового слэша

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
        # центр правого поля
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const inps = [...document.querySelectorAll('input')].filter(i => i.offsetParent !== null && i.getBoundingClientRect().width > 200);
          const tgt = inps.sort((a,b) => b.getBoundingClientRect().x - a.getBoundingClientRect().x)[0];
          const rc = tgt.getBoundingClientRect();
          return JSON.stringify({x: Math.round(rc.x + rc.width/2), y: Math.round(rc.y + rc.height/2)});
        })()
        """, "returnByValue": True})
        tgt = json.loads(r.get("result", {}).get("value", "{}"))
        # тройной клик = выделить всё
        await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": tgt["x"], "y": tgt["y"], "button": "left", "clickCount": 3})
        await asyncio.sleep(0.05)
        await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": tgt["x"], "y": tgt["y"], "button": "left", "clickCount": 3})
        await asyncio.sleep(0.4)
        await call("Input.dispatchKeyEvent", {"type": "keyDown", "key": "Delete", "code": "Delete", "windowsVirtualKeyCode": 46})
        await call("Input.dispatchKeyEvent", {"type": "keyUp", "key": "Delete", "code": "Delete", "windowsVirtualKeyCode": 46})
        await asyncio.sleep(0.4)
        # посимвольно, полные события
        for ch in URL:
            await call("Input.dispatchKeyEvent", {"type": "keyDown", "text": ch, "key": ch, "code": "", "windowsVirtualKeyCode": ord(ch)})
            await call("Input.dispatchKeyEvent", {"type": "char", "text": ch})
            await call("Input.dispatchKeyEvent", {"type": "keyUp", "key": ch, "code": "", "windowsVirtualKeyCode": ord(ch)})
            await asyncio.sleep(0.03)
        await asyncio.sleep(1.2)
        st = await call("Runtime.evaluate", {"expression": """
        (() => {
          const inps = [...document.querySelectorAll('input')].filter(i => i.offsetParent !== null && i.getBoundingClientRect().width > 200);
          return JSON.stringify(inps.map(i => ({x: Math.round(i.getBoundingClientRect().x), val: i.value})));
        })()
        """, "returnByValue": True})
        print("VALUES:", st.get("result", {}).get("value"))
        st2 = await call("Runtime.evaluate", {"expression": """
        (() => {
          const spans = [...document.querySelectorAll('span')].filter(e =>
            (e.innerText||'').trim() === 'ПРОДОЛЖИТЬ' && e.children.length === 0);
          const out = [];
          for (const sp of spans) {
            let el = sp;
            for (let j = 0; j < 8 && el.parentElement; j++) {
              if (/U26fgb/.test(el.className || '')) {
                const rc = el.getBoundingClientRect();
                out.push({x: Math.round(rc.x + rc.width/2), y: Math.round(rc.y + rc.height/2),
                          disabled: /RDPZE/.test(el.className||'') || el.getAttribute('aria-disabled') === 'true'});
                break;
              }
              el = el.parentElement;
            }
          }
          return JSON.stringify(out);
        })()
        """, "returnByValue": True})
        btns = json.loads(st2.get("result", {}).get("value", "[]"))
        print("BTNS:", btns)
        active = [b for b in btns if not b["disabled"]]
        if active:
            b = max(active, key=lambda x: x["x"])
            await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": b["x"], "y": b["y"], "button": "left", "clickCount": 1})
            await asyncio.sleep(0.1)
            await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": b["x"], "y": b["y"], "button": "left", "clickCount": 1})
            await asyncio.sleep(6)
            st3 = await call("Runtime.evaluate", {"expression": """
            (() => JSON.stringify({text: document.body.innerText.replace(/\\s+/g,' ').slice(0, 600)}))()
            """, "returnByValue": True})
            print("AFTER:", st3.get("result", {}).get("value"))
        else:
            # попробовать Enter
            await call("Input.dispatchKeyEvent", {"type": "keyDown", "key": "Enter", "code": "Enter", "windowsVirtualKeyCode": 13})
            await call("Input.dispatchKeyEvent", {"type": "keyUp", "key": "Enter", "code": "Enter", "windowsVirtualKeyCode": 13})
            await asyncio.sleep(5)
            st3 = await call("Runtime.evaluate", {"expression": """
            (() => JSON.stringify({text: document.body.innerText.replace(/\\s+/g,' ').slice(0, 600)}))()
            """, "returnByValue": True})
            print("AFTER ENTER:", st3.get("result", {}).get("value"))

asyncio.run(main())
