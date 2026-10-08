# -*- coding: utf-8 -*-
"""Запрос индексации ключевых страниц через «Проверка URL» в GSC."""
import json, asyncio, urllib.request
import websockets

PORT = 9229

URLS = [
    "https://stackpickr.vercel.app/",
    "https://stackpickr.vercel.app/hosting/",
    "https://stackpickr.vercel.app/affiliate-software/",
    "https://stackpickr.vercel.app/hosting/best-vps-providers/",
    "https://stackpickr.vercel.app/affiliate-software/best-affiliate-software/",
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
            base = "https://search.google.com/search-console/inspect?resource_id=https%3A%2F%2Fstackpickr.vercel.app%2F&id=" + urllib.parse.quote(u, safe="")
            await call("Page.navigate", {"url": base})
            await asyncio.sleep(13)
            # кнопка «ЗАПРОСИТЬ ИНДЕКСИРОВАНИЕ»
            r = await call("Runtime.evaluate", {"expression": """
            (() => {
              const els = [...document.querySelectorAll('*')].filter(e =>
                e.offsetParent !== null && e.children.length === 0 &&
                /запросить индексирование/i.test((e.innerText||'').trim()) && (e.innerText||'').trim().length < 40);
              if (!els.length) {
                return JSON.stringify({btn: 'none', text: document.body.innerText.replace(/\\s+/g,' ').slice(0,300)});
              }
              const rc = els[0].getBoundingClientRect();
              return JSON.stringify({btn: 'found', x: Math.round(rc.x + rc.width/2), y: Math.round(rc.y + rc.height/2)});
            })()
            """, "returnByValue": True})
            v = json.loads(r.get("result", {}).get("value", "{}"))
            if v.get("btn") != "found":
                print(f"{u}: BUTTON NOT FOUND | {v.get('text','')[:150]}")
                continue
            await call("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": v["x"], "y": v["y"]})
            await asyncio.sleep(0.3)
            await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": v["x"], "y": v["y"], "button": "left", "clickCount": 1})
            await asyncio.sleep(0.1)
            await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": v["x"], "y": v["y"], "button": "left", "clickCount": 1})
            # ждать диалог постановки в очередь
            done = False
            for _ in range(6):
                await asyncio.sleep(8)
                st = await call("Runtime.evaluate", {"expression": """
                (() => {
                  const t = document.body.innerText.replace(/\\s+/g,' ');
                  return JSON.stringify({queued: /поставлен в очередь|запрошено индексирование|запрос отправлен/i.test(t),
                    snippet: t.slice(0, 200)});
                })()
                """, "returnByValue": True})
                sv = json.loads(st.get("result", {}).get("value", "{}"))
                if sv.get("queued"):
                    done = True
                    break
            print(f"{u}: {'QUEUED' if done else 'uncertain — ' + sv.get('snippet','')[:120]}")

import urllib.parse
asyncio.run(main())
