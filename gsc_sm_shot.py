# -*- coding: utf-8 -*-
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
        await call("Page.enable")
        await call("Runtime.evaluate", {"expression": """
        (() => {
          const inp = document.querySelector('input[aria-label="URL файла Sitemap"]');
          if (inp) inp.scrollIntoView({block:'center'});
          return 1;
        })()
        """, "returnByValue": True})
        await asyncio.sleep(1)
        shot = await call("Page.captureScreenshot", {"format": "png"})
        with open(r"C:\Users\Admin\fabrika\cmpsite\gsc-sm.png", "wb") as f:
            f.write(base64.b64decode(shot["data"]))
        from PIL import Image
        im = Image.open(r"C:\Users\Admin\fabrika\cmpsite\gsc-sm.png")
        im = im.resize((im.width//2, im.height//2))
        im.save(r"C:\Users\Admin\fabrika\cmpsite\gsc-sm-small.jpg", quality=72)
        print("SHOT")

asyncio.run(main())
