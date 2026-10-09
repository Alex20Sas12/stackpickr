# -*- coding: utf-8 -*-
"""Простучать поле клавиатурными событиями, чтобы кнопка ПРОДОЛЖИТЬ активировалась."""
import json, asyncio, urllib.request
import websockets

PORT = 9229
URL = "https://stackpickr.vercel.app/"

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
        # очистить поле и сфокусировать программно
        await call("Runtime.evaluate", {"expression": """
        (() => {
          const inps = [...document.querySelectorAll('input')].filter(i => i.offsetParent !== null && i.getBoundingClientRect().width > 200);
          const tgt = inps.sort((a,b) => b.getBoundingClientRect().x - a.getBoundingClientRect().x)[0];
          tgt.focus();
          // выделить всё и удалить
          tgt.setSelectionRange(0, tgt.value.length);
          return 'focused, len=' + tgt.value.length;
        })()
        """, "returnByValue": True})
        await asyncio.sleep(0.3)
        await call("Input.dispatchKeyEvent", {"type": "keyDown", "key": "Backspace", "code": "Backspace", "windowsVirtualKeyCode": 8})
        await call("Input.dispatchKeyEvent", {"type": "keyUp", "key": "Backspace", "code": "Backspace", "windowsVirtualKeyCode": 8})
        await asyncio.sleep(0.3)
        # посимвольный ввод через keyDown/char/keyUp — самый надёжный для React
        for ch in URL:
            await call("Input.dispatchKeyEvent", {"type": "char", "text": ch})
            await asyncio.sleep(0.02)
        await asyncio.sleep(1)
        # значение
        st = await call("Runtime.evaluate", {"expression": """
        (() => {
          const inps = [...document.querySelectorAll('input')].filter(i => i.offsetParent !== null && i.getBoundingClientRect().width > 200);
          return JSON.stringify(inps.map(i => ({x: Math.round(i.getBoundingClientRect().x), val: i.value})));
        })()
        """, "returnByValue": True})
        print("VALUES:", st.get("result", {}).get("value"))
        # кнопки ПРОДОЛЖИТЬ
        r2 = await call("Runtime.evaluate", {"expression": """
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
        btns = json.loads(r2.get("result", {}).get("value", "[]"))
        print("CONTINUE BTNS:", btns)
        # кликаем правую (активную) если есть
        active = [b for b in btns if not b["disabled"]]
        if active:
            b = active[-1]  # правая секция ниже/правее
            await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": b["x"], "y": b["y"], "button": "left", "clickCount": 1})
            await asyncio.sleep(0.1)
            await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": b["x"], "y": b["y"], "button": "left", "clickCount": 1})
            await asyncio.sleep(5)
            st3 = await call("Runtime.evaluate", {"expression": """
            (() => JSON.stringify({url: location.href, text: document.body.innerText.replace(/\\s+/g,' ').slice(0, 700)}))()
            """, "returnByValue": True})
            print("AFTER CONTINUE:", st3.get("result", {}).get("value"))
        else:
            print("NO ACTIVE BUTTON")

asyncio.run(main())
