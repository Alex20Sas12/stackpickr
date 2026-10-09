# -*- coding: utf-8 -*-
"""Разведка: как переключить язык на страницах (селекторы)."""
import json, asyncio, urllib.request
import websockets

PORT = 9222

def new_tab(url):
    req = urllib.request.Request(f"http://localhost:{PORT}/json/new?{urllib.parse.quote(url, safe=':/')}", method="PUT")
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return json.load(r)
    except Exception:
        with urllib.request.urlopen(f"http://localhost:{PORT}/json/new?{url}", timeout=5) as r:
            return json.load(r)

def close_tab(tid):
    try:
        urllib.request.urlopen(f"http://localhost:{PORT}/json/close/{tid}", timeout=5)
    except Exception:
        pass

JS_LANG = """
(() => {
  // ищем всё похожее на переключатель языка
  const hits = [];
  for (const a of document.querySelectorAll('a, select, button')) {
    const t = (a.textContent || '').trim();
    if (a.offsetParent !== null && /^(en(?!g)|english|рус|ru|язык|language)$/i.test(t) && t.length < 12) {
      hits.push({tag: a.tagName, text: t, href: a.href || '', cls: (a.className||'').toString().slice(0,60)});
    }
  }
  // select с языками
  for (const s of document.querySelectorAll('select')) {
    const opts = [...s.options].map(o => o.text).join(',');
    if (/en|рус|language/i.test(opts)) hits.push({tag: 'SELECT', text: opts.slice(0,60), id: s.id});
  }
  return JSON.stringify({url: location.href, hits: hits.slice(0, 10), cookies: document.cookie.slice(0, 300)});
})()
"""

async def main():
    for url in ["https://www.cloudways.com/en/", "https://ishosting.com/"]:
        tab = new_tab(url)
        ws_url = tab["webSocketDebuggerUrl"]; tid = tab["id"]
        try:
            async with websockets.connect(ws_url, max_size=20*1024*1024) as ws:
                _id = [1]
                async def call(method, params=None):
                    _id[0] += 1
                    await ws.send(json.dumps({"id": _id[0], "method": method, "params": params or {}}))
                    while True:
                        msg = json.loads(await ws.recv())
                        if msg.get("id") == _id[0]:
                            return msg.get("result", {})
                await call("Page.enable")
                await call("Page.navigate", {"url": url})
                await asyncio.sleep(10)
                r = await call("Runtime.evaluate", {"expression": JS_LANG, "returnByValue": True})
                print("====", url)
                print(r.get("result", {}).get("value"))
        finally:
            close_tab(tid)

asyncio.run(main())
