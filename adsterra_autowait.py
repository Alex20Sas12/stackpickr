# -*- coding: utf-8 -*-
"""Свежий релоад + долгое ожидание авто-прохода челленджа + наблюдение за кнопкой."""
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
        await call("Page.navigate", {"url": "https://publishers.adsterra.com/login"})

        for i in range(12):
            await asyncio.sleep(5)
            st = await call("Runtime.evaluate", {"expression": """
            (() => {
              const btn = [...document.querySelectorAll('button')].find(b => /log in|авторизоваться/i.test((b.textContent||'').trim()));
              const hidden = document.querySelector('input[name="cloudflareCaptchaToken"]');
              const resp = window.turnstile ? window.turnstile.getResponse() : null;
              return JSON.stringify({btnDisabled: btn ? btn.disabled : null,
                tokenLen: hidden && hidden.value ? hidden.value.length : 0,
                respLen: resp ? String(resp).length : 0});
            })()
            """, "returnByValue": True})
            v = json.loads(st.get("result", {}).get("value", "{}"))
            print(f"t={ (i+1)*5 }s: btn={v.get('btnDisabled')} token={v.get('tokenLen')} resp={v.get('respLen')}")
            if v.get("btnDisabled") is False:
                print("BUTTON ENABLED!")
                # заполнить поля если пусты
                await call("Runtime.evaluate", {"expression": f"""
                (() => {{
                  const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;
                  const dispatch = (el) => {{ ['focus','input','change'].forEach(ev => el.dispatchEvent(new Event(ev, {{bubbles:true}}))); }};
                  const loginF = document.querySelector('input[name="login"]');
                  const passF = document.querySelector('input[name="signin"]') || document.querySelector('input[type="password"]');
                  if (loginF && !loginF.value) {{ setter.call(loginF, {json.dumps(login)}); dispatch(loginF); }}
                  if (passF && !passF.value) {{ setter.call(passF, {json.dumps(pwd)}); dispatch(passF); }}
                  return 'filled';
                }})()
                """, "returnByValue": True})
                await asyncio.sleep(1)
                r = await call("Runtime.evaluate", {"expression": """
                (() => {
                  const btn = [...document.querySelectorAll('button')].find(b => /log in|авторизоваться/i.test((b.textContent||'').trim()));
                  const rc = btn.getBoundingClientRect();
                  return JSON.stringify({x: rc.x + rc.width/2, y: rc.y + rc.height/2});
                })()
                """, "returnByValue": True})
                bpos = json.loads(r.get("result", {}).get("value", "{}"))
                await call("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": bpos["x"], "y": bpos["y"]})
                await asyncio.sleep(0.3)
                await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": bpos["x"], "y": bpos["y"], "button": "left", "clickCount": 1})
                await asyncio.sleep(0.12)
                await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": bpos["x"], "y": bpos["y"], "button": "left", "clickCount": 1})
                await asyncio.sleep(10)
                fin = await call("Runtime.evaluate", {"expression": """
                (() => JSON.stringify({url: location.href, title: document.title}))()
                """, "returnByValue": True})
                print("FINAL:", fin.get("result", {}).get("value"))
                return
        print("button never enabled in 60s")

asyncio.run(main())
