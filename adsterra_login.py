# -*- coding: utf-8 -*-
"""Логин в Adsterra publisher-кабинет (порт 9222, вкладка уже есть)."""
import json, asyncio, os, re, subprocess, urllib.request
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
    if not ws_url:
        print("NO ADSTERRA TAB"); return
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
        await call("Page.navigate", {"url": "https://publishers.adsterra.com/login"})
        await asyncio.sleep(9)
        st = await call("Runtime.evaluate", {"expression": """
        (() => {
          const inps = [...document.querySelectorAll('input')].filter(i => i.offsetParent !== null)
            .map(i => ({name:i.name||'',type:i.type||'',ph:i.placeholder||''}));
          const btns = [...document.querySelectorAll('button')].filter(b => b.offsetParent !== null)
            .map(b => (b.textContent||'').trim()).filter(Boolean);
          return JSON.stringify({url: location.href, inps, btns});
        })()
        """, "returnByValue": True})
        print("STATE:", st.get("result", {}).get("value"))

        # заполняем логин+пароль
        r = await call("Runtime.evaluate", {"expression": f"""
        (() => {{
          const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;
          const inps = [...document.querySelectorAll('input')].filter(i => i.offsetParent !== null);
          const user = inps.find(i => /email|login|user/i.test(i.name+i.placeholder+i.type));
          const pass = inps.find(i => i.type === 'password');
          let filled = [];
          if (user) {{ setter.call(user, {json.dumps(email)}); user.dispatchEvent(new Event('input',{{bubbles:true}})); filled.push('user'); }}
          if (pass) {{ setter.call(pass, {json.dumps(pwd)}); pass.dispatchEvent(new Event('input',{{bubbles:true}})); filled.push('pass'); }}
          return filled.join(',');
        }})()
        """, "returnByValue": True})
        print("FILLED:", r.get("result", {}).get("value"))
        await asyncio.sleep(1)
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const b = [...document.querySelectorAll('button')].find(b => b.offsetParent !== null && /log|войти|вход|sign/i.test(b.textContent||''));
          if (b) { b.click(); return 'clicked: ' + b.textContent.trim(); }
          return 'no button';
        })()
        """, "returnByValue": True})
        print("SUBMIT:", r.get("result", {}).get("value"))
        await asyncio.sleep(9)
        st2 = await call("Runtime.evaluate", {"expression": """
        (() => {
          const inps = [...document.querySelectorAll('input')].filter(i => i.offsetParent !== null)
            .map(i => ({name:i.name||'',type:i.type||'',ph:i.placeholder||''}));
          return JSON.stringify({url: location.href, title: document.title, inps,
            text: document.body.innerText.slice(0,300).replace(/\\s+/g,' ')});
        })()
        """, "returnByValue": True})
        print("AFTER:", st2.get("result", {}).get("value"))

asyncio.run(main())
