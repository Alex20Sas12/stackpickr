#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Проверка/вход Adsterra в окне 9222 через CDP. Разовый хелпер."""
import json, sys, time, urllib.request, websocket

PORT = 9222

def pages():
    d = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/list", timeout=5).read())
    return [t for t in d if t.get("type") == "page"]

def find(sub):
    for t in pages():
        if sub in t.get("url", ""):
            return t
    return None

def js(ws, expr, mid):
    ws.send(json.dumps({"id": mid, "method": "Runtime.evaluate",
                        "params": {"expression": expr, "returnByValue": True, "awaitPromise": True}}))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == mid:
            return r.get("result", {}).get("result", {}).get("value")

def main():
    t = find("adsterra") or pages()[0]
    ws = websocket.create_connection(t["webSocketDebuggerUrl"], timeout=30)
    mid = [0]
    def ev(expr):
        mid[0] += 1
        return js(ws, expr, mid[0])
    ws.send(json.dumps({"id": 100, "method": "Page.navigate",
                        "params": {"url": "https://publishers.adsterra.com/"}}))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == 100:
            break
    time.sleep(8)
    info = ev("JSON.stringify({url: location.href, title: document.title, body: document.body ? document.body.innerText.slice(0,600) : ''})")
    print(info)
    ws.close()

if __name__ == "__main__":
    main()
