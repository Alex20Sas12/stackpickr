# -*- coding: utf-8 -*-
"""Диагностика диалога добавления ресурса: что видимо."""
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
          const dlg = document.querySelector('[role=dialog], .modal-dialog, [class*=dialog]');
          const vis = dlg ? dlg.offsetParent !== null : false;
          // все видимые инпуты с ненулевой шириной
          const inps = [...document.querySelectorAll('input')].map(i => {
            const rc = i.getBoundingClientRect();
            return {x: Math.round(rc.x), y: Math.round(rc.y), w: Math.round(rc.width),
                    h: Math.round(rc.height), type: i.type, ph: i.placeholder||'',
                    aria: (i.getAttribute('aria-label')||'').slice(0,40), visible: i.offsetParent !== null};
          });
          return JSON.stringify({dialogVisible: vis, inps});
        })()
        """, "returnByValue": True})
        v = json.loads(r.get("result", {}).get("value", "{}"))
        print("DIALOG VISIBLE:", v.get("dialogVisible"))
        for i in v.get("inps", []):
            print(i)
        shot = await call("Page.captureScreenshot", {"format": "png"})
        with open(r"C:\Users\Admin\fabrika\cmpsite\gsc-dialog.png", "wb") as f:
            f.write(base64.b64decode(shot["data"]))
        print("SHOT SAVED")

asyncio.run(main())
