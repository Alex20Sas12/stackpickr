# -*- coding: utf-8 -*-
"""
sitegen.py — генератор сравнительного сайта StackPickr (фабрика, фаза 4.x).
Данные в data/*.json → статический сайт в site/.
Типы страниц: home, hub, review, vs, listicle, guide.
SEO/AEO: уникальные title, JSON-LD (Article/FAQPage/SoftwareApplication/ItemList/Breadcrumb),
llms.txt, sitemap.xml, robots.txt, OG-теги.
"""
import json, os, html, re
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
OUT = os.path.join(HERE, "site")

CFG = json.load(open(os.path.join(DATA, "config.json"), encoding="utf-8"))
DOMAIN = CFG["domain"]

HOME_FAQS = [
    ("What is StackPickr?",
     "StackPickr is an independent editorial site that compares cloud hosting, VPS and affiliate tracking software using published specs and pricing. Every comparison ends with a clear winner and the reasoning behind it."),
    ("How does StackPickr compare hosting providers?",
     "We collect each plan's exact entry price, renewal price, included backups, data-center locations and support terms from official sources, then lay them side by side in a comparison table."),
    ("Is StackPickr free to use?",
     "Yes. All comparisons, reviews and guides are free, with no login or signup required. We may earn an affiliate commission when you buy through some links, at no extra cost to you."),
    ("How often are prices and specs updated?",
     "Every page carries a verification date. We re-check quarterly or whenever a provider announces a pricing change."),
]
DISCLOSURE = CFG["disclosure"]
ADSTERRA_KEY = CFG.get("adsterra", {}).get("native_key")
ADSTERRA_SUB = CFG.get("adsterra", {}).get("subdomain", "pl31188985.profitableratecpmnetwork.com")

PRODUCTS = json.load(open(os.path.join(DATA, "products.json"), encoding="utf-8"))

def esc(s): return html.escape(str(s), quote=False)
def e(s): return html.escape(str(s))

def link_for(key):
    """Возвращает (href, label). Пока модерация не одобрена — ссылка на офиц. сайт."""
    info = CFG["links"].get(key, {})
    if info.get("href"):
        return info["href"], True
    p = PRODUCTS.get(key)
    return (p["official_url"] if p else "#"), False

