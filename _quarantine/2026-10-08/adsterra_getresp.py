# -*- coding: utf-8 -*-
import json, asyncio, urllib.request
import websockets

PORT = 9222

def get_tabs():
    with urllib.request.urlopen(f"http://localhost:{PORT}/json", timeout=5) as r:
        return json.load(r)

async def main():
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
        r = await call("Runtime.evaluate", {"expression": """
        (() => {
          const t = window.turnstile;
          let resp = null;
          try { resp = t.getResponse(); } catch(e) { resp = 'ERR:' + e; }
          const hidden = document.querySelector('input[name="cloudflareCaptchaToken"]');
          const btn = [...document.querySelectorAll('button')].find(b => /log in|авторизоваться/i.test((b.textContent||'').trim()));
          return JSON.stringify({
            response: resp ? String(resp).slice(0, 40) : null,
            hiddenVal: hidden ? (hidden.value ? 'LEN=' + hidden.value.length : 'empty') : 'none',
            btnDisabled: btn ? btn.disabled : null
          });
        })()
        """, "returnByValue": True})
        print("STATE:", r.get("result", {}).get("value"))

asyncio.run(main())
