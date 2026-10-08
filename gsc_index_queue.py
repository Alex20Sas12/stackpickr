# -*- coding: utf-8 -*-
"""Запрос индексации ключевых страниц StackPickr через верхнюю строку Проверки URL.
Запуск: python gsc_index_queue.py
Требует: Chrome-профиль chrome-gsc-profile на порту 9229, вход в alexford0289@gmail.com.
Лимит Google ~10 запросов/день — скрипт берёт первые N незапрошенных URL, прогресс в .gsc_indexed.json.
Вкладку GSC открывает сам, если её нет (11.09: фикс — раньше падал с ERROR и терял день).
"""
import json, asyncio, os, re, subprocess, sys, time, urllib.parse, urllib.request
import websockets

PORT = 9229
PROFILE = os.path.expandvars(r"%USERPROFILE%\chrome-gsc-profile")
CHROME = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
LIMIT = 2  # ponytail: квота GSC (~10 проверок/день) ОБЩАЯ на все сайты аккаунта — по 2 на сайт, иначе остальные кроны получают QUOTA
HERE = os.path.dirname(os.path.abspath(__file__))
PROG = os.path.join(HERE, ".gsc_indexed.json")
URLS = [
    # BOFU-батч 10.09 (план «1», трек 1+3): новые страницы цен и инструментов
    "https://stackpickr.vercel.app/hosting/cheapest-vps/",
    "https://stackpickr.vercel.app/guides/vps-hosting-prices-2026/",
    "https://stackpickr.vercel.app/tools/vps-cost-calculator/",
]
GSC_URL = "https://search.google.com/search-console?resource_id=https%3A%2F%2Fstackpickr.vercel.app%2F"

def get_tabs():
    with urllib.request.urlopen(f"http://localhost:{PORT}/json", timeout=5) as r:
        return json.load(r)

def ensure_chrome_window():
    """Поднять окно GSC-профиля, если порт мёртв (фикс 12.09: крон терял день из-за URLError)."""
    try:
        get_tabs(); return
    except Exception:
        pass
    subprocess.Popen([CHROME, f"--remote-debugging-port={PORT}",
                      f"--user-data-dir={PROFILE}", "--remote-allow-origins=*",
                      "--no-first-run", GSC_URL])
    for _ in range(20):
        time.sleep(3)
        try:
            get_tabs(); return
        except Exception:
            pass
    raise RuntimeError(f"окно {PORT} не поднялось")

def ensure_gsc_tab():
    """Найти вкладку search.google.com; если нет — открыть новую через PUT /json/new."""
    for t in get_tabs():
        if t.get("type") == "page" and "search.google.com" in t.get("url", ""):
            return t["webSocketDebuggerUrl"]
    req = urllib.request.Request(f"http://localhost:{PORT}/json/new?{urllib.parse.quote(GSC_URL, safe=':/?%=&')}", method="PUT")
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.load(r)["webSocketDebuggerUrl"]

