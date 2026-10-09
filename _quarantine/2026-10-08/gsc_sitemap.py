# -*- coding: utf-8 -*-
"""Отправка sitemap на страницу Файлы Sitemap."""
import json, asyncio, base64, urllib.request
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
    async with websockets.connect(ws_url, max_size=40*1024*1024) as ws:
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
        await asyncio.sleep(12)
        # найти инпут в строке с кнопкой ОТПРАВИТЬ (по вертикальной близости)
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const btns = [...document.querySelectorAll('button, div[role=button], span')]
            .filter(e => e.offsetParent !== null && (e.innerText||'').trim() === 'ОТПРАВИТЬ');
          if (!btns.length) return JSON.stringify({err: 'no submit btn'});
          const btn = btns[0];
          const by = btn.getBoundingClientRect().y;
          const inps = [...document.querySelectorAll('input')].filter(i => i.offsetParent !== null);
          const inp = inps.find(i => Math.abs(i.getBoundingClientRect().y - by) < 20 && i.value === '');
          if (!inp) return JSON.stringify({err: 'no input', btnY: by, inps: inps.map(i => ({y: Math.round(i.getBoundingClientRect().y), val: i.value}))});
          inp.scrollIntoView({block:'center'});
          inp.focus(); inp.click();
          const rc = inp.getBoundingClientRect();
          return JSON.stringify({ok: true, x: Math.round(rc.x + rc.width/2), y: Math.round(rc.y + rc.height/2)});
        })()
        """, "returnByValue": True})
        v = json.loads(r.get("result", {}).get("value", "{}"))
        print("INPUT:", v)
        if not v.get("ok"):
            return
        await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": v["x"], "y": v["y"], "button": "left", "clickCount": 1})
        await asyncio.sleep(0.1)
        await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": v["x"], "y": v["y"], "button": "left", "clickCount": 1})
        await asyncio.sleep(0.4)
        await call("Input.insertText", {"text": "sitemap.xml"})
        await asyncio.sleep(1)
        # найти и кликнуть ОТПРАВИТЬ заново (активную)
        r2 = await call("Runtime.evaluate", {"expression": """
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
        b = json.loads(r2.get("result", {}).get("value", "null"))
        print("SUBMIT BTN:", b)
        if not b or b.get("disabled"):
            print("SUBMIT DISABLED"); return
        await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": b["x"], "y": b["y"], "button": "left", "clickCount": 1})
        await asyncio.sleep(0.1)
        await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": b["x"], "y": b["y"], "button": "left", "clickCount": 1})
        await asyncio.sleep(6)
        st = await call("Runtime.evaluate", {"expression": """
        (() => {
          const rows = [...document.querySelectorAll('tr')].filter(tr => tr.offsetParent !== null);
          return JSON.stringify({rows: rows.map(tr => (tr.innerText||'').replace(/\\s+/g,' ').slice(0,140)).filter(t => /sitemap/i.test(t)),
            snippet: document.body.innerText.replace(/\\s+/g,' ').slice(0, 300)});
        })()
        """, "returnByValue": True})
        print("RESULT:", st.get("result", {}).get("value"))

asyncio.run(main())
