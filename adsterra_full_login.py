# -*- coding: utf-8 -*-
"""Полный проход логина Adsterra: заполнить, капча кликом координатами, вход."""
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
    if not ws_url:
        print("NO TAB"); return
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

        # 1. заполнить поля (с полным набором событий для React)
        r = await call("Runtime.evaluate", {"expression": f"""
        (() => {{
          const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;
          const dispatch = (el) => {{ ['focus','keydown','keypress','input','keyup','change'].forEach(ev =>
            el.dispatchEvent(new Event(ev, {{bubbles:true}}))); }};
          const loginF = document.querySelector('input[name="login"]');
          const passF = document.querySelector('input[name="signin"]') || document.querySelector('input[type="password"]');
          if (loginF) {{ setter.call(loginF, {json.dumps(login)}); dispatch(loginF); }}
          if (passF) {{ setter.call(passF, {json.dumps(pwd)}); dispatch(passF); }}
          return (loginF ? 'L' : '-') + (passF ? 'P' : '-');
        }})()
        """, "returnByValue": True})
        print("FILL:", r.get("result", {}).get("value"))
        await asyncio.sleep(2)

        # 2. капча: координаты контейнера
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const el = document.getElementById('cf-turnstile');
          if (!el) return JSON.stringify({err: 'no container'});
          const rc = el.getBoundingClientRect();
          return JSON.stringify({x: rc.x, y: rc.y, w: rc.width, h: rc.height});
        })()
        """, "returnByValue": True})
        pos = json.loads(r.get("result", {}).get("value", "{}"))
        print("CAPTCHA BOX:", pos)
        if "err" not in pos and pos.get("w"):
            cx = pos["x"] + 30
            cy = pos["y"] + pos["h"] / 2
            await call("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": cx, "y": cy})
            await asyncio.sleep(0.6)
            await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": cx, "y": cy, "button": "left", "clickCount": 1})
            await asyncio.sleep(0.15)
            await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": cx, "y": cy, "button": "left", "clickCount": 1})
            print(f"clicked captcha at {cx:.0f},{cy:.0f}")
            await asyncio.sleep(8)

        # 3. проверка состояния капчи и кнопки
        st = await call("Runtime.evaluate", {"expression": """
        (() => {
          const btn = [...document.querySelectorAll('button')].find(b => /log in|авторизоваться/i.test((b.textContent||'').trim()));
          const resp = document.querySelector('input[name="cf-turnstile-response"]');
          return JSON.stringify({btnDisabled: btn ? btn.disabled : null, hasResponse: resp ? !!resp.value : null});
        })()
        """, "returnByValue": True})
        print("PRE-LOGIN STATE:", st.get("result", {}).get("value"))

        # если кнопка активна — кликаем
        stv = json.loads(st.get("result", {}).get("value", "{}"))
        if stv.get("btnDisabled") is False:
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
            print("login clicked")
            await asyncio.sleep(11)
            st2 = await call("Runtime.evaluate", {"expression": """
            (() => {
              const errs = [...document.querySelectorAll('div,span')].filter(e => e.offsetParent !== null &&
                /invalid|incorrect|wrong|failed|ошибк|неверн|неправил/i.test(e.textContent||'') && (e.textContent||'').length < 120)
                .map(e => e.textContent.trim()).slice(0,2);
              return JSON.stringify({url: location.href, title: document.title, errs});
            })()
            """, "returnByValue": True})
            print("RESULT:", st2.get("result", {}).get("value"))
        else:
            print("BUTTON STILL DISABLED — captcha not passed")

asyncio.run(main())
