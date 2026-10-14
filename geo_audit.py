"""StackPickr geo_audit: реальный поисковый спрос -> CSV с дырами в покрытии.

Сигнал спроса: Google Suggest API (бесплатно, без ключа, без регистрации).
Это НЕ GSC-импрешены - частоты нет. Значит: здесь нет чисел "impressions>=8".
Контент-крону достаётся список запросов с запрос (gap) - решает сам, писать ли страницу.

Вывод: fabrika/geo_audit/gsc_queries.csv
Колонки: query, covered, best_page, score
  covered=True  → запрос закрыт существующей страницей
  covered=False → дыра: спрос есть, страницы нет ← сюда и идёт content-крон
  score = число совпавших ключевых слов запроса с уже покрытыми страницами (0 = чистая дыра)

selfcheck: `python geo_audit.py --check` — падает, если CSV не создан или пуст.
"""
import csv, glob, os, re, sys, time, urllib.parse, urllib.request

SUGGEST = "https://suggestqueries.google.com/complete/search?client=firefox&hl=en&q="
UA = {"User-Agent": "Mozilla/5.0"}
SITE = "https://stackpickr.vercel.app"
SITE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site")
OUT = os.path.join(os.path.expanduser("~"), "fabrika", "geo_audit", "gsc_queries.csv")

# Семена по нишам сайта (hosting / affiliate-software / tools / transfer).
SEEDS = [
    "cloud hosting comparison", "vps hosting comparison", "managed cloud hosting",
    "cloudways vs", "cloudways pricing", "is hosting vps", "is hosting review",
    "kinsta vs", "wp engine vs", "digitalocean droplet pricing", "hetzner vs digitalocean",
    "affiliate tracking software", "affiliate management software", "affiliate program software",
    "referral tracking software", "tapfiliate vs", "rewardful vs firstpromoter",
    "online whiteboard tools", "collaboration whiteboard", "invideo vs canva",
    "airport transfer turkey", "istanbul airport transfer", "airport transfer comparison",
]

# ponytail: stopwords жёсткий список (англ.), без NLP-пакетов. Расширять при ошибочных совпадениях.
STOP = set("vs with free price pricing best review reviews how to for in of and the a vs. 2026 2025".split())


def suggest(q, tries=3):
    url = SUGGEST + urllib.parse.quote(q)
    for _ in range(tries):
        try:
            import json
            d = json.loads(urllib.request.urlopen(
                urllib.request.Request(url, headers=UA), timeout=15).read())
            return d[1][:8]
        except Exception:
            time.sleep(0.5)
    return []


def load_pages():
    """Страница → текст (h1 + title + description), для проверки покрытия."""
    pages = {}
    for f in glob.glob(os.path.join(SITE_DIR, "**", "index.html"), recursive=True):
        try:
            h = open(f, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        rel = os.path.relpath(os.path.dirname(f), SITE_DIR).replace("\\", "/")
        path = "/" + rel + "/" if rel != "." else "/"
        title = re.search(r"<title>([^<]*)</title>", h)
        txt = " ".join(re.findall(r"<h1[^>]*>(.*?)</h1>", h, re.S)).strip()
        pages[path] = (title.group(1) if title else "", txt)
    return pages


def tokens(text):
    return {w.lower() for w in re.findall(r"[a-z0-9*]{3,}", text)} - STOP


def best_match(query, pages):
    """Поиск страницы закрывающей запрос. Возвращает (path, score)."""
    qt = tokens(query)
    if not qt:
        return ("", 0)
    best, bs = ("", 0)
    for path, (title, h1) in pages.items():
        covered = tokens(title + " " + h1)
        # точное вхождение слова запроса в path = сильный сигнал
        s = len(qt & covered) + sum(1 for t in qt if t in path)
        if s > bs:
            best, bs = path, s
    return best, bs


def main():
    pages = load_pages()
    if not pages:
        raise SystemExit("EMPTY SITE — нет страниц в site/")
    rows, seen = [], set()
    for seed in SEEDS:
        for q in suggest(seed):
            q = q.strip().lower()
            if not q or q in seen:
                continue
            seen.add(q)
            path, score = best_match(q, pages)
            rows.append({
                "query": q,
                "covered": str(bool(path and score >= 2)).lower(),
                "best_page": path,
                "score": score,
            })
        time.sleep(0.3)

    gaps = [r for r in rows if not r["covered"]]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["query", "covered", "best_page", "score"])
        w.writeheader()
        w.writerows(rows)

    print(f"queries: {len(rows)} | covered: {len(rows) - len(gaps)} | GAPS: {len(gaps)}")
    for g in gaps[:12]:
        print("  GAP:", g["query"])
    return rows


if __name__ == "__main__":
    if "--check" in sys.argv:
        assert os.path.exists(OUT), "gsc_queries.csv не создан"
        rows = list(csv.DictReader(open(OUT, encoding="utf-8")))
        assert len(rows) > 1, "CSV пустой (только заголовок)"
        assert any(r["covered"] == "false" for r in rows), "нет ни одной дыры - сигнал мертв"
        print(f"OK: gsc_queries.csv живой, {len(rows)} запросов, дыр {sum(1 for r in rows if r['covered']=='false')}")
    else:
        main()
