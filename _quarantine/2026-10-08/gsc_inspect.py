# -*- coding: utf-8 -*-
"""Инспекция URL через верхнюю строку + запрос индексации."""
import json, asyncio, urllib.request
import websockets

PORT = 9229
URLS = [
    "https://stackpickr.vercel.app/",
    "https://stackpickr.vercel.app/hosting/",
    "https://stackpickr.vercel.app/affiliate-software/",
    "https://stackpickr.vercel.app/hosting/best-vps-providers/",
    "https://stackpickr.vercel.app/affiliate-software/best-affiliate-software/",
    "https://stackpickr.vercel.app/guides/",
]

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

        for u in URLS:
            # база ресурса — страница обзора
            await call("Page.navigate", {"url": "https://search.google.com/search-console?resource_id=https%3A%2F%2Fstackpickr.vercel.app%2F"})
            await asyncio.sleep(9)
            # верхняя строка проверки URL
            r = await call("Runtime.evaluate", {"expression": """
            (() => {
              const inps = [...document.querySelectorAll('input')].filter(i =>
                i.offsetParent !== null && /проверка всех url/i.test(i.getAttribute('aria-label')||''));
              if (!inps.length) return 'none';
              const inp = inps[0];
              inp.scrollIntoView({block:'center'});
              const rc = inp.getBoundingClientRect();
              return JSON.stringify({x: Math.round(rc.x + rc.width/2), y: Math.round(rc.y + rc.height/2)});
            })()
            """, "returnByValue": True})
            v = r.get("result", {}).get("value")
            if v == "none":
                print(f"{u}: no inspect bar"); continue
            b = json.loads(v)
            await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": b["x"], "y": b["y"], "button": "left", "clickCount": 1})
            await asyncio.sleep(0.05)
            await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": b["x"], "y": b["y"], "button": "left", "clickCount": 1})
            await asyncio.sleep(0.4)
            await call("Input.insertText", {"text": u})
            await asyncio.sleep(0.4)
            await call("Input.dispatchKeyEvent", {"type": "keyDown", "key": "Enter", "code": "Enter", "windowsVirtualKeyCode": 13})
            await call("Input.dispatchKeyEvent", {"type": "keyUp", "key": "Enter", "code": "Enter", "windowsVirtualKeyCode": 13})
            # ждать результата проверки
            status = "?"
            for _ in range(8):
                await asyncio.sleep(6)
                st = await call("Runtime.evaluate", {"expression": """
                (() => {
                  const t = document.body.innerText.replace(/\\s+/g,' ');
                  return JSON.stringify({
                    indexed: /url есть в google|url: в google|есть в google/i.test(t),
                    notIndexed: /url нет в google|нет в google/i.test(t),
                    requestBtn: [...document.querySelectorAll('*')].some(e => e.offsetParent !== null && e.children.length === 0 && /запросить индексирование/i.test((e.innerText||'').trim())),
                    snippet: t.slice(0, 250)
                  });
                })()
                """, "returnByValue": True})
                sv = json.loads(st.get("result", {}).get("value", "{}"))
                if sv.get("requestBtn") or sv.get("indexed") or sv.get("notIndexed"):
                    status = sv
                    break
            if isinstance(status, dict):
                if status.get("indexed"):
                    print(f"{u}: ALREADY INDEXED")
                elif status.get("requestBtn"):
                    # кликнуть кнопку запроса
                    rr = await call("Runtime.evaluate", {"expression": """
                    (() => {
                      const els = [...document.querySelectorAll('*')].filter(e =>
                        e.offsetParent !== null && e.children.length === 0 &&
                        /запросить индексирование/i.test((e.innerText||'').trim()) && (e.innerText||'').trim().length < 40);
                      const rc = els[0].getBoundingClientRect();
                      els[0].scrollIntoView({block:'center'});
                      return JSON.stringify({x: Math.round(rc.x + rc.width/2), y: Math.round(rc.y + rc.height/2)});
                    })()
                    """, "returnByValue": True})
                    rb = json.loads(rr.get("result", {}).get("value", "{}"))
                    await asyncio.sleep(0.5)
                    await call("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": rb["x"], "y": rb["y"]})
                    await asyncio.sleep(0.3)
                    await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": rb["x"], "y": rb["y"], "button": "left", "clickCount": 1})
                    await asyncio.sleep(0.1)
                    await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": rb["x"], "y": rb["y"], "button": "left", "clickCount": 1})
                    queued = False
                    for _ in range(7):
                        await asyncio.sleep(8)
                        st2 = await call("Runtime.evaluate", {"expression": """
                        (() => {
                          const t = document.body.innerText.replace(/\\s+/g,' ');
                          return /поставлен в очередь|запрос отправлен|индексирование запрошено/i.test(t);
                        })()
                        """, "returnByValue": True})
                        if st2.get("result", {}).get("value"):
                            queued = True
                            break
                    print(f"{u}: {'QUEUED' if queued else 'clicked, uncertain'}")
                else:
                    print(f"{u}: no request btn | {status.get('snippet','')[:120]}")
            else:
                print(f"{u}: TIMEOUT waiting inspection")

asyncio.run(main())
