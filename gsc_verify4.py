# -*- coding: utf-8 -*-
"""Точный клик по кнопке ПОДТВЕРДИТЬ ПРАВО СОБСТВЕННОСТИ."""
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
        # все элементы с текстом, их координаты
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const els = [...document.querySelectorAll('*')].filter(e =>
            e.offsetParent !== null && e.children.length === 0 &&
            /подтвердить право собственности/i.test((e.innerText||'').trim()));
          return JSON.stringify(els.map(e => {
            const rc = e.getBoundingClientRect();
            return {tag: e.tagName, cls: (e.className||'').toString().slice(0,50),
                    x: Math.round(rc.x + rc.width/2), y: Math.round(rc.y + rc.height/2),
                    w: Math.round(rc.width), h: Math.round(rc.height), vh: window.innerHeight};
          }));
        })()
        """, "returnByValue": True})
        els = json.loads(r.get("result", {}).get("value", "[]"))
        print("CANDS:", json.dumps(els, indent=1))
        if not els:
            return
        el = els[0]
        # если за пределами вьюпорта — скроллим
        if el["y"] > el["vh"] - 50 or el["y"] < 0:
            await call("Runtime.evaluate", {"expression": """
            (() => {
              const els = [...document.querySelectorAll('*')].filter(e =>
                e.offsetParent !== null && e.children.length === 0 &&
                /подтвердить право собственности/i.test((e.innerText||'').trim()));
              els[0].scrollIntoView({block:'center'});
              return 1;
            })()
            """, "returnByValue": True})
            await asyncio.sleep(1)
            r = await call("Runtime.evaluate", {"expression": """
            (() => {
              const els = [...document.querySelectorAll('*')].filter(e =>
                e.offsetParent !== null && e.children.length === 0 &&
                /подтвердить право собственности/i.test((e.innerText||'').trim()));
              const rc = els[0].getBoundingClientRect();
              return JSON.stringify({x: Math.round(rc.x + rc.width/2), y: Math.round(rc.y + rc.height/2)});
            })()
            """, "returnByValue": True})
            el = json.loads(r.get("result", {}).get("value", "{}"))
            print("AFTER SCROLL:", el)
        await call("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": el["x"], "y": el["y"]})
        await asyncio.sleep(0.4)
        await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": el["x"], "y": el["y"], "button": "left", "clickCount": 1})
        await asyncio.sleep(0.1)
        await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": el["x"], "y": el["y"], "button": "left", "clickCount": 1})
        await asyncio.sleep(7)
        st = await call("Runtime.evaluate", {"expression": """
        (() => JSON.stringify({url: location.href, text: document.body.innerText.replace(/\\s+/g,' ').slice(0, 500)}))()
        """, "returnByValue": True})
        print("AFTER:", st.get("result", {}).get("value"))
        shot = await call("Page.captureScreenshot", {"format": "png"})
        with open(r"C:\Users\Admin\fabrika\cmpsite\gsc-v4.png", "wb") as f:
            f.write(base64.b64decode(shot["data"]))
        from PIL import Image
        im = Image.open(r"C:\Users\Admin\fabrika\cmpsite\gsc-v4.png")
        im = im.resize((im.width//2, im.height//2))
        im.save(r"C:\Users\Admin\fabrika\cmpsite\gsc-v4-small.jpg", quality=72)
        print("SHOT")

asyncio.run(main())