async def main():
    ensure_chrome_window()
    ws_url = ensure_gsc_tab()
    done_urls = set(json.load(open(PROG, encoding="utf-8"))) if os.path.exists(PROG) else set()
    # ponytail: очередь из sitemap (как transfersite) — хардкод URLS оставляем фолбэком
    sm = os.path.join(HERE, "site", "sitemap.xml")
    all_u = re.findall(r"<loc>(.*?)</loc>", open(sm, encoding="utf-8").read()) if os.path.exists(sm) else URLS
    todo = [u for u in all_u if u not in done_urls]
    if not todo:
        print("ALL_REQUESTED: все URL уже запрошены"); return
    async with websockets.connect(ws_url, max_size=20*1024*1024) as ws:
        _id = [0]
        async def call(method, params=None):
            _id[0] += 1
            await ws.send(json.dumps({"id": _id[0], "method": method, "params": params or {}}))
            while True:
                m = json.loads(await ws.recv())
                if m.get("id") == _id[0]:
                    return m.get("result", {})
        await call("Runtime.enable")
        await call("Page.enable")

        queued_total = 0
        for u in todo[:LIMIT]:
            await call("Page.navigate", {"url": GSC_URL})
            await asyncio.sleep(10)
            # строка проверки URL: JS-setter + JS Enter (CDP-клавиши GSC не слушает)
            r = await call("Runtime.evaluate", {"expression": """
            ((U) => {
              const inp = [...document.querySelectorAll('input')].filter(i =>
                i.offsetParent !== null && /проверка всех url/i.test(i.getAttribute('aria-label')||''))[0];
              if (!inp) return 'none';
              inp.focus();
              const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
              setter.call(inp, U);
              inp.dispatchEvent(new Event('input', {bubbles: true}));
              inp.dispatchEvent(new Event('change', {bubbles: true}));
              for (const type of ['keydown', 'keypress', 'keyup']) {
                inp.dispatchEvent(new KeyboardEvent(type, {key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true, cancelable: true}));
              }
              return 'sent';
            })(%s)
            """ % json.dumps(u), "returnByValue": True})
            v = r.get("result", {}).get("value")
            if v != "sent":
                print(f"{u}: нет строки проверки"); continue
            await asyncio.sleep(5)
            # ждать результата проверки до 45 сек
            status = None
            for _ in range(9):
                await asyncio.sleep(5)
                st = await call("Runtime.evaluate", {"expression": """
                (() => {
                  const t = document.body.innerText.replace(/\\s+/g,' ');
                  const reqBtn = [...document.querySelectorAll('*')].some(e => e.offsetParent !== null &&
                    e.children.length === 0 && /запросить индексирование/i.test((e.innerText||'').trim()));
                  return JSON.stringify({
                    indexed: /url есть в индексе google/i.test(t),
                    reqBtn,
                    quota: /квота превышена/i.test(t)
                  });
                })()
                """, "returnByValue": True})
                sv = json.loads(st.get("result", {}).get("value", "{}"))
                if sv.get("quota"):
                    status = "QUOTA_EXHAUSTED"; break
                if sv.get("indexed"):
                    status = "ALREADY_INDEXED"; break
                if sv.get("reqBtn"):
                    status = "REQUEST"; break
            if status == "QUOTA_EXHAUSTED":
                print(f"{u}: квота исчерпана — стоп"); break
            if status == "ALREADY_INDEXED":
                print(f"{u}: УЖЕ В ИНДЕКСЕ ✓"); queued_total += 1; done_urls.add(u); continue
            if status != "REQUEST":
                print(f"{u}: не дождался результата ({status})"); continue
            # закрыть обучающие подсказки
            await call("Runtime.evaluate", {"expression": """
            (() => { const els = [...document.querySelectorAll('*')].filter(e =>
                e.offsetParent !== null && e.children.length === 0 && (e.innerText||'').trim() === 'Закрыть');
              for (const e of els) e.click(); return els.length; })()
            """, "returnByValue": True})
            await asyncio.sleep(1.5)
            # клик Запросить индексирование
            r2 = await call("Runtime.evaluate", {"expression": """
            (() => {
              const els = [...document.querySelectorAll('*')].filter(e =>
                e.offsetParent !== null && e.children.length === 0 &&
                /запросить индексирование/i.test((e.innerText||'').trim()) && (e.innerText||'').trim().length < 40);
              if (!els.length) return 'none';
              els[0].scrollIntoView({block:'center'});
              return 'ok';
            })()
            """, "returnByValue": True})
            if r2.get("result", {}).get("value") != "ok":
                print(f"{u}: кнопка пропала"); continue
            await asyncio.sleep(0.7)
            # 27.09: координатный CDP-клик GSC НЕ слушает (кнопка MD-ripple) — дёргаем JS-кликом по кнопке-предку
            r3 = await call("Runtime.evaluate", {"expression": """
            (() => {
              const els = [...document.querySelectorAll('*')].filter(e =>
                e.offsetParent !== null && e.children.length === 0 &&
                /запросить индексирование/i.test((e.innerText||'').trim()) && (e.innerText||'').trim().length < 40);
              if (!els.length) return 'none';
              let tgt = els[0];
              for (let i = 0; i < 8 && tgt; i++) { if (tgt.matches && tgt.matches('button,a,[role=button]')) break; tgt = tgt.parentElement || tgt; }
              ['pointerdown','mousedown','pointerup','mouseup','click'].forEach(n =>
                tgt.dispatchEvent(new MouseEvent(n, {bubbles: true, cancelable: true, view: window})));
              tgt.click && tgt.click();
              return 'clicked';
            })()
            """, "returnByValue": True})
            if r3.get("result", {}).get("value") != "clicked": continue
            # ждать «поставлен в очередь» до 2.5 мин (Google делает живой тест)
            ok = False
            for _ in range(18):
                await asyncio.sleep(8)
                st2 = await call("Runtime.evaluate", {"expression": """
                (() => {
                  const t = document.body.innerText.replace(/\\s+/g,' ');
                  return JSON.stringify({queued: /поставлен в очередь|запрошено индексирование/i.test(t),
                    quota: /квота превышена/i.test(t)});
                })()
                """, "returnByValue": True})
                s2 = json.loads(st2.get("result", {}).get("value", "{}"))
                if s2.get("queued"): ok = True; break
                if s2.get("quota"):
                    print(f"{u}: квота исчерпана во время обработки"); break
            print(f"{u}: {'В ОЧЕРЕДИ ✓' if ok else 'не подтверждено'}")
            if ok:
                queued_total += 1; done_urls.add(u)
            else:
                break  # вероятно квота
        print(f"ИТОГО: {queued_total} страниц обработано/в очереди")
        json.dump(sorted(done_urls), open(PROG, "w", encoding="utf-8"))

asyncio.run(main())