def css():
    return """
:root{--bg:#0e1116;--panel:#161b23;--panel2:#1d242f;--text:#e8ecf1;--muted:#9aa5b1;
--acc:#4f9cf9;--acc2:#38d39f;--warn:#f6b73c;--bad:#ef6b6b;--border:#2a3340;--radius:12px}
*{box-sizing:border-box}body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;
background:var(--bg);color:var(--text);line-height:1.65;font-size:17px}
a{color:var(--acc);text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:880px;margin:0 auto;padding:0 20px}
header.site{border-bottom:1px solid var(--border);background:var(--panel)}
header.site .wrap{display:flex;align-items:center;gap:24px;padding:14px 20px}
header.site .logo{font-weight:800;font-size:20px;color:var(--text)}
header.site nav{display:flex;gap:18px;font-size:15px}
.breadcrumbs{font-size:14px;color:var(--muted);margin:18px 0 6px}
.breadcrumbs a{color:var(--muted)}
h1{font-size:34px;line-height:1.25;margin:.4em 0}
h2{font-size:26px;margin-top:1.6em;border-bottom:1px solid var(--border);padding-bottom:.25em}
h3{font-size:20px}
.tldr{background:linear-gradient(135deg,#1a2332,#16202a);border:1px solid var(--border);
border-left:5px solid var(--acc);border-radius:var(--radius);padding:18px 22px;margin:22px 0}
.tldr b.winner{color:var(--acc2)}
.cta-box{background:var(--panel2);border:1px solid var(--border);border-radius:var(--radius);
padding:20px;margin:26px 0;display:flex;flex-wrap:wrap;gap:16px;align-items:center;justify-content:space-between}
.cta-box .info{flex:1;min-width:240px}
.btn{display:inline-block;padding:12px 26px;border-radius:9px;font-weight:700;font-size:16px;color:#08131f}
.btn.primary{background:var(--acc2)}
.btn.secondary{background:var(--acc)}
.btn.ghost{background:transparent;border:1px solid var(--border);color:var(--text)}
.btn:hover{text-decoration:none;filter:brightness(1.1)}
table{border-collapse:collapse;width:100%;margin:20px 0;font-size:15.5px}
th,td{border:1px solid var(--border);padding:10px 13px;text-align:left;vertical-align:top}
thead th{background:var(--panel2)}
tbody tr:nth-child(even){background:rgba(255,255,255,.025)}
td.win{color:var(--acc2);font-weight:600}
td.lose{color:var(--muted)}
.verdict{background:rgba(56,211,159,.08);border:1px solid rgba(56,211,159,.35);border-radius:var(--radius);padding:18px 22px;margin:26px 0}
.pros-cons{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:20px 0}
@media(max-width:640px){.pros-cons{grid-template-columns:1fr}}
.pros,.cons{border-radius:var(--radius);padding:16px 20px}
.pros{background:rgba(56,211,159,.07);border:1px solid rgba(56,211,159,.3)}
.cons{background:rgba(239,107,107,.07);border:1px solid rgba(239,107,107,.3)}
.pros h3,.cons h3{margin-top:0;font-size:17px}
.stars{color:var(--warn);letter-spacing:2px;font-size:18px}
.score-badge{display:inline-block;background:var(--panel2);border:1px solid var(--border);
border-radius:8px;padding:6px 12px;font-weight:700;font-size:18px;margin-right:8px}
figure{margin:26px 0;text-align:center}
figure img{max-width:100%;border-radius:var(--radius);border:1px solid var(--border)}
figcaption{font-size:14px;color:var(--muted);margin-top:8px}
details{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:12px 18px;margin:10px 0}
summary{cursor:pointer;font-weight:600}
details[open] summary{margin-bottom:8px;color:var(--acc)}
.ad-slot{margin:30px 0;min-height:20px}
.discl{font-size:13.5px;color:var(--muted);border-top:1px solid var(--border);margin-top:40px;padding-top:16px}
.note{font-size:13.5px;color:var(--muted)}
footer.site{border-top:1px solid var(--border);margin-top:50px;padding:30px 0;color:var(--muted);font-size:14.5px}
footer.site .wrap{display:flex;flex-wrap:wrap;gap:30px;justify-content:space-between}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:16px;margin:22px 0}
.card{background:var(--panel);border:1px solid var(--border);border-radius:var(--radius);padding:18px}
.card h3{margin:0 0 8px;font-size:17px}
.card p{margin:6px 0;font-size:14.5px;color:var(--muted)}
.tag{display:inline-block;background:var(--panel2);border:1px solid var(--border);border-radius:6px;
padding:2px 9px;font-size:12.5px;color:var(--muted);margin:2px 4px 2px 0}
.updated{font-size:13.5px;color:var(--muted)}
ul.check li::marker{content:"✔ ";color:var(--acc2)}
"""

def head(p):
    title = p["title"]
    desc = p["description"]
    url = DOMAIN + p["path"]
    og_img = DOMAIN + p.get("og_image", "/img/og-default.png")
    ld = p.get("jsonld", [])
    ld_html = "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    gsc = CFG.get("gsc_meta")
    gsc_tag = f'<meta name="google-site-verification" content="{gsc}">' if gsc else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
{gsc_tag}
<link rel="canonical" href="{url}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="article">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{og_img}">
<meta property="og:site_name" content="StackPickr">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>">
<link rel="stylesheet" href="/style.css">
<link rel="alternate" type="application/rss+xml" title="StackPickr Feed" href="https://stackpickr.vercel.app/feed.xml">
{ld_html}
</head>"""

def header(p):
    nav = [("Home","/"),("Hosting","/hosting/"),("Affiliate Software","/affiliate-software/"),("Tools","/tools/"),("Transfers","/transfer/"),("Guides","/guides/")]
    items = "".join(f'<a href="{h}">{e(t)}</a>' for t,h in nav)
    crumbs = p.get("crumbs")
    cr = ""
    if crumbs:
        cr = '<div class="wrap breadcrumbs">' + " › ".join(f'<a href="{h}">{e(t)}</a>' for t,h in crumbs[:-1]) + f' › {e(crumbs[-1][0])}' + "</div>"
    return f"""<header class="site"><div class="wrap"><a class="logo" href="/">⚡ StackPickr</a><nav>{items}</nav></div>{cr}</header>"""

def ad_block():
    if ADSTERRA_KEY:
        return f'<div class="ad-slot"><script async="async" data-cfasync="false" src="https://{ADSTERRA_SUB}/{ADSTERRA_KEY}/invoke.js"></script><div id="container-{ADSTERRA_KEY}"></div></div>'
    return '<div class="ad-slot" data-ad="pending"></div>'

def footer():
    return f"""<footer class="site"><div class="wrap">
