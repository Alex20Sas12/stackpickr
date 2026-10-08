# -*- coding: utf-8 -*-
"""Скриншоты страниц продуктов через реальный браузер (порт 9222) — проходит антибот."""
import json, asyncio, base64, os, urllib.request
import websockets

PORT = 9222
OUT = r"C:\Users\Admin\fabrika\cmpsite\site\img"
SHOTS = [
    ("https://www.cloudways.com/en/", "cloudways-home.png"),
    ("https://www.cloudways.com/en/pricing.php?lang=en", "cloudways-pricing.png"),
    ("https://ishosting.com/en", "ishosting-home.png"),
    ("https://ishosting.com/en/vps?lang=en", "ishosting-vps.png"),
    ("https://tapfiliate.com/pricing/", "tapfiliate-pricing.png"),
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
        ws_url = tab["webSocketDebuggerUrl"]
        tid = tab["id"]
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
                await call("Network.enable")
                await call("Network.setExtraHTTPHeaders", {"headers": {"Accept-Language": "en-US,en;q=0.9"}})
                await call("Emulation.setDeviceMetricsOverride", {"width": 1400, "height": 900, "deviceScaleFactor": 1, "mobile": False})
                await call("Page.navigate", {"url": url})
                await asyncio.sleep(12)  # антибот-чек проходит за это время
                # перезагрузка: куки языка (cwLang / X-Default-Language) уже встали на en
                await call("Page.navigate", {"url": url})
                await asyncio.sleep(9)
                # скролл вниз-вверх чтобы прогрузить картинки
                await call("Runtime.evaluate", {"expression": "window.scrollTo(0, 300); window.scrollTo(0, 0); 1"})
                await asyncio.sleep(2)
                # закрыть куки-баннер если есть
                await call("Runtime.evaluate", {"expression": """
                (() => {
                  const btns = [...document.querySelectorAll('button')].filter(b => b.offsetParent !== null);
                  const ok = btns.find(b => /^(OKAY|Accept|Accept all|Принять|Согласиться)$/i.test((b.textContent||'').trim()));
                  if (ok) { ok.click(); return 'closed'; }
                  return 'none';
                })()
                """, "returnByValue": True})
                await asyncio.sleep(1.5)
                shot = await call("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": False})
                fp = os.path.join(OUT, fname)
                with open(fp, "wb") as f:
                    f.write(base64.b64decode(shot["data"]))
                title = await call("Runtime.evaluate", {"expression": "document.title", "returnByValue": True})
                print(f"OK {fname} | {os.path.getsize(fp)//1024}KB | {title.get('result',{}).get('value','')[:60]}")
        finally:
            close_tab(tid)

asyncio.run(main())
