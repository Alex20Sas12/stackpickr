# -*- coding: utf-8 -*-
"""Только проверка (inspect) всех URL — БЕЗ запроса индексирования (квоту не тратит)."""
import json, asyncio, urllib.request
import websockets

PORT = 9229
URLS = [
    "https://stackpickr.vercel.app/",
    "https://stackpickr.vercel.app/hosting/",
    "https://stackpickr.vercel.app/affiliate-software/",
    "https://stackpickr.vercel.app/hosting/best-vps-providers/",
    "https://stackpickr.vercel.app/affiliate-software/best-affiliate-software/",
    "https://stackpickr.vercel.app/hosting/cloudways/",
    "https://stackpickr.vercel.app/hosting/ishosting/",
    "https://stackpickr.vercel.app/affiliate-software/tapfiliate/",
]

async def main():
    with urllib.request.urlopen(f"http://localhost:{PORT}/json", timeout=5) as r:
        tabs = json.load(r)
    ws_url = None
    for t in tabs:
        if t.get("type") == "page" and "search.google.com" in t.get("url", ""):
            ws_url = t["webSocketDebuggerUrl"]; break
    async with websockets.connect(ws_url, max_size=20*1024*1024) as ws:
        _id = [0]
        async def call(method, params=None):
            _id[0] += 1
            await ws.send(json.dumps({"id": _id[0], "method": method, "params": params or {}}))
            while True:
                m = json.loads(await ws.recv())
                if m.get("id") == _id[0]:
                    return m.get("result", {})
        await call("Runtime.enable"); await call("Page.enable")
        results = []
        for u in URLS:
            await call("Page.navigate", {"url": "https://search.google.com/search-console?resource_id=https%3A%2F%2Fstackpickr.vercel.app%2F"})
            await asyncio.sleep(9)
            r = await call("Runtime.evaluate", {"expression": """
            ((U) => {
              const inp = [...document.querySelectorAll('input')].filter(i =>
                i.offsetParent !== null && /проверка всех url/i.test(i.getAttribute('aria-label')||''))[0];
              if (!inp) return 'none';
              inp.focus();
              const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
              setter.call(inp, U);
              inp.dispatchEvent(new Event('input', {bubbles: true}));
              for (const type of ['keydown', 'keypress', 'keyup']) {
                inp.dispatchEvent(new KeyboardEvent(type, {key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true, cancelable: true}));
              }
              return 'sent';
            })(%s)""" % json.dumps(u), "returnByValue": True})
            if r.get("result", {}).get("value") != "sent":
                results.append((u, "NO_INPUT")); continue
            status = "?"
            for i in range(10):
                await asyncio.sleep(5)
                st = await call("Runtime.evaluate", {"expression": """
                (() => {
                  const t = document.body.innerText.replace(/\\s+/g,' ');
                  return JSON.stringify({
                    indexed: /url есть в индексе google/i.test(t),
                    notIndexed: /url нет в google|url отсутствует в google|еще не проиндексирована|не проиндексирована/i.test(t),
                    reqBtn: [...document.querySelectorAll('*')].some(e => e.offsetParent !== null &&
                      e.children.length === 0 && /запросить индексирование/i.test((e.innerText||'').trim())),
                    crawled: /просканирована|последнее сканирование/i.test(t)
                  });
                })()""", "returnByValue": True})
                sv = json.loads(st.get("result", {}).get("value", "{}"))
                if sv.get("indexed"): status = "INDEXED"; break
                if sv.get("notIndexed"): status = "NOT_INDEXED(reqBtn=%s)" % sv.get("reqBtn"); break
                if sv.get("reqBtn") or sv.get("crawled"): status = "RESULT_NO_INDEX_MARK(reqBtn=%s)" % sv.get("reqBtn"); break
            results.append((u, status))
            print(u, "->", status, flush=True)
        print("\n=== SUMMARY ===")
        for u, s in results:
            print(f"{s:35s} {u}")

asyncio.run(main())