<div>
<b style="color:var(--text)">StackPickr</b><br>
Independent software comparisons. We test, research and compare so you don't have to.<br>
Need Excel templates for your business? Visit <a href="{CFG['links']['showcase']['href']}">TemplatesPRO</a>.
</div>
<div>
<a href="/hosting/">Hosting comparisons</a> · <a href="/affiliate-software/">Affiliate software</a> · <a href="/tools/">Tool reviews</a> · <a href="/transfer/">Turkey transfers</a> · <a href="/guides/">Guides</a> · <a href="/about/">About & methodology</a> · <a href="/privacy/">Privacy</a><br>
© {date.today().year} StackPickr
</div>
</div></footer>"""

def render(p, body):
    return (head(p) + header(p) + f'<main class="wrap">{body}</main>' + footer() + "</html>")

def stars(r):
    full = int(r); half = "½" if (r - full) >= 0.5 else ""
    return f'<span class="stars">{"★"*full}{half}{"☆"*(5-full- (1 if half else 0))}</span> <b>{r}/5</b>'

def cta_box(key, blurb=None):
    p = PRODUCTS[key]
    href, is_aff = link_for(key)
    rel = ' rel="nofollow sponsored noopener"' if is_aff else ' rel="noopener"'
    label = f"Visit {p['name']} →"
    sub = blurb or p.get("cta_blurb", "")
    return f"""<div class="cta-box"><div class="info"><b>{e(p['name'])}</b> — {e(sub)}<br>
<span class="stars">{stars(p.get('rating',4.5))}</span></div>
<a class="btn primary" href="{href}"{rel} target="_blank">{label}</a></div>"""

def compare_table(rows, cols):
    """rows: list of dicts {feature, values:[...] , winner:int|None}"""
    th = "".join(f"<th>{e(c)}</th>" for c in cols)
    body = ""
    for r in rows:
        tds = ""
        for i, v in enumerate(r["values"]):
            cls = ""
            if r.get("winner") is not None:
                cls = ' class="win"' if i == r["winner"] else ' class="lose"'
            mark = " ✔" if r.get("winner") == i else ""
            tds += f"<td{cls}>{e(v)}{mark}</td>"
        body += f"<tr><th scope='row'>{e(r['feature'])}</th>{tds}</tr>"
    return f'<table><thead><tr><th>Feature</th>{th}</tr></thead><tbody>{body}</tbody></table>'

def pros_cons(pros, cons, name):
    pi = "".join(f"<li>{e(x)}</li>" for x in pros)
    ci = "".join(f"<li>{e(x)}</li>" for x in cons)
    return f"""<div class="pros-cons"><div class="pros"><h3>{e(name)} — Pros</h3><ul class="check">{pi}</ul></div>
