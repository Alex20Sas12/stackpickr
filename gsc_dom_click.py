# -*- coding: utf-8 -*-
"""Прямой DOM-клик по селектору ресурса (поиск по тексту)."""
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
        # найти все элементы с текстом ресурса и кликнуть каждый родительский кликабельный
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const txts = [...document.querySelectorAll('*')].filter(e =>
            e.children.length === 0 && /shablony-pro/.test(e.innerText||''));
          const info = txts.map(e => {
            const rc = e.getBoundingClientRect();
            return {tag: e.tagName, cls: (e.className||'').toString().slice(0,40),
                    x: Math.round(rc.x+rc.width/2), y: Math.round(rc.y+rc.height/2), w: Math.round(rc.width)};
          });
          if (txts.length) {
            // поднимаемся до кликабельного предка
            let el = txts[0];
            for (let i = 0; i < 10 && el; i++) {
              if (el.tagName === 'BUTTON' || el.getAttribute('role') === 'button' ||
                  (el.className||'').toString().match(/clickable|U26fgb|selector/i) ||
                  el.onclick || el.tagName === 'A') break;
              el = el.parentElement;
            }
            if (el) { el.click(); }
          }
          return JSON.stringify({found: info, clicked: !!txts.length});
        })()
        """, "returnByValue": True})
        print("CLICK:", r.get("result", {}).get("value"))
        await asyncio.sleep(3)
        r3 = await call("Runtime.evaluate", {"expression": """
        (() => {
          const els = [...document.querySelectorAll('*')].filter(e =>
            e.offsetParent !== null && e.children.length === 0 &&
            /добавить ресурс|добавить сайт|выбрать ресурс|выбрать сайт|все ресурсы|управление ресурсами|управление свойствами|выбрать свойство/.test(e.innerText||''));
          return JSON.stringify(els.slice(0,8).map(e => {
            const rc = e.getBoundingClientRect();
            return {tag: e.tagName, text: (e.innerText||'').trim().slice(0,60),
                    x: Math.round(rc.x + rc.width/2), y: Math.round(rc.y + rc.height/2)};
          }));
        })()
        """, "returnByValue": True})
        print("MENU:", r3.get("result", {}).get("value"))

asyncio.run(main())
