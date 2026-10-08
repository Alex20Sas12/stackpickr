# -*- coding: utf-8 -*-
"""Диагностика логина: значения полей + сабмит через Enter + ошибки."""
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

        # заполнить ПОЛНЫМ набором событий (React-совместимо)
        r = await call("Runtime.evaluate", {"expression": f"""
        (() => {{
          const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;
          const dispatch = (el) => {{
            ['focus','keydown','keypress','input','keyup','change','blur'].forEach(ev =>
              el.dispatchEvent(new Event(ev, {{bubbles:true}})));
          }};
          const loginF = document.querySelector('input[name="login"]');
          const passF = document.querySelector('input[name="signin"]') || document.querySelector('input[type="password"]');
          if (loginF) {{ setter.call(loginF, {json.dumps(login)}); dispatch(loginF); }}
          if (passF) {{ setter.call(passF, {json.dumps(pwd)}); dispatch(passF); }}
          return JSON.stringify({{loginVal: loginF ? loginF.value.slice(0,3)+'***len='+loginF.value.length : 'NOFIELD',
            passLen: passF ? passF.value.length : -1}});
        }})()
        """, "returnByValue": True})
        print("FILL:", r.get("result", {}).get("value"))
        await asyncio.sleep(1)
        # Enter на поле пароля
        await call("Runtime.evaluate", {"expression": """
        (() => {
          const passF = document.querySelector('input[type="password"]');
          if (passF) { passF.focus(); passF.dispatchEvent(new KeyboardEvent('keydown', {key:'Enter',code:'Enter',keyCode:13,which:13,bubbles:true})); }
          const b = [...document.querySelectorAll('button')].find(b => b.offsetParent !== null && /^Log in$/i.test((b.textContent||'').trim()));
          if (b) { b.dispatchEvent(new MouseEvent('click', {bubbles:true, cancelable:true, view:window})); }
          return 'sent';
        })()
        """, "returnByValue": True})
        await asyncio.sleep(11)
        st = await call("Runtime.evaluate", {"expression": """
        (() => {
          const errs = [...document.querySelectorAll('div,span,p')].filter(e => e.offsetParent !== null &&
            /invalid|incorrect|wrong|failed|ошибк|неверн/i.test(e.textContent||'') && (e.textContent||'').length < 150)
            .map(e => e.textContent.trim()).slice(0,3);
          return JSON.stringify({url: location.href, errs, snippet: document.body.innerText.replace(/\\s+/g,' ').slice(0,400)});
        })()
        """, "returnByValue": True})
        print("RESULT:", st.get("result", {}).get("value"))

asyncio.run(main())
