# -*- coding: utf-8 -*-
"""Inspect the about:blank challenge frame content; try executing inside it."""
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
        # find the about:blank 300x150 frame — check its content via Runtime.evaluate in isolated world
        def walk(node, out):
            f = node.get("frame", {})
            out.append(f)
            for c in node.get("childFrames", []):
                walk(c, out)
        frames = []
        walk(tree.get("frameTree", {}), frames)
        for f in frames:
            if f.get("url") == "about:blank":
                fid = f.get("id")
                # create an isolated world to eval inside
                iw = await call("Page.createIsolatedWorld", {"frameId": fid, "worldName": "probe"})
                ctx = iw.get("executionContextId")
                if ctx:
                    r = await call("Runtime.evaluate", {
                        "expression": "JSON.stringify({url: location.href, title: document.title, bodyLen: document.body ? document.body.innerHTML.length : -1, html: document.documentElement.outerHTML.slice(0,500)})",
                        "contextId": ctx, "returnByValue": True})
                    print(f"FRAME {fid[:8]}:", r.get("result", {}).get("value"))

asyncio.run(main())
