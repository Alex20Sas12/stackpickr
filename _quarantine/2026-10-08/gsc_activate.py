# -*- coding: utf-8 -*-
"""Активация кнопки: фокус + insertText + input-событие + blur/Enter."""
import json, asyncio, urllib.request
import websockets

PORT = 9229
URL = "https://stackpickr.vercel.app/"

def get_tabs():
    with urllib.request.urlopen(f"http://localhost:{PORT}/json", timeout=5) as r:
        return json.load(r)

def btn_state():
    return """
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
    """

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

        # 1) сфокусировать правое поле кликом мыши по его центру
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const inps = [...document.querySelectorAll('input')].filter(i => i.offsetParent !== null && i.getBoundingClientRect().width > 200);
          const tgt = inps.sort((a,b) => b.getBoundingClientRect().x - a.getBoundingClientRect().x)[0];
          const rc = tgt.getBoundingClientRect();
          return JSON.stringify({x: Math.round(rc.x + rc.width/2), y: Math.round(rc.y + rc.height/2), val: tgt.value});
        })()
        """, "returnByValue": True})
        tgt = json.loads(r.get("result", {}).get("value", "{}"))
        print("TARGET:", tgt)
        await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": tgt["x"], "y": tgt["y"], "button": "left", "clickCount": 3})
        await asyncio.sleep(0.1)
        await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": tgt["x"], "y": tgt["y"], "button": "left", "clickCount": 3})
        await asyncio.sleep(0.5)
        # стереть выделенное
        await call("Input.dispatchKeyEvent", {"type": "keyDown", "key": "Backspace", "code": "Backspace", "windowsVirtualKeyCode": 8})
        await call("Input.dispatchKeyEvent", {"type": "keyUp", "key": "Backspace", "code": "Backspace", "windowsVirtualKeyCode": 8})
        await asyncio.sleep(0.3)
        # 2) insertText (генерирует beforeinput+input как настоящий ввод)
        await call("Input.insertText", {"text": URL})
        await asyncio.sleep(0.7)
        # 3) дополнительно синтетические события ввода/потери фокуса на элементе
        r2 = await call("Runtime.evaluate", {"expression": """
        (() => {
          const inps = [...document.querySelectorAll('input')].filter(i => i.offsetParent !== null && i.getBoundingClientRect().width > 200);
          const tgt = inps.sort((a,b) => b.getBoundingClientRect().x - a.getBoundingClientRect().x)[0];
          tgt.dispatchEvent(new Event('input', {bubbles: true}));
          tgt.dispatchEvent(new Event('change', {bubbles: true}));
          return 'dispatched, val=' + tgt.value;
        })()
        """, "returnByValue": True})
        print("DISPATCH:", r2.get("result", {}).get("value"))
        await asyncio.sleep(0.7)
        st = await call("Runtime.evaluate", {"expression": btn_state(), "returnByValue": True})
        btns = json.loads(st.get("result", {}).get("value", "[]"))
        print("BTNS after events:", btns)
        # 4) если всё ещё не активна — нажать Tab или кликнуть вне поля (потеря фокуса)
        if not any(not b["disabled"] for b in btns):
            await call("Input.dispatchKeyEvent", {"type": "keyDown", "key": "Tab", "code": "Tab", "windowsVirtualKeyCode": 9})
            await call("Input.dispatchKeyEvent", {"type": "keyUp", "key": "Tab", "code": "Tab", "windowsVirtualKeyCode": 9})
            await asyncio.sleep(1)
            st = await call("Runtime.evaluate", {"expression": btn_state(), "returnByValue": True})
            btns = json.loads(st.get("result", {}).get("value", "[]"))
            print("BTNS after Tab:", btns)
        # 5) клик активной правой кнопки
        active = [b for b in btns if not b["disabled"]]
        if active:
            b = max(active, key=lambda x: x["x"])
            await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": b["x"], "y": b["y"], "button": "left", "clickCount": 1})
            await asyncio.sleep(0.1)
            await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": b["x"], "y": b["y"], "button": "left", "clickCount": 1})
            await asyncio.sleep(5)
            st3 = await call("Runtime.evaluate", {"expression": """
            (() => JSON.stringify({text: document.body.innerText.replace(/\\s+/g,' ').slice(0, 600)}))()
            """, "returnByValue": True})
            print("AFTER:", st3.get("result", {}).get("value"))
        else:
            print("STILL DISABLED")

asyncio.run(main())
