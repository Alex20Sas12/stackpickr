# -*- coding: utf-8 -*-
"""Дерево фреймов → поиск challenge-фрейма → клик по чекбоксу."""
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
        await call("Page.enable")
        tree = await call("Page.getFrameTree")
        def walk(node, depth=0):
            f = node.get("frame", {})
            print("  " * depth + f"{f.get('id','')[:8]} | {f.get('url','')[:100]}")
            for c in node.get("childFrames", []):
                walk(c, depth + 1)
        walk(tree.get("frameTree", {}))

asyncio.run(main())
