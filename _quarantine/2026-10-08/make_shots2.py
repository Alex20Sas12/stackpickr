# -*- coding: utf-8 -*-
"""Скриншоты с принудительными кукисами языка (до навигации)."""
import json, asyncio, base64, os, urllib.request
import websockets

PORT = 9222
OUT = r"C:\Users\Admin\fabrika\cmpsite\site\img"
SHOTS = [
    ([("cwLang", "en", "www.cloudways.com")], "https://www.cloudways.com/en/", "cloudways-home.png"),
    ([("cwLang", "en", "www.cloudways.com")], "https://www.cloudways.com/en/pricing.php", "cloudways-pricing.png"),
    ([("X-Default-Language", "en", "ishosting.com")], "https://ishosting.com/en", "ishosting-home.png"),
    ([("X-Default-Language", "en", "ishosting.com")], "https://ishosting.com/en/vps", "ishosting-vps.png"),
    ([], "https://tapfiliate.com/pricing/", "tapfiliate-pricing.png"),
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
    for cookies, url, fname in SHOTS:
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
                await call("Network.enable")
                await call("Network.setExtraHTTPHeaders", {"headers": {"Accept-Language": "en-US,en;q=0.9"}})
                for name, value, domain in cookies:
                    await call("Network.setCookie", {"name": name, "value": value, "domain": domain, "path": "/"})
                await call("Emulation.setDeviceMetricsOverride", {"width": 1400, "height": 900, "deviceScaleFactor": 1, "mobile": False})
                await call("Page.navigate", {"url": url})
                await asyncio.sleep(13)
                # если всё ещё не английский — ставим куки из контекста страницы и перезагружаем
                lang = await call("Runtime.evaluate", {"expression": "document.documentElement.lang + '|' + document.title.slice(0,30)", "returnByValue": True})
                cur = lang.get("result", {}).get("value", "")
                if "en" not in cur.lower()[:4]:
                    await call("Runtime.evaluate", {"expression": "document.cookie='cwLang=en; path=/'; document.cookie='X-Default-Language=en; path=/'; 1"})
                    await call("Page.navigate", {"url": url})
                    await asyncio.sleep(10)
                await call("Runtime.evaluate", {"expression": """
                (() => {
                  const btns = [...document.querySelectorAll('button')].filter(b => b.offsetParent !== null);
                  const ok = btns.find(b => /^(OKAY|Accept|Accept all)$/i.test((b.textContent||'').trim()));
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
