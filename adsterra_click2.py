# -*- coding: utf-8 -*-
"""Поиск видимого текста капчи + последовательные клики по кандидатам чекбокса."""
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
        await asyncio.sleep(12)

        # где виден текст капчи?
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const all = [...document.querySelectorAll('*')];
          const hits = all.filter(e => e.offsetParent !== null &&
            /подтвердите|verify you are human|я человек|confirm you/i.test(e.textContent || '') &&
            (e.textContent || '').length < 100);
          return JSON.stringify(hits.slice(0,5).map(e => {
            const rc = e.getBoundingClientRect();
            return {tag: e.tagName, text: e.textContent.trim().slice(0,60), x: Math.round(rc.x), y: Math.round(rc.y), w: Math.round(rc.width), h: Math.round(rc.height)};
          }));
        })()
        """, "returnByValue": True})
        print("CAPTCHA TEXT:", r.get("result", {}).get("value"))

        # кандидаты клика: чекбокс слева внутри виджета
        cont = await call("Runtime.evaluate", {"expression": """
        (() => {
          const el = document.getElementById('cf-turnstile');
          const rc = el.getBoundingClientRect();
          return JSON.stringify({x: rc.x, y: rc.y, w: rc.width, h: rc.height});
        })()
        """, "returnByValue": True})
        c = json.loads(cont.get("result", {}).get("value", "{}"))
        print("CONTAINER:", c)

        candidates = []
        if c.get("w"):
            # виджет 300px центрирован: старт = x + (w-300)/2
            wx = c["x"] + (c["w"] - 300) / 2
            wy = c["y"] + c["h"] / 2
            candidates = [(wx + 32, wy), (c["x"] + 32, wy), (wx + 28, wy - 5), (wx + 150, wy)]
        for cx, cy in candidates:
            print(f"click {cx:.0f},{cy:.0f}")
            await call("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": cx, "y": cy})
            await asyncio.sleep(0.5)
            await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": cx, "y": cy, "button": "left", "clickCount": 1})
            await asyncio.sleep(0.15)
            await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": cx, "y": cy, "button": "left", "clickCount": 1})
            await asyncio.sleep(6)
            st = await call("Runtime.evaluate", {"expression": """
            (() => {
              const btn = [...document.querySelectorAll('button')].find(b => /log in|авторизоваться/i.test((b.textContent||'').trim()));
              const hidden = document.querySelector('input[name="cloudflareCaptchaToken"]');
              const resp = window.turnstile ? window.turnstile.getResponse() : null;
              return JSON.stringify({btnDisabled: btn ? btn.disabled : null, tokenLen: hidden && hidden.value ? hidden.value.length : 0});
            })()
            """, "returnByValue": True})
            v = json.loads(st.get("result", {}).get("value", "{}"))
            print("  ->", v)
            if v.get("btnDisabled") is False or v.get("tokenLen", 0) > 0:
                print("CAPTCHA PASSED")
                # заполнить и войти
                await call("Runtime.evaluate", {"expression": f"""
                (() => {{
                  const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;
                  const dispatch = (el) => {{ ['focus','input','change'].forEach(ev => el.dispatchEvent(new Event(ev, {{bubbles:true}}))); }};
                  const loginF = document.querySelector('input[name="login"]');
                  const passF = document.querySelector('input[name="signin"]') || document.querySelector('input[type="password"]');
                  if (loginF) {{ setter.call(loginF, {json.dumps(login)}); dispatch(loginF); }}
                  if (passF) {{ setter.call(passF, {json.dumps(pwd)}); dispatch(passF); }}
                  return 'filled';
                }})()
                """, "returnByValue": True})
                await asyncio.sleep(1)
                r = await call("Runtime.evaluate", {"expression": """
                (() => {
                  const btn = [...document.querySelectorAll('button')].find(b => /log in|авторизоваться/i.test((b.textContent||'').trim()));
                  if (btn && !btn.disabled) { btn.click(); return 'submitted'; }
                  return 'disabled';
                })()
                """, "returnByValue": True})
                print("SUBMIT:", r.get("result", {}).get("value"))
                await asyncio.sleep(10)
                fin = await call("Runtime.evaluate", {"expression": "JSON.stringify({url: location.href, title: document.title})", "returnByValue": True})
                print("FINAL:", fin.get("result", {}).get("value"))
                return
        print("captcha not passed")

asyncio.run(main())