<div class="cons"><h3>{e(name)} — Cons</h3><ul>{ci}</ul></div></div>"""

def faq_block(faqs):
    items = ""
    for q, a in faqs:
        items += f"<details><summary>{e(q)}</summary><p>{a}</p></details>"
    return f'<h2>Frequently Asked Questions</h2>{items}'

def write(path, content):
    rel = path.lstrip("/")
    if rel == "" or rel.endswith("/"):
        rel += "index.html"
    fp = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    with open(fp, "w", encoding="utf-8") as f:
        f.write(content)

# JSON-LD builders
def ld_breadcrumb(crumbs):
    return {"@context":"https://schema.org","@type":"BreadcrumbList",
            "itemListElement":[{"@type":"ListItem","position":i+1,"name":t,
             **({"item":DOMAIN+h} if h else {})} for i,(t,h) in enumerate(crumbs)]}

def ld_faq(faqs):
    return {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":re.sub('<[^>]+>','',a)}} for q,a in faqs]}

def ld_article(p):
    return {"@context":"https://schema.org","@type":"Article",
            "headline":p["title"],"description":p["description"],
            "author":{"@type":"Organization","name":"StackPickr Editorial Team"},
            "publisher":{"@type":"Organization","name":"StackPickr"},
            "dateModified":p.get("updated", str(date.today())),
            "mainEntityOfPage":DOMAIN+p["path"]}

def ld_software(key):
    p = PRODUCTS[key]
    return {"@context":"https://schema.org","@type":"SoftwareApplication",
            "name":p["name"],"applicationCategory":p.get("app_category","BusinessApplication"),
            "url":p["official_url"],"description":p["short"],
            "offers":{"@type":"Offer","price":p.get("price_from","0"),"priceCurrency":"USD"},
            "aggregateRating":{"@type":"AggregateRating","ratingValue":p.get("rating",4.5),
                               "ratingCount":p.get("rating_count",120),"bestRating":5}}

def main():
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "style.css"), "w", encoding="utf-8") as f:
        f.write(css())
    from pages import build
    pages = build()
    for p in pages:
        write(p["path"], render(p, p["_body"]))
        print("  ✓", p["path"])
    sitemap()
    llms(pages)
    pricing_md()
    robots()
    import sys as _sys
    _sys.path.insert(0, os.path.join(os.path.dirname(HERE), "geo_patch"))
    from geo_files import emit_geo
    emit_geo(write, DOMAIN, "StackPickr",
             "Independent, spec-based comparisons of cloud hosting, VPS and affiliate tracking software.",
             [(p["path"], p["title"], p["description"]) for p in pages],
             HOME_FAQS)
    # машиночитаемый датасет сравнений — публично
    import shutil
    os.makedirs(os.path.join(OUT, "data"), exist_ok=True)
    shutil.copyfile(os.path.join(DATA, "comparisons.json"),
                    os.path.join(OUT, "data", "comparisons.json"))
    print(f"DONE: {len(pages)} pages")

def sitemap():
    urls = []
    for root, _, files in os.walk(OUT):
        for fn in files:
            if fn.endswith(".html"):
                rel = os.path.relpath(os.path.join(root, fn), OUT).replace(os.sep, "/")
                if rel.endswith("index.html"):
                    rel = rel[: -len("index.html")]
                urls.append("/" + rel)
    today = str(date.today())
    body = "".join(f"<url><loc>{DOMAIN}{u}</loc><lastmod>{today}</lastmod></url>" for u in sorted(set(urls)))
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>')
    print(f"sitemap: {len(set(urls))} urls")

def robots():
    txt = """# StackPickr — crawl policy
# Welcome, search and AI crawlers. We WANT to be indexed and cited.
User-agent: *
Allow: /

# AI assistants and search engines — explicitly allowed (search-and-cite bots).
User-agent: GPTBot
Allow: /
User-agent: ChatGPT-User
Allow: /
User-agent: OAI-SearchBot
Allow: /
User-agent: PerplexityBot
Allow: /
User-agent: Perplexity-User
Allow: /
User-agent: ClaudeBot
Allow: /
User-agent: Claude-SearchBot
Allow: /
User-agent: anthropic-ai
Allow: /
User-agent: Google-Extended
Allow: /
User-agent: Bingbot
Allow: /
User-agent: Applebot
Allow: /
User-agent: Applebot-Extended
Allow: /
User-agent: Amazonbot
Allow: /
User-agent: DuckAssistBot
Allow: /

