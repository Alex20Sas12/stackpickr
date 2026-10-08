# -*- coding: utf-8 -*-
"""Заполнить форму логина (капча уже пройдена владельцем) и войти."""
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
        # текущее состояние
        st = await call("Runtime.evaluate", {"expression": """
        (() => {
          const btn = [...document.querySelectorAll('button')].find(b => /log in|авторизоваться/i.test((b.textContent||'').trim()));
          const hidden = document.querySelector('input[name="cloudflareCaptchaToken"]');
          return JSON.stringify({url: location.href, btnDisabled: btn ? btn.disabled : null,
            tokenLen: hidden && hidden.value ? hidden.value.length : 0,
            respLen: window.turnstile && window.turnstile.getResponse() ? String(window.turnstile.getResponse()).length : 0});
        })()
        """, "returnByValue": True})
        print("STATE:", st.get("result", {}).get("value"))

        # заполнить поля (клик мышью по полю + ввод через Input.insertText для надёжности)
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const loginF = document.querySelector('input[name="login"]');
          const rc = loginF.getBoundingClientRect();
          return JSON.stringify({x: rc.x + rc.width/2, y: rc.y + rc.height/2, curVal: loginF.value});
        })()
        """, "returnByValue": True})
        lp = json.loads(r.get("result", {}).get("value", "{}"))
        # кликаем поле логина
        await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": lp["x"], "y": lp["y"], "button": "left", "clickCount": 1})
        await asyncio.sleep(0.1)
        await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": lp["x"], "y": lp["y"], "button": "left", "clickCount": 1})
        await call("Runtime.evaluate", {"expression": "document.querySelector('input[name=\"login\"]').select(); 1"})
        await call("Input.insertText", {"text": login})
        await asyncio.sleep(0.5)
        # поле пароля
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const p = document.querySelector('input[name="signin"]') || document.querySelector('input[type="password"]');
          const rc = p.getBoundingClientRect();
          return JSON.stringify({x: rc.x + rc.width/2, y: rc.y + rc.height/2});
        })()
        """, "returnByValue": True})
        pp = json.loads(r.get("result", {}).get("value", "{}"))
        await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": pp["x"], "y": pp["y"], "button": "left", "clickCount": 1})
        await asyncio.sleep(0.1)
        await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": pp["x"], "y": pp["y"], "button": "left", "clickCount": 1})
        await call("Input.insertText", {"text": pwd})
        await asyncio.sleep(1)

        st2 = await call("Runtime.evaluate", {"expression": """
        (() => {
          const btn = [...document.querySelectorAll('button')].find(b => /log in|авторизоваться/i.test((b.textContent||'').trim()));
          const loginF = document.querySelector('input[name="login"]');
          const passF = document.querySelector('input[name="signin"]') || document.querySelector('input[type="password"]');
          return JSON.stringify({btnDisabled: btn ? btn.disabled : null, loginLen: loginF.value.length, passLen: passF.value.length});
        })()
        """, "returnByValue": True})
        print("FILLED:", st2.get("result", {}).get("value"))

        # клик кнопки входа
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const btn = [...document.querySelectorAll('button')].find(b => /log in|авторизоваться/i.test((b.textContent||'').trim()));
          if (!btn) return 'NOBTN';
          const rc = btn.getBoundingClientRect();
          return JSON.stringify({x: rc.x + rc.width/2, y: rc.y + rc.height/2, disabled: btn.disabled});
        })()
        """, "returnByValue": True})
        print("BTN:", r.get("result", {}).get("value"))
        bpos = json.loads(r.get("result", {}).get("value", "{}")) if r.get("result", {}).get("value") not in ("NOBTN", None) else None
        if bpos and not bpos.get("disabled"):
            await call("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": bpos["x"], "y": bpos["y"]})
            await asyncio.sleep(0.3)
            await call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": bpos["x"], "y": bpos["y"], "button": "left", "clickCount": 1})
            await asyncio.sleep(0.12)
            await call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": bpos["x"], "y": bpos["y"], "button": "left", "clickCount": 1})
            await asyncio.sleep(12)
            fin = await call("Runtime.evaluate", {"expression": """
            (() => {
              const errs = [...document.querySelectorAll('div,span')].filter(e => e.offsetParent !== null &&
                /invalid|incorrect|wrong|failed|ошибк|неверн|неправил|введен|парол|логин|капч|captcha/i.test(e.textContent||'') && (e.textContent||'').length < 120)
                .map(e => e.textContent.trim()).slice(0,3);
              return JSON.stringify({url: location.href, title: document.title, errs,
                snippet: document.body.innerText.replace(/\\s+/g,' ').slice(0,200)});
            })()
            """, "returnByValue": True})
            print("RESULT:", fin.get("result", {}).get("value"))
        else:
            print("button disabled or missing — not submitting")

asyncio.run(main())
