# -*- coding: utf-8 -*-
"""Клик 'Запросить индексирование' + ожидание постановки в очередь."""
import json, asyncio, base64, urllib.request
import websockets

PORT = 9229
SHOT_DIR = r"C:\Users\Admin\fabrika\cmpsite"

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
        # найти и кликнуть кнопку
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const els = [...document.querySelectorAll('*')].filter(e =>
            e.offsetParent !== null && e.children.length === 0 &&
            /запросить индексирование/i.test((e.innerText||'').trim()) && (e.innerText||'').trim().length < 40);
          if (!els.length) return 'none';
          els[0].scrollIntoView({block:'center'});
          return JSON.stringify(els.map(e => {
            const rc = e.getBoundingClientRect();
            return {x: Math.round(rc.x + rc.width/2), y: Math.round(rc.y + rc.height/2)};
          }));
        })()
        """, "returnByValue": True})
        v = r.get("result", {}).get("value")
        print("BTN:", v)
        if v == "none":
            return
        btns = json.loads(v)
        b = btns[0]
        await asyncio.sleep(0.7)
        # после scrollIntoView пересчитать координаты
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const els = [...document.querySelectorAll('*')].filter(e =>
            e.offsetParent !== null && e.children.length === 0 &&
            /запросить индексирование/i.test((e.innerText||'').trim()) && (e.innerText||'').trim().length < 40);
          const rc = els[0].getBoundingClientRect();
          return JSON.stringify({x: Math.round(rc.x + rc.width/2), y: Math.round(rc.y + rc.height/2)});
        })()
        """, "returnByValue": True})
        b = json.loads(r.get("result", {}).get("value"))
        print("BTN after scroll:", b)
        await call("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": b["x"], "y": b["y"]})
        await asyncio.sleep(0.4)
        await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": b["x"], "y": b["y"], "button": "left", "clickCount": 1})
        await asyncio.sleep(0.1)
        await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": b["x"], "y": b["y"], "button": "left", "clickCount": 1})
        # ждать диалог (проверка URL -> постановка в очередь занимает до 2 мин)
        for i in range(16):
            await asyncio.sleep(8)
            st = await call("Runtime.evaluate", {"expression": """
            (() => {
              const t = document.body.innerText.replace(/\\s+/g,' ');
              return JSON.stringify({
                queued: /поставлен в очередь|запрос отправлен|индексирование запрошено/i.test(t),
                testing: /проверка|тестируем|ожидайте|живой тест/i.test(t),
                snippet: t.slice(0, 250)
              });
            })()
            """, "returnByValue": True})
            sv = json.loads(st.get("result", {}).get("value", "{}"))
            print(f"t={8*(i+1)}s: queued={sv.get('queued')} testing={sv.get('testing')} | {sv.get('snippet','')[:120]}")
            if sv.get("queued"):
                break
        s = await call("Page.captureScreenshot", {"format": "png"})
        with open(f"{SHOT_DIR}\\ins-queued.png", "wb") as f:
            f.write(base64.b64decode(s["data"]))
        print("shot saved")

asyncio.run(main())
