# -*- coding: utf-8 -*-
"""Прямой DOM-клик по кнопке подтверждения + scrollIntoView."""
import json, asyncio, base64, urllib.request
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
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const els = [...document.querySelectorAll('button, div[role=button], a, span')].filter(e =>
            e.offsetParent !== null && /подтвердить право собственности/i.test((e.innerText||'').trim()) &&
            (e.innerText||'').trim().length < 40);
          if (!els.length) return 'none';
          // берём самый глубокий (последний вложенный)
          let el = els[els.length-1];
          // поднимаемся до кликабельного предка
          let target = el;
          for (let j = 0; j < 8 && target.parentElement; j++) {
            const cn = (target.className||'').toString();
            if (/U26fgb/.test(cn) || target.tagName === 'BUTTON' || target.getAttribute('role') === 'button') break;
            target = target.parentElement;
          }
          target.scrollIntoView({block:'center'});
          target.click();
          el.click();
          const rc = target.getBoundingClientRect();
          return JSON.stringify({clicked: true, x: Math.round(rc.x+rc.width/2), y: Math.round(rc.y+rc.height/2), tag: target.tagName});
        })()
        """, "returnByValue": True})
        print("CLICK:", r.get("result", {}).get("value"))
        await asyncio.sleep(7)
        st = await call("Runtime.evaluate", {"expression": """
        (() => JSON.stringify({url: location.href, text: document.body.innerText.replace(/\\s+/g,' ').slice(0, 600)}))()
        """, "returnByValue": True})
        print("AFTER:", st.get("result", {}).get("value"))
        shot = await call("Page.captureScreenshot", {"format": "png"})
        with open(r"C:\Users\Admin\fabrika\cmpsite\gsc-v3.png", "wb") as f:
            f.write(base64.b64decode(shot["data"]))
        print("SHOT")

asyncio.run(main())
