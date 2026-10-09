# -*- coding: utf-8 -*-
"""Комплексная попытка: insertText + blur + Enter + клик. Диагностика реального disabled."""
import json, asyncio, urllib.request
import websockets

PORT = 9229
URL = "https://stackpickr.vercel.app/"

def get_tabs():
    with urllib.request.urlopen(f"http://localhost:{PORT}/json", timeout=5) as r:
        return json.load(r)

JS_BTN = """
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
                  cls: el.className.toString().slice(0,80),
                  disabledAttr: el.disabled === true,
                  ariaDisabled: el.getAttribute('aria-disabled')});
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
        # координаты правого поля
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const inps = [...document.querySelectorAll('input')].filter(i => i.offsetParent !== null && i.getBoundingClientRect().width > 200);
          const tgt = inps.sort((a,b) => b.getBoundingClientRect().x - a.getBoundingClientRect().x)[0];
          const rc = tgt.getBoundingClientRect();
          return JSON.stringify({x: Math.round(rc.x + rc.width/2), y: Math.round(rc.y + rc.height/2)});
        })()
        """, "returnByValue": True})
        tgt = json.loads(r.get("result", {}).get("value", "{}"))
        print("field:", tgt)
        # выделить всё и удалить
        await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": tgt["x"], "y": tgt["y"], "button": "left", "clickCount": 3})
        await asyncio.sleep(0.05)
        await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": tgt["x"], "y": tgt["y"], "button": "left", "clickCount": 3})
        await asyncio.sleep(0.3)
        await call("Input.dispatchKeyEvent", {"type": "rawKeyDown", "key": "Delete", "code": "Delete", "windowsVirtualKeyCode": 46})
        await call("Input.dispatchKeyEvent", {"type": "keyUp", "key": "Delete", "code": "Delete", "windowsVirtualKeyCode": 46})
        await asyncio.sleep(0.3)
        # insertText
        await call("Input.insertText", {"text": URL})
        await asyncio.sleep(1.0)
        # blur — клик в пустую область диалога (заголовок)
        await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": 560, "y": 150, "button": "left", "clickCount": 1})
        await asyncio.sleep(0.1)
        await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": 560, "y": 150, "button": "left", "clickCount": 1})
        await asyncio.sleep(1.2)
        st = await call("Runtime.evaluate", {"expression": JS_BTN, "returnByValue": True})
        print("after blur:", st.get("result", {}).get("value"))
        btns = json.loads(st.get("result", {}).get("value", "[]"))
        right = max(btns, key=lambda x: x["x"]) if btns else None
        active = right and not right.get("disabledAttr") and right.get("ariaDisabled") not in ("true",)
        # даже если выглядит неактивной — попробуем нажать правую кнопку + Enter
        if right:
            await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": right["x"], "y": right["y"], "button": "left", "clickCount": 1})
            await asyncio.sleep(0.1)
            await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": right["x"], "y": right["y"], "button": "left", "clickCount": 1})
            await asyncio.sleep(4)
            st2 = await call("Runtime.evaluate", {"expression": "JSON.stringify({url: location.href, txt: document.body.innerText.replace(/\\s+/g,' ').slice(0,400)})", "returnByValue": True})
            print("after click:", st2.get("result", {}).get("value"))

asyncio.run(main())
