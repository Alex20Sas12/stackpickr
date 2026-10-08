# -*- coding: utf-8 -*-
"""Ввод стека в правое поле диалога (префиксный ресурс) + ПРОДОЛЖИТЬ."""
import json, asyncio, urllib.request
import websockets

PORT = 9229
URL = "https://stackpickr.vercel.app/"

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
        # найти правое поле (префиксный ресурс): видимое, в правой половине диалога
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const inps = [...document.querySelectorAll('input')].filter(i => i.offsetParent !== null && i.getBoundingClientRect().width > 100);
          return JSON.stringify(inps.map(i => {
            const rc = i.getBoundingClientRect();
            return {x: Math.round(rc.x), y: Math.round(rc.y), w: Math.round(rc.width), ph: i.placeholder||''};
          }));
        })()
        """, "returnByValue": True})
        inps = json.loads(r.get("result", {}).get("value", "[]"))
        print("INPUTS:", inps)
        # правое поле: то, что справа от центра (~480) и с плейсхолдером про URL
        right = [i for i in inps if i["x"] > 480 and "example" in i.get("ph", "").lower() or (i["x"] > 560 and i["w"] > 200)]
        # если не нашлось по фильтру, берём самый правый широкий
        if not right:
            wide = [i for i in inps if i["w"] > 200]
            right = [max(wide, key=lambda i: i["x"])] if wide else []
        if not right:
            print("NO RIGHT INPUT"); return
        tgt = right[0]
        print("TARGET:", tgt)
        # сфокусировать и ввести
        cx, cy = tgt["x"] + tgt["w"] // 2, tgt["y"] + 20
        await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": cx, "y": cy, "button": "left", "clickCount": 1})
        await asyncio.sleep(0.1)
        await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": cx, "y": cy, "button": "left", "clickCount": 1})
        await asyncio.sleep(0.5)
        await call("Runtime.evaluate", {"expression": """
        (() => {
          const inps = [...document.querySelectorAll('input')].filter(i => i.offsetParent !== null && i.getBoundingClientRect().width > 100);
          const wide = inps.filter(i => i.getBoundingClientRect().width > 200);
          const tgt = wide.sort((a,b) => b.getBoundingClientRect().x - a.getBoundingClientRect().x)[0];
          if (tgt) { tgt.scrollIntoView({block:'center'}); tgt.focus(); tgt.click(); }
          return tgt ? 'focused' : 'none';
        })()
        """, "returnByValue": True})
        await asyncio.sleep(0.5)
        await call("Input.insertText", {"text": URL})
        await asyncio.sleep(1.5)
        # проверить значение
        st = await call("Runtime.evaluate", {"expression": """
        (() => {
          const inps = [...document.querySelectorAll('input')].filter(i => i.offsetParent !== null && i.getBoundingClientRect().width > 200);
          return JSON.stringify(inps.map(i => ({x: Math.round(i.getBoundingClientRect().x), val: i.value})));
        })()
        """, "returnByValue": True})
        print("VALUES:", st.get("result", {}).get("value"))
        # найти кнопку ПРОДОЛЖИТЬ для правой секции и проверить её состояние
        r2 = await call("Runtime.evaluate", {"expression": """
        (() => {
          const spans = [...document.querySelectorAll('span')].filter(e =>
            (e.innerText||'').trim() === 'ПРОДОЛЖИТЬ' && e.children.length === 0);
          const out = [];
          for (const sp of spans) {
            let el = sp;
            for (let j = 0; j < 8 && el.parentElement; j++) {
              if (/U26fgb/.test(el.className || '')) {
                const rc = el.getBoundingClientRect();
                out.push({x: Math.round(rc.x + rc.width/2), y: Math.round(rc.y + rc.height/2),
                          disabled: /RDPZE/.test(el.className||'') || el.getAttribute('aria-disabled') === 'true'});
                break;
              }
              el = el.parentElement;
            }
          }
          return JSON.stringify(out);
        })()
        """, "returnByValue": True})
        btns = json.loads(r2.get("result", {}).get("value", "[]"))
        print("CONTINUE BTNS:", btns)

asyncio.run(main())
