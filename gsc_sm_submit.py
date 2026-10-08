# -*- coding: utf-8 -*-
"""Активация кнопки ОТПРАВИТЬ: события ввода + Enter + клик."""
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
        # найти поле по aria
        await call("Runtime.evaluate", {"expression": """
        (() => {
          const inp = document.querySelector('input[aria-label="URL файла Sitemap"]');
          inp.scrollIntoView({block:'center'});
          inp.focus();
          inp.dispatchEvent(new Event('input', {bubbles:true}));
          inp.dispatchEvent(new Event('change', {bubbles:true}));
          return inp.value;
        })()
        """, "returnByValue": True})
        await asyncio.sleep(0.7)
        # Enter
        await call("Input.dispatchKeyEvent", {"type": "keyDown", "key": "Enter", "code": "Enter", "windowsVirtualKeyCode": 13})
        await call("Input.dispatchKeyEvent", {"type": "keyUp", "key": "Enter", "code": "Enter", "windowsVirtualKeyCode": 13})
        await asyncio.sleep(4)
        st = await call("Runtime.evaluate", {"expression": """
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
        b = json.loads(st.get("result", {}).get("value", "null"))
        print("SUBMIT:", b)
        # проверим результат — возможно, уже отправлено через Enter
        rows = await call("Runtime.evaluate", {"expression": """
        (() => {
          const trs = [...document.querySelectorAll('tr')].filter(tr => tr.offsetParent !== null);
          return JSON.stringify(trs.map(tr => (tr.innerText||'').replace(/\\s+/g,' ').slice(0,140)));
        })()
        """, "returnByValue": True})
        print("ROWS:", rows.get("result", {}).get("value"))

asyncio.run(main())
