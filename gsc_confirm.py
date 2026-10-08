# -*- coding: utf-8 -*-
"""Клик ПОДТВЕРДИТЬ в раскрытой секции 'Тег HTML'."""
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
        await call("Page.enable")
        # убедиться что секция 'Тег HTML' раскрыта — кликнуть заголовок если нужно
        await call("Runtime.evaluate", {"expression": """
        (() => {
          const els = [...document.querySelectorAll('*')].filter(e =>
            e.offsetParent !== null && e.children.length === 0 &&
            (e.innerText||'').trim() === 'Тег HTML');
          if (els.length) { els[0].scrollIntoView({block:'center'}); els[0].click(); }
          return els.length;
        })()
        """, "returnByValue": True})
        await asyncio.sleep(2)
        # найти кнопку ПОДТВЕРДИТЬ в секции Тег HTML
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const spans = [...document.querySelectorAll('span')].filter(e =>
            (e.innerText||'').trim() === 'ПОДТВЕРДИТЬ' && e.children.length === 0);
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
        btns = json.loads(r.get("result", {}).get("value", "[]"))
        print("CONFIRM BTNS:", btns)
        if not btns:
            print("NO CONFIRM BUTTON"); return
        b = btns[0]
        # скролл к кнопке
        await call("Runtime.evaluate", {"expression": """
        (() => {
          const spans = [...document.querySelectorAll('span')].filter(e =>
            (e.innerText||'').trim() === 'ПОДТВЕРДИТЬ' && e.children.length === 0);
          if (spans.length) spans[0].scrollIntoView({block:'center'});
          return 1;
        })()
        """, "returnByValue": True})
        await asyncio.sleep(1)
        # пересчитать координаты после скролла
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const spans = [...document.querySelectorAll('span')].filter(e =>
            (e.innerText||'').trim() === 'ПОДТВЕРДИТЬ' && e.children.length === 0);
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
        """, "returnByValue": True})
        b = json.loads(r.get("result", {}).get("value", "null"))
        print("BTN after scroll:", b)
        if not b or b == 'none':
            return
        await call("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": b["x"], "y": b["y"]})
        await asyncio.sleep(0.3)
        await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": b["x"], "y": b["y"], "button": "left", "clickCount": 1})
        await asyncio.sleep(0.1)
        await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": b["x"], "y": b["y"], "button": "left", "clickCount": 1})
        await asyncio.sleep(6)
        st = await call("Runtime.evaluate", {"expression": """
        (() => JSON.stringify({url: location.href, text: document.body.innerText.replace(/\\s+/g,' ').slice(0,700)}))()
        """, "returnByValue": True})
        print("AFTER CONFIRM:", st.get("result", {}).get("value"))

asyncio.run(main())
