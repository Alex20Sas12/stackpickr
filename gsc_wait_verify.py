# -*- coding: utf-8 -*-
"""Ожидание завершения верификации."""
import json, asyncio, urllib.request
import websockets

PORT = 9229

def get_tabs():
    with urllib.request.urlopen(f"http://localhost:{PORT}/json", timeout=5) as r:
        return json.load(r)

async def main():
    tabs = get_tabs()
    ws_url = None
    for t in tabs:
        if t.get("type") == "page" and "search.google.com" in t.get("url", ""):
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
        for i in range(10):
            await asyncio.sleep(5)
            st = await call("Runtime.evaluate", {"expression": """
            (() => {
              const t = document.body.innerText.replace(/\\s+/g,' ');
              const waiting = /выполняется подтверждение|подождите|проверяем/.test(t);
              const success = /подтверждено|владение подтверждено|успешно|готово/.test(t);
              const err = /не удалось|ошибка|не подтверждено|невозможно/.test(t);
              return JSON.stringify({waiting, success, err, snippet: t.slice(0, 250)});
            })()
            """, "returnByValue": True})
            v = json.loads(st.get("result", {}).get("value", "{}"))
            print(f"round {i}:", v)
            if not v.get("waiting") and (v.get("success") or v.get("err")):
                break
            if not v.get("waiting") and not v.get("success") and not v.get("err"):
                # возможно диалог закрылся — проверить наличие ресурса
                break

asyncio.run(main())
