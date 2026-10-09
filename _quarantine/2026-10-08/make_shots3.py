# -*- coding: utf-8 -*-
"""Доп. скриншоты: документация/датцентры/главные."""
import json, asyncio, base64, os, urllib.request
import websockets

PORT = 9222
OUT = r"C:\Users\Admin\fabrika\cmpsite\site\img"
SHOTS = [
    ("https://ishosting.com/en/datacenters", "ishosting-datacenters.png"),
    ("https://ishosting.com/en/payment-methods", "ishosting-payments.png"),
    ("https://tapfiliate.com/", "tapfiliate-home.png"),
    ("https://tapfiliate.com/integrations/", "tapfiliate-integrations.png"),
    ("https://support.cloudways.com/", "cloudways-docs.png"),
]

def new_tab(url):
    req = urllib.request.Request(f"http://localhost:{PORT}/json/new?{urllib.parse.quote(url, safe=':/')}", method="PUT")
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return json.load(r)
    except Exception:
        with urllib.request.urlopen(f"http://localhost:{PORT}/json/new?{url}", timeout=5) as r:
            return json.load(r)

def close_tab(tid):
    try:
        urllib.request.urlopen(f"http://localhost:{PORT}/json/close/{tid}", timeout=5)
    except Exception:
        pass

async def main():
    for url, fname in SHOTS:
        tab = new_tab("about:blank")
        ws_url = tab["webSocketDebuggerUrl"]; tid = tab["id"]
        try:
            async with websockets.connect(ws_url, max_size=60*1024*1024) as ws:
                _id = [1]
                async def call(method, params=None):
                    _id[0] += 1
                    await ws.send(json.dumps({"id": _id[0], "method": method, "params": params or {}}))
                    while True:
                        msg = json.loads(await ws.recv())
                        if msg.get("id") == _id[0]:
                            return msg.get("result", {})
                await call("Page.enable")
                await call("Emulation.setDeviceMetricsOverride", {"width": 1400, "height": 900, "deviceScaleFactor": 1, "mobile": False})
                await call("Page.navigate", {"url": url})
                await asyncio.sleep(13)
                await call("Runtime.evaluate", {"expression": """
                (() => {
                  const btns = [...document.querySelectorAll('button')].filter(b => b.offsetParent !== null);
                  const ok = btns.find(b => /^(OKAY|Accept|Accept all|Отклонить|Принять)$/i.test((b.textContent||'').trim()));
                  if (ok) { ok.click(); return 'closed'; } return 'none';
                })()
                """, "returnByValue": True})
                await asyncio.sleep(1.5)
                shot = await call("Page.captureScreenshot", {"format": "png"})
                fp = os.path.join(OUT, fname)
                with open(fp, "wb") as f:
                    f.write(base64.b64decode(shot["data"]))
                title = await call("Runtime.evaluate", {"expression": "document.title", "returnByValue": True})
                print(f"OK {fname} | {os.path.getsize(fp)//1024}KB | {title.get('result',{}).get('value','')[:70]}")
        finally:
            close_tab(tid)

asyncio.run(main())
