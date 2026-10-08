# -*- coding: utf-8 -*-
"""Закрыть подсказку и кликнуть 'Запросить индексирование'."""
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
        # закрыть все подсказки
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          let n = 0;
          const els = [...document.querySelectorAll('*')].filter(e =>
            e.offsetParent !== null && e.children.length === 0 &&
            (e.innerText||'').trim() === 'Закрыть' && (e.innerText||'').trim().length < 10);
          for (const e of els) { e.click(); n++; }
          return 'closed=' + n;
        })()
        """, "returnByValue": True})
        print("TOOLTIPS:", r.get("result", {}).get("value"))
        await asyncio.sleep(2)
        # кликнуть запрос индексирования
        r2 = await call("Runtime.evaluate", {"expression": """
        (() => {
          const els = [...document.querySelectorAll('*')].filter(e =>
            e.offsetParent !== null && e.children.length === 0 &&
            /запросить индексирование/i.test((e.innerText||'').trim()) && (e.innerText||'').trim().length < 40);
          if (!els.length) return 'none';
          els[0].scrollIntoView({block:'center'});
          return 'found';
        })()
        """, "returnByValue": True})
        print("FIND:", r2.get("result", {}).get("value"))
        if r2.get("result", {}).get("value") == "none":
            return
        await asyncio.sleep(0.7)
        r3 = await call("Runtime.evaluate", {"expression": """
        (() => {
          const els = [...document.querySelectorAll('*')].filter(e =>
            e.offsetParent !== null && e.children.length === 0 &&
            /запросить индексирование/i.test((e.innerText||'').trim()) && (e.innerText||'').trim().length < 40);
          const rc = els[0].getBoundingClientRect();
          return JSON.stringify({x: Math.round(rc.x + rc.width/2), y: Math.round(rc.y + rc.height/2)});
        })()
        """, "returnByValue": True})
        b = json.loads(r3.get("result", {}).get("value"))
        print("BTN:", b)
        await call("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": b["x"], "y": b["y"]})
        await asyncio.sleep(0.4)
        await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": b["x"], "y": b["y"], "button": "left", "clickCount": 1})
        await asyncio.sleep(0.1)
        await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": b["x"], "y": b["y"], "button": "left", "clickCount": 1})
        # ждать результат (может занять до 2-3 минут: живой тест + очередь)
        for i in range(20):
            await asyncio.sleep(8)
            st = await call("Runtime.evaluate", {"expression": """
            (() => {
              const t = document.body.innerText.replace(/\\s+/g,' ');
              return JSON.stringify({
                queued: /поставлен в очередь|запрос отправлен|индексирование запрошено|запрошено индексирование/i.test(t),
                snippet: t.slice(0, 220)
              });
            })()
            """, "returnByValue": True})
            sv = json.loads(st.get("result", {}).get("value", "{}"))
            print(f"t={8*(i+1)}s: queued={sv.get('queued')}")
            if sv.get("queued"):
                print("QUEUED!")
                break
        s = await call("Page.captureScreenshot", {"format": "png"})
        with open(f"{SHOT_DIR}\\ins-final.png", "wb") as f:
            f.write(base64.b64decode(s["data"]))
        print("shot saved")

asyncio.run(main())
