# -*- coding: utf-8 -*-
"""GSC: закрыть попапы + кликнуть селектор ресурса."""
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
    if not ws_url:
        print("NO TAB"); return
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
        # 1. закрыть обучающие попапы
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          let closed = 0;
          const els = [...document.querySelectorAll('button, [role=button]')].filter(e =>
            e.offsetParent !== null && /закрыть|закры|закрыть|закрыть|закрыть|закрыть/.test((e.innerText||'').trim()) && (e.innerText||'').trim().length < 12);
          for (const x of els) { x.click(); closed++; }
          // крестики без текста
          const xs = [...document.querySelectorAll('[aria-label="Закрыть"], [aria-label="Закрыть окно"], [aria-label*="Закрыть"]')]
            .filter(e => e.offsetParent !== null);
          for (const x of xs) { x.click(); closed++; }
          return 'closed=' + closed;
        })()
        """, "returnByValue": True})
        print("CLOSE:", r.get("result", {}).get("value"))
        await asyncio.sleep(1.5)

        # 2. DOM-поиск селектора ресурса
        r2 = await call("Runtime.evaluate", {"expression": """
        (() => {
          const all = [...document.querySelectorAll('*')];
          const sel = all.find(e => e.offsetParent !== null &&
            (['listbox','menu','true'].includes(e.getAttribute('aria-haspopup')) || e.getAttribute('role') === 'combobox') &&
            /shablony|ресурс|сайт/.test((e.innerText||'') + (e.getAttribute('aria-label')||'')));
          if (!sel) return JSON.stringify({found: false});
          const rc = sel.getBoundingClientRect();
          return JSON.stringify({found: true, tag: sel.tagName,
            x: Math.round(rc.x + rc.width/2), y: Math.round(rc.y + rc.height/2),
            aria: sel.getAttribute('aria-haspopup'), role: sel.getAttribute('role')});
        })()
        """, "returnByValue": True})
        v = json.loads(r2.get("result", {}).get("value", "{}"))
        print("SELECTOR:", v)
        if not v.get("found"):
            # фолбэк: клик по координатам стрелки со скриншота
            v = {"x": 231, "y": 140}
            print("FALLBACK coords:", v)
        await call("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": v["x"], "y": v["y"]})
        await asyncio.sleep(0.3)
        await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": v["x"], "y": v["y"], "button": "left", "clickCount": 1})
        await asyncio.sleep(0.1)
        await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": v["x"], "y": v["y"], "button": "left", "clickCount": 1})
        await asyncio.sleep(3)
        r3 = await call("Runtime.evaluate", {"expression": """
        (() => {
          const els = [...document.querySelectorAll('*')].filter(e =>
            e.offsetParent !== null && e.children.length === 0 &&
            /добавить ресурс|добавить сайт|выбрать ресурс|выбрать сайт|все ресурсы|управление ресурсами/.test(e.innerText||''));
          return JSON.stringify(els.slice(0,8).map(e => {
            const rc = e.getBoundingClientRect();
            return {tag: e.tagName, text: (e.innerText||'').trim().slice(0,60),
                    x: Math.round(rc.x + rc.width/2), y: Math.round(rc.y + rc.height/2)};
          }));
        })()
        """, "returnByValue": True})
        print("MENU:", r3.get("result", {}).get("value"))

asyncio.run(main())
