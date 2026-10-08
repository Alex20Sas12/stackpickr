# -*- coding: utf-8 -*-
"""Отладка 3: клик по 'Проверка URL' в сайдбаре, затем ввод URL."""
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
        # 1) клик по элементу сайдбара "Проверка URL"
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const els = [...document.querySelectorAll('a,div,span')].filter(e => e.offsetParent !== null &&
            e.children.length <= 2 && (e.innerText||'').trim() === 'Проверка URL');
          if (!els.length) return 'none';
          const el = els[els.length-1];
          const rc = el.getBoundingClientRect();
          return JSON.stringify({x: Math.round(rc.x + rc.width/2), y: Math.round(rc.y + rc.height/2), tag: el.tagName, href: el.href||''});
        })()""", "returnByValue": True})
        v = r.get("result", {}).get("value")
        print("SIDEBAR:", v)
        if v and v != "none":
            b = json.loads(v)
            await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": b["x"], "y": b["y"], "button": "left", "clickCount": 1})
            await asyncio.sleep(0.05)
            await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": b["x"], "y": b["y"], "button": "left", "clickCount": 1})
            await asyncio.sleep(6)
        print("URL now:", (await call("Runtime.evaluate", {"expression": "location.href", "returnByValue": True})).get("result",{}).get("value",""))
        # 2) найти input проверки
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const inps = [...document.querySelectorAll('input')].filter(i => i.offsetParent !== null);
          return JSON.stringify(inps.map(i => ({al: i.getAttribute('aria-label'), ph: i.placeholder, type: i.type})));
        })()""", "returnByValue": True})
        print("INPUTS:", r.get("result", {}).get("value", "")[:600])
        # 3) клик + ввод + проверка значения
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const inps = [...document.querySelectorAll('input')].filter(i =>
            i.offsetParent !== null && /проверка/i.test(i.getAttribute('aria-label')||''));
          if (!inps.length) return 'none';
          const inp = inps[0]; inp.focus();
          const rc = inp.getBoundingClientRect();
          return JSON.stringify({x: Math.round(rc.x + rc.width/2), y: Math.round(rc.y + rc.height/2)});
        })()""", "returnByValue": True})
        v = r.get("result", {}).get("value")
        print("INSPECT INPUT:", v)
        if not v or v == "none": return
        b = json.loads(v)
        await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": b["x"], "y": b["y"], "button": "left", "clickCount": 1})
        await asyncio.sleep(0.05)
        await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": b["x"], "y": b["y"], "button": "left", "clickCount": 1})
        await asyncio.sleep(0.4)
        await call("Input.insertText", {"text": U})
        await asyncio.sleep(0.5)
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const inps = [...document.querySelectorAll('input')].filter(i =>
            i.offsetParent !== null && /проверка/i.test(i.getAttribute('aria-label')||''));
          return inps.length ? inps[0].value : 'NOINPUT';
        })()""", "returnByValue": True})
        print("VALUE AFTER INSERT:", r.get("result", {}).get("value", ""))
        await call("Input.dispatchKeyEvent", {"type": "keyDown", "key": "Enter", "code": "Enter", "windowsVirtualKeyCode": 13})
        await call("Input.dispatchKeyEvent", {"type": "keyUp", "key": "Enter", "code": "Enter", "windowsVirtualKeyCode": 13})
        for i in range(10):
            await asyncio.sleep(6)
            st = await call("Runtime.evaluate", {"expression": """
            (() => {
              const t = document.body.innerText.replace(/\\s+/g,' ');
              const reqBtn = [...document.querySelectorAll('*')].some(e => e.offsetParent !== null &&
                e.children.length === 0 && /запросить индексирование/i.test((e.innerText||'').trim()));
              return JSON.stringify({url: location.href, indexed: /url есть в google/i.test(t), reqBtn,
                quota: /квота превышена/i.test(t), snippet: t.slice(0, 300)});
            })()""", "returnByValue": True})
            out = st.get("result", {}).get("value", "")
            print(f"--- t={6*(i+1)}s:", out[:500])
            sv = json.loads(out or "{}")
            if sv.get("reqBtn") or sv.get("indexed") or sv.get("quota"):
                break

asyncio.run(main())
