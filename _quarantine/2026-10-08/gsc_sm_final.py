# -*- coding: utf-8 -*-
"""Финальная проверка кнопки ОТПРАВИТЬ и отправка."""
import json, asyncio, urllib.request
import websockets

PORT = 9229

def get_tabs():
    with urllib.request.urlopen(f"http://localhost:{PORT}/json", timeout=5) as r:
        return json.load(r)

JS_BTN = """
(() => {
  const spans = [...document.querySelectorAll('span')].filter(e =>
    (e.innerText||'').trim() === 'ОТПРАВИТЬ' && e.children.length === 0);
  for (const sp of spans) {
    let el = sp;
    for (let j = 0; j < 8 && el.parentElement; j++) {
      if (/U26fgb/.test(el.className || '')) {
        const rc = el.getBoundingClientRect();
        return JSON.stringify({x: Math.round(rc.x + rc.width/2), y: Math.round(rc.y + rc.height/2),
                  disabled: /RDPZE/.test(el.className||'') || el.getAttribute('aria-disabled') === 'true'});
      }
      el = el.parentElement;
    }
  }
  return 'none';
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
        # допечатать значение (если оно уже полное — перепечатать не страшно: выделим и введём заново)
        await call("Runtime.evaluate", {"expression": """
        (() => {
          const inp = document.querySelector('input[aria-label="URL файла Sitemap"]');
          inp.focus();
          inp.setSelectionRange(0, inp.value.length);
          return inp.value;
        })()
        """, "returnByValue": True})
        await asyncio.sleep(0.3)
        await call("Input.insertText", {"text": "sitemap.xml"})
        await asyncio.sleep(0.5)
        # реальный посимвольный штрих: пробел + backspace чтобы React точно увидел change
        await call("Input.dispatchKeyEvent", {"type": "char", "text": "."})
        await asyncio.sleep(0.2)
        await call("Input.dispatchKeyEvent", {"type": "rawKeyDown", "key": "Backspace", "code": "Backspace", "windowsVirtualKeyCode": 8})
        await call("Input.dispatchKeyEvent", {"type": "keyUp", "key": "Backspace", "code": "Backspace", "windowsVirtualKeyCode": 8})
        await asyncio.sleep(1)
        st = await call("Runtime.evaluate", {"expression": JS_BTN, "returnByValue": True})
        b = st.get("result", {}).get("value")
        print("BTN:", b)
        bj = json.loads(b) if b != "none" else None
        if bj and not bj.get("disabled"):
            await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": bj["x"], "y": bj["y"], "button": "left", "clickCount": 1})
            await asyncio.sleep(0.1)
            await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": bj["x"], "y": bj["y"], "button": "left", "clickCount": 1})
            await asyncio.sleep(8)
            rows = await call("Runtime.evaluate", {"expression": """
            (() => {
              const trs = [...document.querySelectorAll('tr')].filter(tr => tr.offsetParent !== null);
              return JSON.stringify(trs.map(tr => (tr.innerText||'').replace(/\\s+/g,' ').slice(0,150)));
            })()
            """, "returnByValue": True})
            print("ROWS:", rows.get("result", {}).get("value"))
        else:
            print("still disabled")

asyncio.run(main())
