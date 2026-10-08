# -*- coding: utf-8 -*-
"""Отладка 6: JS-Enter / form submit."""
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
        # ввод текста через JS с input-событием
        r = await call("Runtime.evaluate", {"expression": f"""
        (() => {{
          const inp = [...document.querySelectorAll('input')].filter(i =>
            i.offsetParent !== null && /проверка всех url/i.test(i.getAttribute('aria-label')||''))[0];
          if (!inp) return 'NOINPUT';
          inp.focus();
          const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
          setter.call(inp, {json.dumps(U)});
          inp.dispatchEvent(new Event('input', {{bubbles: true}}));
          inp.dispatchEvent(new Event('change', {{bubbles: true}}));
          return 'SET:' + inp.value;
        }})()""", "returnByValue": True})
        print("SET:", r.get("result", {}).get("value", ""))
        await asyncio.sleep(1)
        # JS keydown Enter
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const inp = [...document.querySelectorAll('input')].filter(i =>
            i.offsetParent !== null && /проверка всех url/i.test(i.getAttribute('aria-label')||''))[0];
          if (!inp) return 'NOINPUT';
          for (const type of ['keydown', 'keypress', 'keyup']) {
            inp.dispatchEvent(new KeyboardEvent(type, {key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true, cancelable: true}));
          }
          return 'ENTER_DISPATCHED';
        })()""", "returnByValue": True})
        print("ENTER:", r.get("result", {}).get("value", ""))
        await asyncio.sleep(5)
        cur = (await call("Runtime.evaluate", {"expression": "location.href", "returnByValue": True})).get("result",{}).get("value","")
        print("URL after Enter:", cur)
        if "inspect" not in cur:
            # пробуем form.requestSubmit
            r = await call("Runtime.evaluate", {"expression": """
            (() => {
              const inp = [...document.querySelectorAll('input')].filter(i =>
                i.offsetParent !== null && /проверка всех url/i.test(i.getAttribute('aria-label')||''))[0];
              const form = inp && inp.closest('form');
              if (!form) return 'NOFORM';
              try { form.requestSubmit(); return 'SUBMITTED'; } catch(e) { form.submit(); return 'SUBMIT_FALLBACK'; }
            })()""", "returnByValue": True})
            print("FORM:", r.get("result", {}).get("value", ""))
            await asyncio.sleep(6)
            cur = (await call("Runtime.evaluate", {"expression": "location.href", "returnByValue": True})).get("result",{}).get("value","")
            print("URL after submit:", cur)
        for i in range(10):
            await asyncio.sleep(6)
            st = await call("Runtime.evaluate", {"expression": """
            (() => {
              const t = document.body.innerText.replace(/\\s+/g,' ');
              const reqBtn = [...document.querySelectorAll('*')].some(e => e.offsetParent !== null &&
                e.children.length === 0 && /запросить индексирование/i.test((e.innerText||'').trim()));
              return JSON.stringify({url: location.href, indexed: /url есть в google/i.test(t), reqBtn,
                quota: /квота превышена/i.test(t), snippet: t.slice(0, 250)});
            })()""", "returnByValue": True})
            out = st.get("result", {}).get("value", "")
            print(f"--- t={6*(i+1)}s:", out[:450])
            sv = json.loads(out or "{}")
            if sv.get("reqBtn") or sv.get("indexed") or sv.get("quota"):
                break

asyncio.run(main())
