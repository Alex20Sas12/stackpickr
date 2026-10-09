# -*- coding: utf-8 -*-
"""Отладка 5: исследуем DOM вокруг input проверки URL — ищем кнопку отправки."""
import json, asyncio, urllib.request
import websockets

PORT = 9229

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
        await call("Runtime.enable")
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const inp = [...document.querySelectorAll('input')].filter(i =>
            i.offsetParent !== null && /проверка всех url/i.test(i.getAttribute('aria-label')||''))[0];
          if (!inp) return 'NOINPUT';
          const out = [];
          // подняться на 5 уровней и собрать всех кликабельных/иконки
          let el = inp;
          for (let lv = 0; lv < 6 && el; lv++) {
            const parent = el.parentElement;
            if (!parent) break;
            for (const c of parent.children) {
              if (c === el) continue;
              const html = c.outerHTML.slice(0, 400);
              out.push({level: lv, tag: c.tagName, cls: (c.className||'').toString().slice(0,80),
                aria: c.getAttribute('aria-label'), role: c.getAttribute('role'),
                txt: (c.innerText||'').trim().slice(0,60), html: html.replace(/\\s+/g,' ')});
            }
            el = parent;
          }
          // также форма
          const form = inp.closest('form');
          return JSON.stringify({siblings: out, hasForm: !!form,
            formAction: form ? form.action : null,
            inpHTML: inp.outerHTML.slice(0,300)}, null, 1).slice(0, 6000);
        })()""", "returnByValue": True})
        print(r.get("result", {}).get("value", ""))

asyncio.run(main())