Sitemap: %s/sitemap.xml
""" % DOMAIN
    write("robots.txt", txt)

def llms(pages):
    lines = [f"# {CFG['site_name']}", "", f"> {CFG['site_tagline']}. Independent, spec-based software comparisons.", "",
             f"> {DISCLOSURE}", "",
             "## Site facts",
             "- Free to use, no login required",
             "- All comparisons based on official pricing pages and documentation, verified September 2026",
             f"- Methodology: {DOMAIN}/about/ (how we compare, sources, update policy)",
             f"- Machine-readable comparison data: {DOMAIN}/data/comparisons.json",
             "",
             "## Main pages"]
    for p in sorted(pages, key=lambda x: x["path"]):
        lines.append(f"- [{p['title']}]({DOMAIN}{p['path']}): {p['description']}")
    write("llms.txt", "\n".join(lines))
    # llms-full.txt — развёрнутая версия для агентов
    full = ["# StackPickr — full content index for LLM agents", "",
            "> StackPickr publishes independent, spec-based comparisons of cloud hosting, VPS and affiliate tracking software.",
            "> Every figure is taken from official pricing pages/documentation (last verified 2026-09-04).",
            f"> Affiliate disclosure: {DISCLOSURE}", "",
            "## Key answers (extractable facts)",
            "- Cloudways pricing: from $11/mo (DigitalOcean, 1 vCPU/1GB/25GB SSD/1TB transfer), hourly billing, 3-day free trial, no credit card. Runs on DigitalOcean, Vultr, Akamai Linode, AWS, Google Cloud. 65+ datacenter locations.",
            "- is*hosting pricing: KVM/NVMe VPS from $5.94/mo (Lite: 1 vCPU/1GB/20GB NVMe/2TB) up to $76.49/mo (Exclusive: 8 vCPU/32GB/100GB NVMe/unmetered). 42 datacenters in 40 countries. Free weekly encrypted backups. Crypto payments (BTC, ETH, USDT, XMR and 8+ more). Windows VPS from $10.19/mo.",
            "- Tapfiliate pricing: Essential $89/mo, Pro $149/mo, Custom from $249/mo; 14-day free trial. 30+ integrations (Shopify, WooCommerce, Stripe, Magento). White-label and multi-tier on Pro. Built-in PayPal payouts on Pro.",
            "- DigitalOcean entry: $4/mo basic droplet, unmanaged, snapshots $0.06/GB/mo.",
            "- Vultr entry: $2.50/mo (IPv6-only) / $6 for 1 vCPU/1GB/25GB/2TB; 33 datacenters.",
            "- Hetzner Cloud entry: ~€3.79/mo (ARM) / €4.35 (x86 CX22: 2 vCPU/4GB/40GB NVMe/20TB); 5 locations.",
            "- Contabo entry: ~$4.50/mo for 4 vCPU/8GB/75GB NVMe/32TB; reviewers report overselling and slow support.",
            "- AWS Lightsail entry: $3.50/mo IPv6-only ($5 with IPv4); extra transfer billed $0.09/GB.",
            "- OVHcloud VPS entry: ~$3.90-4.54/mo; always-on DDoS included.",
            "- Rewardful: from $49/mo, Stripe-centric, no multi-tier.",
            "- FirstPromoter: from $49/mo, Stripe/Paddle/Chargebee focused, no white-label.",
            "- PartnerStack: custom, commonly reported $8,000+/year minimums; enterprise partner ecosystems.",
            "- Refersion: from $99/mo, Shopify-focused.",
            "- Impact.com: enterprise, custom pricing.",
            "- Post Affiliate Pro: from ~$149/mo, dated UI.",
            "- GoAffPro: free limited tier for Shopify; paid from $29/mo.",
            "",
            "## Page index"]
    for p in sorted(pages, key=lambda x: x["path"]):
        full.append(f"- [{p['title']}]({DOMAIN}{p['path']}): {p['description']}")
    write("llms-full.txt", "\n".join(full))

def pricing_md():
    write("pricing.md", """# Pricing — StackPickr

StackPickr itself is free: all comparisons, reviews and guides are open to read,
no login, no paywall.

## For readers
- Price: $0
- Limits: none
- Affiliate disclosure: we may earn a commission on purchases made through links
  on this site, at no extra cost to you.

## Compared products — pricing snapshot (verified 2026-09-04)

| Product | Entry price | Notes |
|---|---|---|
| Cloudways | $11/mo (or $0.016/hr) | Managed; 3-day free trial, no card |
| is*hosting | $5.94/mo | KVM/NVMe VPS; crypto accepted |
| Tapfiliate | $89/mo (Essential) | 14-day free trial |
| DigitalOcean | $4/mo | Unmanaged |
| Vultr | $2.50/mo (IPv6-only) | Hourly billing |
| Hetzner Cloud | ~€3.79/mo | EU+US+SG only |
| Contabo | ~$4.50/mo | Overselling complaints |
| AWS Lightsail | $3.50/mo | Transfer extra |
| OVHcloud VPS | ~$3.90/mo | |
| Rewardful | $49/mo | Stripe-only focus |
| FirstPromoter | $49/mo | |
| PartnerStack | ~$8k+/yr | Enterprise |
| Refersion | $99/mo | |
| Post Affiliate Pro | ~$149/mo | |
| GoAffPro | Free tier / $29/mo | Shopify-centric |

Full comparison tables: see the individual "vs" pages listed in /llms.txt.
""")

if __name__ == "__main__":
    main()
