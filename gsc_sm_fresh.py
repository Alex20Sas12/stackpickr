# -*- coding: utf-8 -*-
"""Свежая загрузка + полный ввод с нуля (один проход)."""
import json, asyncio, urllib.request
import websockets

PORT = 9229
SM_URL = "https://search.google.com/search-console/sitemaps?resource_id=https%3A%2F%2Fstackpickr.vercel.app%2F"

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
        await call("Page.navigate", {"url": SM_URL})
        await asyncio.sleep(13)

        def btn_state():
            return call("Runtime.evaluate", {"expression": """
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
            """, "returnByValue": True})

        # координаты поля и реальный клик
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const inp = document.querySelector('input[aria-label="URL файла Sitemap"]');
          if (!inp) return 'noinput';
          inp.scrollIntoView({block:'center'});
          const rc = inp.getBoundingClientRect();
          return JSON.stringify({x: Math.round(rc.x + rc.width/2), y: Math.round(rc.y + rc.height/2), val: inp.value});
        })()
        """, "returnByValue": True})
        print("FIELD:", r.get("result", {}).get("value"))
        if r.get("result", {}).get("value") == "noinput":
            return
        inp = json.loads(r.get("result", {}).get("value"))
        await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": inp["x"], "y": inp["y"], "button": "left", "clickCount": 1})
        await asyncio.sleep(0.05)
        await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": inp["x"], "y": inp["y"], "button": "left", "clickCount": 1})
        await asyncio.sleep(0.5)
        # ввод посимвольно
        for ch in "sitemap.xml":
            await call("Input.dispatchKeyEvent", {"type": "char", "text": ch})
            await asyncio.sleep(0.06)
        await asyncio.sleep(1.5)
        st = await btn_state()
        print("BTN after typing:", st.get("result", {}).get("value"))
        b = json.loads(st.get("result", {}).get("value", "null")) if st.get("result", {}).get("value") != "none" else None
        if b and not b.get("disabled"):
            await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": b["x"], "y": b["y"], "button": "left", "clickCount": 1})
            await asyncio.sleep(0.1)
            await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": b["x"], "y": b["y"], "button": "left", "clickCount": 1})
            await asyncio.sleep(7)
        else:
            # пробем Enter на поле
            await call("Runtime.evaluate", {"expression": """
            (() => { const inp = document.querySelector('input[aria-label="URL файла Sitemap"]'); inp.focus(); return inp.value; })()
            """, "returnByValue": True})
            await asyncio.sleep(0.3)
            await call("Input.dispatchKeyEvent", {"type": "keyDown", "key": "Enter", "code": "Enter", "windowsVirtualKeyCode": 13})
            await call("Input.dispatchKeyEvent", {"type": "keyUp", "key": "Enter", "code": "Enter", "windowsVirtualKeyCode": 13})
            await asyncio.sleep(7)
        rows = await call("Runtime.evaluate", {"expression": """
        (() => {
          const trs = [...document.querySelectorAll('tr')].filter(tr => tr.offsetParent !== null);
          return JSON.stringify(trs.map(tr => (tr.innerText||'').replace(/\\s+/g,' ').slice(0,150)));
        })()
        """, "returnByValue": True})
        print("ROWS:", rows.get("result", {}).get("value"))

asyncio.run(main())
