# -*- coding: utf-8 -*-
"""Повтор логина: закрыть куки, ввести LOGIN (не email), проверить ошибки."""
import json, asyncio, os, re, urllib.request
import websockets

PORT = 9222

def creds():
    txt = open(os.path.expanduser("~/.bashrc"), encoding="utf-8").read()
    def g(n):
        m = re.search(rf"{n}=[\"']?([^\"'\n]+)", txt)
        return m.group(1).strip() if m else None
    return g("ADSTERRA_LOGIN"), g("ADSTERRA_EMAIL"), g("ADSTERRA_PASSWORD")

def get_tabs():
    with urllib.request.urlopen(f"http://localhost:{PORT}/json", timeout=5) as r:
        return json.load(r)

async def main():
    login, email, pwd = creds()
    tabs = get_tabs()
    ws_url = None
    for t in tabs:
        if t.get("type") == "page" and "adsterra" in t.get("url", ""):
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
        await call("Page.enable")

        # закрыть куки-баннер
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const b = [...document.querySelectorAll('button')].find(b => b.offsetParent !== null && /^Allow all$/i.test((b.textContent||'').trim()));
          if (b) { b.click(); return 'cookies-allowed'; }
          return 'no-banner';
        })()
        """, "returnByValue": True})
        print("COOKIES:", r.get("result", {}).get("value"))
        await asyncio.sleep(2)

        await call("Page.navigate", {"url": "https://publishers.adsterra.com/login"})
        await asyncio.sleep(9)
        # закрыть баннер ещё раз если появился
        await call("Runtime.evaluate", {"expression": """
        (() => {
          const b = [...document.querySelectorAll('button')].find(b => b.offsetParent !== null && /^Allow all$/i.test((b.textContent||'').trim()));
          if (b) { b.click(); return 'ok'; } return 'none';
        })()
        """, "returnByValue": True})
        await asyncio.sleep(1)

        # заполнить: поле login = ЛОГИН, пароль = пароль
        r = await call("Runtime.evaluate", {"expression": f"""
        (() => {{
          const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;
          const loginF = document.querySelector('input[name="login"]');
          const passF = document.querySelector('input[name="signin"]') || document.querySelector('input[type="password"]');
          const out = [];
          if (loginF) {{ setter.call(loginF, {json.dumps(login)}); loginF.dispatchEvent(new Event('input',{{bubbles:true}})); out.push('login'); }}
          if (passF) {{ setter.call(passF, {json.dumps(pwd)}); passF.dispatchEvent(new Event('input',{{bubbles:true}})); out.push('pass'); }}
          return out.join(',');
        }})()
        """, "returnByValue": True})
        print("FILLED:", r.get("result", {}).get("value"))
        await asyncio.sleep(1)
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const b = [...document.querySelectorAll('button')].find(b => b.offsetParent !== null && /^Log in$/i.test((b.textContent||'').trim()));
          if (b) { b.click(); return 'clicked'; }
          return 'no-btn';
        })()
        """, "returnByValue": True})
        print("SUBMIT:", r.get("result", {}).get("value"))
        await asyncio.sleep(10)
        st = await call("Runtime.evaluate", {"expression": """
        (() => {
          const err = [...document.querySelectorAll('[class*=error], [class*=invalid], [role=alert]')]
            .map(e => e.textContent.trim()).filter(Boolean).join(' | ');
          return JSON.stringify({url: location.href, title: document.title, err: err.slice(0,300),
            text: document.body.innerText.replace(/\\s+/g,' ').slice(0,300)});
        })()
        """, "returnByValue": True})
        print("AFTER:", st.get("result", {}).get("value"))

asyncio.run(main())
