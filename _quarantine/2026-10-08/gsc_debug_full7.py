# -*- coding: utf-8 -*-
"""Отладка 7: полный цикл для одного URL с дампами текста и скриншотами после клика кнопки."""
import json, asyncio, base64, urllib.request
import websockets

PORT = 9229
U = "https://stackpickr.vercel.app/"

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
        async def txt(limit=800):
            r = await call("Runtime.evaluate", {"expression": f"document.body.innerText.replace(/\\s+/g,' ').slice(0,{limit})", "returnByValue": True})
            return r.get("result", {}).get("value", "")
        async def shot(name):
            r = await call("Page.captureScreenshot", {"format": "jpeg", "quality": 60})
            data = r.get("data")
            if data:
                with open(name, "wb") as f: f.write(base64.b64decode(data))
                print("shot:", name)
        await call("Page.navigate", {"url": "https://search.google.com/search-console?resource_id=https%3A%2F%2Fstackpickr.vercel.app%2F"})
        await asyncio.sleep(12)
        # ввести URL
        r = await call("Runtime.evaluate", {"expression": """
        ((U) => {
          const inp = [...document.querySelectorAll('input')].filter(i =>
            i.offsetParent !== null && /проверка всех url/i.test(i.getAttribute('aria-label')||''))[0];
          if (!inp) return 'none';
          inp.focus();
          const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
          setter.call(inp, U);
          inp.dispatchEvent(new Event('input', {bubbles: true}));
          for (const type of ['keydown', 'keypress', 'keyup']) {
            inp.dispatchEvent(new KeyboardEvent(type, {key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true, cancelable: true}));
          }
          return 'sent';
        })(%s)""" % json.dumps(U), "returnByValue": True})
        print("SET:", r.get("result", {}).get("value"))
        # ждать появления результата проверки (кнопка) до 60 сек
        got = False
        for i in range(12):
            await asyncio.sleep(5)
            st = await call("Runtime.evaluate", {"expression": """
            (() => {
              const t = document.body.innerText.replace(/\\s+/g,' ');
              const reqBtn = [...document.querySelectorAll('*')].some(e => e.offsetParent !== null &&
                e.children.length === 0 && /запросить индексирование/i.test((e.innerText||'').trim()));
              return JSON.stringify({indexed: /url есть в google/i.test(t), reqBtn, quota: /квота превышена/i.test(t)});
            })()""", "returnByValue": True})
            sv = json.loads(st.get("result", {}).get("value", "{}"))
            print(f"t={5*(i+1)}s status:", sv)
            if sv.get("reqBtn") or sv.get("indexed") or sv.get("quota"):
                got = True; break
        await shot("dbg7_inspect_result.jpg")
        print("TEXT:", await txt(600))
        if not got or not sv.get("reqBtn"):
            return
        # закрыть подсказки
        await call("Runtime.evaluate", {"expression": """
        (() => { const els = [...document.querySelectorAll('*')].filter(e =>
            e.offsetParent !== null && e.children.length === 0 && (e.innerText||'').trim() === 'Закрыть');
          for (const e of els) e.click(); return els.length; })()""", "returnByValue": True})
        await asyncio.sleep(1)
        # найти кнопку, координаты, кликнуть мышью
        r3 = await call("Runtime.evaluate", {"expression": """
        (() => {
          const els = [...document.querySelectorAll('*')].filter(e =>
            e.offsetParent !== null && e.children.length === 0 &&
            /запросить индексирование/i.test((e.innerText||'').trim()) && (e.innerText||'').trim().length < 40);
          if (!els.length) return 'none';
          const el = els[0];
          el.scrollIntoView({block:'center'});
          const rc = el.getBoundingClientRect();
          return JSON.stringify({x: Math.round(rc.x + rc.width/2), y: Math.round(rc.y + rc.height/2), tag: el.tagName, cls: (el.className||'').toString().slice(0,60)});
        })()""", "returnByValue": True})
        v = r3.get("result", {}).get("value")
        print("BTN:", v)
        if not v or v == "none": return
        bb = json.loads(v)
        await asyncio.sleep(0.5)
        await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": bb["x"], "y": bb["y"], "button": "left", "clickCount": 1})
        await asyncio.sleep(0.1)
        await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": bb["x"], "y": bb["y"], "button": "left", "clickCount": 1})
        print("clicked")
        for i in range(24):
            await asyncio.sleep(8)
            t = await txt(400)
            st = await call("Runtime.evaluate", {"expression": """
            (() => {
              const t = document.body.innerText.replace(/\\s+/g,' ');
              return JSON.stringify({queued: /поставлен в очередь|запрошено индексирование|в очередь/i.test(t),
                quota: /квота превышена|превышен/i.test(t)});
            })()""", "returnByValue": True})
            sv2 = json.loads(st.get("result", {}).get("value", "{}"))
            print(f"--- t={8*(i+1)}s:", sv2, "|", t[:200])
            if sv2.get("queued"):
                await shot("dbg7_queued.jpg"); break
            if sv2.get("quota"):
                await shot("dbg7_quota.jpg"); break
            if i == 3: await shot("dbg7_mid.jpg")

asyncio.run(main())
