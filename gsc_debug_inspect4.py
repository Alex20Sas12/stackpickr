# -*- coding: utf-8 -*-
"""Отладка 4: Enter с text=\r + поиск кнопки отправки."""
import json, asyncio, urllib.request
import websockets

PORT = 9229
U = "https://stackpickr.vercel.app/hosting/"

async def main():
    with urllib.request.urlopen(f"http://localhost:{PORT}/json", timeout=5) as r:
        tabs = json.load(r)
    ws_url = None
    for t in tabs:
        if t.get("type") == "page" and "search.google.com" in t.get("url", ""):
            ws_url = t["webSocketDebuggerUrl"]; break
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
        # ввод через JS + native input events
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const inps = [...document.querySelectorAll('input')].filter(i =>
            i.offsetParent !== null && /проверка всех url/i.test(i.getAttribute('aria-label')||''));
          if (!inps.length) return 'none';
          const inp = inps[0]; inp.focus();
          const rc = inp.getBoundingClientRect();
          return JSON.stringify({x: Math.round(rc.x + rc.width/2), y: Math.round(rc.y + rc.height/2)});
        })()""", "returnByValue": True})
        v = r.get("result", {}).get("value")
        if not v or v == "none":
            print("NO INPUT"); return
        b = json.loads(v)
        await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": b["x"], "y": b["y"], "button": "left", "clickCount": 1})
        await asyncio.sleep(0.05)
        await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": b["x"], "y": b["y"], "button": "left", "clickCount": 1})
        await asyncio.sleep(0.3)
        # выделить всё и вставить
        await call("Input.dispatchKeyEvent", {"type": "keyDown", "key": "a", "code": "KeyA", "windowsVirtualKeyCode": 65, "modifiers": 2})
        await call("Input.dispatchKeyEvent", {"type": "keyUp", "key": "a", "code": "KeyA", "windowsVirtualKeyCode": 65, "modifiers": 2})
        await call("Input.insertText", {"text": U})
        await asyncio.sleep(0.4)
        # Enter С text=\r
        await call("Input.dispatchKeyEvent", {"type": "keyDown", "key": "Enter", "code": "Enter", "windowsVirtualKeyCode": 13, "nativeVirtualKeyCode": 13, "text": "\r", "unmodifiedText": "\r"})
        await call("Input.dispatchKeyEvent", {"type": "char", "key": "Enter", "code": "Enter", "windowsVirtualKeyCode": 13, "text": "\r", "unmodifiedText": "\r"})
        await call("Input.dispatchKeyEvent", {"type": "keyUp", "key": "Enter", "code": "Enter", "windowsVirtualKeyCode": 13, "nativeVirtualKeyCode": 13})
        for i in range(12):
            await asyncio.sleep(5)
            st = await call("Runtime.evaluate", {"expression": """
            (() => {
              const t = document.body.innerText.replace(/\\s+/g,' ');
              const reqBtn = [...document.querySelectorAll('*')].some(e => e.offsetParent !== null &&
                e.children.length === 0 && /запросить индексирование/i.test((e.innerText||'').trim()));
              return JSON.stringify({url: location.href, indexed: /url есть в google/i.test(t), reqBtn,
                quota: /квота превышена/i.test(t),
                checking: /проверяется|идет проверка|идёт проверка|тестируется/i.test(t),
                snippet: t.slice(0, 250)});
            })()""", "returnByValue": True})
            out = st.get("result", {}).get("value", "")
            print(f"--- t={5*(i+1)}s:", out[:450])
            sv = json.loads(out or "{}")
            if sv.get("reqBtn") or sv.get("indexed") or sv.get("quota"):
                break

asyncio.run(main())
