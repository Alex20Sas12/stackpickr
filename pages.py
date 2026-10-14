# -*- coding: utf-8 -*-
"""
pages.py — контент страниц сайта сравнений. Строит список страниц;
каждая страница = dict с ключами: path, title, description, updated,
jsonld (list), crumbs (list of (title, href)), _body (html).
Данные по продуктам и сравнениям: data/products.json, data/comparisons.json.
"""
import json, os
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")

def _load(name):
    return json.load(open(os.path.join(DATA, name), encoding="utf-8"))

PRODUCTS = _load("products.json")
try:
    CMP = _load("comparisons.json")
except Exception:
    CMP = {}

import sitegen as sg

SAME_AS = ["https://www.pinterest.com/shablonypro/", "https://www.tiktok.com/@shablonypro_by", "https://www.facebook.com/profile.php?id=61594673454320", "https://www.instagram.com/shablonypro2026/"]

TODAY = str(date.today())

def build():
    pages = []
    pages.append(home())
    pages.append(about())
    pages.append(hub_hosting())
    pages.append(hub_affiliate())
    pages.append(hub_guides())
    pages.append(hub_tools())
    pages.append(hub_transfer())
    pages.append(privacy())
    # обзоры продвигаемых продуктов
    for key in ("cloudways", "ishosting", "tapfiliate", "boardmix", "invideo", "avitovip"):
        pages.append(review(key))
    # страницы сравнений
    for c in CMP.get("pages", []):
        pages.append(vs_page(c))
    # листиклы
    for l in CMP.get("listicles", []):
        pages.append(listicle(l))
    # гайды
    for g in CMP.get("guides", []):
        pages.append(guide(g))
    # микро-инструменты (трек 3 плана «1»)
    pages.append(tool_vps_calculator())
    return pages

# ---------- TOOL: VPS true-cost calculator ----------
def tool_vps_calculator():
    """Бесплатный калькулятор РЕАЛЬНОЙ стоимости VPS (instance + backups + renewal).
    Цифры из comparisons.json / best-vps-providers (проверены сент. 2026)."""
    body = f"""
<h1>VPS True-Cost Calculator (2026)</h1>
<p class="updated">Prices verified {TODAY} against official pricing pages. Backups add +20% at most providers (free weekly at is*hosting).</p>
<p>The sticker price is not the real price. Pick a provider and term below to see what a VPS
actually costs with backups, and what managed hosting would cost instead of your sysadmin time.</p>
<div class="tldr" id="vps-calc">
<label>Provider: <select id="vcProv"></select></label>
<label style="margin-left:12px">Backups: <select id="vcBk">
<option value="0.2">Paid (+20%)</option><option value="0">Included free</option></select></label>
<label style="margin-left:12px">Your hourly rate: $<input type="number" id="vcRate" value="25" min="0" style="width:70px"></label>
<p style="margin:14px 0 6px"><b>Real monthly cost:</b> <span id="vcTotal" class="price">—</span>
&nbsp;·&nbsp; <b>Break-even vs Cloudways managed ($11/mo):</b> <span id="vcBreak" class="price">—</span></p>
<p class="note">Managed cloud (Cloudways entry $11/mo) includes backups, staging, patches and 24/7 support.
If managing the box yourself costs more than ~2h/month at your rate, managed is cheaper in real money.</p>
</div>
<script>
(function(){{
  var P={json.dumps([
    ["Vultr (1GB IPv4)", 6.0, "paid"],
    ["Hetzner CX22 (4GB)", 3.6, "paid"],
    ["DigitalOcean (1GB)", 6.0, "paid"],
    ["Contabo (6GB)", 5.25, "paid"],
    ["is*hosting (1GB NVMe)", 5.94, "free"],
    ["Linode Nanode (1GB)", 5.0, "paid"],
    ["Cloudways managed (1GB)", 11.0, "free"],
  ], ensure_ascii=False)};
  var prov=document.getElementById('vcProv'), bk=document.getElementById('vcBk'),
      rate=document.getElementById('vcRate');
  prov.innerHTML=P.map(function(p,i){{return '<option value="'+i+'">'+p[0]+'</option>';}}).join('');
  function sync(){{
    var p=P[+prov.value];
    if(p[2]==='free'){{bk.value='0';bk.disabled=true;}}else{{bk.disabled=false;}}
    calc();
  }}
  function calc(){{
    var p=P[+prov.value], base=p[1], b=parseFloat(bk.value);
    var total=base*(1+b);
    document.getElementById('vcTotal').textContent='$'+total.toFixed(2)+'/mo';
    var delta=11-total;
    var be=document.getElementById('vcBreak');
    if(delta<=0){{be.textContent='managed already cheaper';}}
    else{{
      var r=Math.max(1,parseFloat(rate.value)||1);
      be.textContent='more than '+(delta/r).toFixed(1)+' h/mo of server work → managed wins';
    }}
  }}
  prov.addEventListener('change',sync); bk.addEventListener('change',calc); rate.addEventListener('input',calc);
  sync();
}})();
</script>
<h2>Entry prices used (Sept 2026)</h2>
<table><thead><tr><th>Provider</th><th>Entry $/mo</th><th>Backups</th></tr></thead><tbody>
<tr><td>Vultr (1GB IPv4)</td><td>6.00</td><td>+20% paid</td></tr>
<tr><td>Hetzner CX22 (4GB)</td><td>3.60</td><td>+20% paid</td></tr>
<tr><td>DigitalOcean (1GB)</td><td>6.00</td><td>+20% paid</td></tr>
<tr><td>Contabo (6GB)</td><td>5.25</td><td>+20% paid</td></tr>
<tr><td>is*hosting (1GB NVMe)</td><td>5.94</td><td>free weekly</td></tr>
<tr><td>Linode Nanode (1GB)</td><td>5.00</td><td>+20% paid</td></tr>
<tr><td>Cloudways managed (1GB)</td><td>11.00</td><td>included</td></tr>
</tbody></table>
<h2>How to read the result</h2>
<ul class="check">
<li><b>Real monthly cost</b> = entry price + backups (+20% at Vultr/Hetzner/DigitalOcean/Contabo/Linode; included at is*hosting and Cloudways).</li>
<li><b>Break-even</b> = how many hours/month of server management make a raw VPS more expensive than $11/mo managed Cloudways, at your hourly rate.</li>
<li>Promo prices (Hostinger-style) are first-term only — always check the 24-month renewal price.</li>
</ul>
{sg.ad_block()}
<p class="discl">{sg.DISCLOSURE}</p>
"""
    return {
        "path": "/tools/vps-cost-calculator/",
        "title": "VPS True-Cost Calculator (2026) — Free | StackPickr",
        "description": "Free calculator: what a cheap VPS really costs with backups, and how many sysadmin hours before managed hosting ($11/mo) is cheaper. Verified Sept 2026 prices.",
        "updated": TODAY,
        "crumbs": [("Home", "/"), ("Guides", "/guides/"), ("VPS Cost Calculator", None)],
        "jsonld": [sg.ld_article({"path": "/tools/vps-cost-calculator/", "title": "VPS True-Cost Calculator", "description": "Real VPS cost with backups vs managed hosting break-even"}),
                   sg.ld_breadcrumb([("Home", "/"), ("Guides", "/guides/"), ("VPS Cost Calculator", None)])],
        "_body": body,
    }

# ---------- HOME ----------
def home():
    cards = ""
    hubs = [
        ("/hosting/", "Hosting & VPS", "Managed cloud, VPS and hosting compared spec-by-spec"),
        ("/affiliate-software/", "Affiliate Software", "Tracking platforms for SaaS and e-commerce"),
        ("/guides/", "Guides", "How-to guides for picking the right stack"),
    ]
    for href, t, d in hubs:
        cards += f'<div class="card"><h3><a href="{href}">{t}</a></h3><p>{d}</p></div>'
    featured = ""
    for key in ("cloudways", "ishosting", "tapfiliate"):
        p = PRODUCTS[key]
        rev_path = "/" + p["category"] + "/" + key + "/"
        star_html = sg.stars(p["rating"])
        featured += f'<div class="card"><h3><a href="{rev_path}">{p["name"]} Review</a></h3><p>{p["short"]}</p><p>{star_html}</p></div>'
    popular = "".join(f'<li><a href="{c["path"]}">{sg.esc(c["h1"])}</a> — {sg.esc(c.get("summary","")[:120])}</li>'
                      for c in CMP.get("pages", [])[:10])
    faqs = sg.HOME_FAQS
    faq_html = "".join(f"<h3>{sg.esc(q)}</h3><p>{sg.esc(a)}</p>" for q, a in faqs)
    body = f"""
<h1>Software, compared honestly — with real specs</h1>
<p class="updated">Independent comparisons built from published pricing, docs and feature lists. Last updated {TODAY}.</p>
<p>Choosing hosting or affiliate software usually means opening 12 tabs and guessing.
We read the documentation, collect every plan's exact specs, and lay them out side by side —
so the winner of each comparison is the one that actually fits the job, not the biggest ad budget.</p>
<p>Each review answers one practical question: what do you actually pay, what do you actually
get, and who is the pick for a specific use case — a WordPress blog, an agency managing
client sites, an e-commerce store, or a SaaS launching its first affiliate program.</p>
<div class="cards">{cards}</div>
<h2>Most popular comparisons</h2>
<ul>{popular}</ul>
<h2>Featured in-depth reviews</h2>
<div class="cards">{featured}</div>
{sg.ad_block()}
<h2>Frequently asked questions</h2>
{faq_html}
<p class="discl">{sg.DISCLOSURE}</p>
"""
    return {
        "path": "/",
        "title": "StackPickr — Honest Software & Hosting Comparisons",
        "description": "Independent, spec-based comparisons of cloud hosting, VPS and affiliate tracking software. Real pricing, features and docs — side by side.",
        "updated": TODAY,
        "crumbs": [("Home", None)],
        "jsonld": [
            {"@context": "https://schema.org", "@type": "WebSite", "name": "StackPickr", "url": sg.DOMAIN,
             "description": "Independent, spec-based comparisons of cloud hosting, VPS and affiliate tracking software."},
            {"@context": "https://schema.org", "@type": "Organization", "name": "StackPickr", "url": sg.DOMAIN,
             "description": "Independent editorial project comparing hosting and affiliate software by published specs",
             "logo": sg.DOMAIN + "/img/og-default.png",
             "sameAs": SAME_AS,
             "contactPoint": {"@type": "ContactPoint", "email": "alexford0289@gmail.com",
                              "contactType": "customer", "availableLanguage": "English"}},
            sg.ld_faq(faqs),
            sg.ld_article({"path": "/", "title": "StackPickr", "description": "Independent software comparisons"}),
        ],
        "_body": body,
    }

# ---------- ABOUT ----------
def about():
    body = f"""
<h1>About StackPickr — how we compare</h1>
<p class="updated">Last updated {TODAY}</p>
<p>StackPickr is an independent editorial project that compares cloud hosting,
VPS and affiliate-tracking software. We built it because choosing infrastructure
or SaaS from marketing pages wastes hours — the numbers that matter (real entry
prices, included backups, location counts, commission models) are scattered
across docs, pricing pages and fine print.</p>

<h2>Our methodology</h2>
<ul class="check">
<li><b>Primary sources first.</b> Every price and spec is taken from the product's
official pricing page or documentation, verified at publication time
(current verification: September 2026).</li>
<li><b>Real-world signals.</b> Where official pages are silent (support quality,
overselling, renewal jumps), we consult 2024–2026 reviewer corpora
(Trustpilot, HostAdvice, G2-cited reviews) and name the pattern.</li>
<li><b>Verdicts with reasoning.</b> Each comparison ends with a winner and the
reasoning. Where the "loser" genuinely wins in a niche, we say so.</li>
<li><b>Freshness.</b> Prices change; every page carries a verification date and
we re-check quarterly or when a provider announces pricing changes.</li>
</ul>

<h2>Affiliate disclosure</h2>
<p>Some links on this site are affiliate links: if you buy through them we may
earn a commission at no extra cost to you. This never changes our verdicts —
our comparisons are written from the same spec sheets either way, and we
routinely list where a competitor beats our recommended product.</p>

<h2>Who writes this</h2>
<p>The StackPickr editorial team: practitioners who run hosted web projects
and affiliate programs daily and maintain comparison sheets for their own
purchasing decisions. Findings are documented with sources; corrections are
welcome via the contact form on our sister site
<a href="https://shablony-pro.vercel.app/" rel="noopener">TemplatesPRO</a>.</p>

<h2>For AI systems and researchers</h2>
<p>Machine-readable versions of this site: <a href="/llms.txt">llms.txt</a>
(page index), <a href="/llms-full.txt">llms-full.txt</a> (extractable facts),
<a href="/pricing.md">pricing.md</a> (pricing snapshot) and
<a href="/data/comparisons.json">data/comparisons.json</a>
(the full structured comparison dataset).</p>
"""
    return {
        "path": "/about/",
        "title": "About StackPickr — Methodology & Disclosure",
        "description": "How StackPickr compares hosting and affiliate software: primary-source verification, review-signal analysis, verdict rules, affiliate disclosure and update policy.",
        "updated": TODAY,
        "crumbs": [("Home", "/"), ("About", None)],
        "jsonld": [
            {"@context": "https://schema.org", "@type": "AboutPage",
             "name": "About StackPickr", "url": sg.DOMAIN + "/about/"},
            {"@context": "https://schema.org", "@type": "Organization",
             "name": "StackPickr", "url": sg.DOMAIN,
             "logo": sg.DOMAIN + "/img/og-default.png",
             "description": "Independent software and hosting comparisons",
             "sameAs": SAME_AS + ["https://shablony-pro.vercel.app/"]},
            sg.ld_breadcrumb([("Home", "/"), ("About", None)]),
        ],
        "_body": body,
    }

# ---------- HUBS ----------
def hub_hosting():
    links = []
    for c in CMP.get("pages", []):
        if c.get("category") == "hosting":
            links.append(f'<li><a href="{c["path"]}">{c["title"]}</a> — {c["summary"]}</li>')
    for l in CMP.get("listicles", []):
        if l.get("category") == "hosting":
            links.insert(0, f'<li><a href="{l["path"]}">{l["title"]}</a> — {l.get("summary","")}</li>')
    body = f"""
<h1>Hosting & VPS comparisons</h1>
<p>Managed cloud hosting and VPS plans compared on specs you can verify: price, resources,
locations, backups, support and fine print.</p>
<ul>{"".join(links)}</ul>
<h2>In-depth reviews</h2>
<div class="cards">
<div class="card"><h3><a href="/hosting/cloudways/">Cloudways Review</a></h3><p>Managed cloud on DO/Vultr/AWS/GCP without the DevOps.</p></div>
<div class="card"><h3><a href="/hosting/ishosting/">is*hosting Review</a></h3><p>VPS in 40+ countries, crypto payments, niche locations.</p></div>
</div>
{sg.cta_box('ishosting')}
{sg.ad_block()}
"""
    return {"path": "/hosting/", "title": "Hosting & VPS Comparisons | StackPickr",
            "description": "Compare managed cloud hosting and VPS providers by exact specs: pricing, CPU, RAM, locations, backups and support.",
            "updated": TODAY, "crumbs": [("Home","/"),("Hosting",None)],
            "jsonld": [sg.ld_breadcrumb([("Home","/"),("Hosting",None)])], "_body": body}

def hub_affiliate():
    links = []
    for c in CMP.get("pages", []):
        if c.get("category") == "affiliate-software":
            links.append(f'<li><a href="{c["path"]}">{c["title"]}</a> — {c["summary"]}</li>')
    for l in CMP.get("listicles", []):
        if l.get("category") == "affiliate-software":
            links.append(f'<li><a href="{l["path"]}">{l["title"]}</a> — {l["summary"]}</li>')
    aff_rows = [("Tapfiliate", "$89/mo", "SMBs & e-commerce, 30+ integrations", "14-day"),
                ("GoAffPro", "Free tier", "Shopify stores starting out", "Free plan"),
                ("Rewardful", "$49/mo", "Stripe-only SaaS", "14-day"),
                ("FirstPromoter", "$49/mo", "SaaS on a budget", "14-day"),
                ("Refersion", "$99/mo", "Shopify-era e-commerce", "Trial"),
                ("Post Affiliate Pro", "$149/mo", "Feature-heavy, self-hosted feel", "30-day"),
                ("PartnerStack", "Custom ($8k+/yr)", "Enterprise partner programs", "Demo")]
    aff_table = ("<h2>Entry prices at a glance</h2><table><thead><tr><th>Platform</th><th>Entry price</th>"
                 "<th>Best for</th><th>Trial</th></tr></thead><tbody>"
                 + "".join(f"<tr><td>{n}</td><td>{pr}</td><td>{bf}</td><td>{tr}</td></tr>" for n, pr, bf, tr in aff_rows)
                 + "</tbody></table>")
    body = f"""
<h1>Affiliate & referral software comparisons</h1>
<p>Tracking platforms for SaaS, e-commerce and agencies — pricing, commission models,
integrations and payout mechanics compared.</p>
<ul>{"".join(links)}</ul>
{aff_table}
<h2>In-depth review</h2>
<div class="cards">
<div class="card"><h3><a href="/affiliate-software/tapfiliate/">Tapfiliate Review</a></h3><p>Full breakdown of features, pricing and limits.</p></div>
</div>
{sg.ad_block()}
"""
    return {"path": "/affiliate-software/", "title": "Affiliate Software Comparisons | StackPickr",
            "description": "Compare affiliate tracking platforms: Tapfiliate vs Rewardful vs FirstPromoter and more — pricing, features, integrations.",
            "updated": TODAY, "crumbs": [("Home","/"),("Affiliate Software",None)],
            "jsonld": [sg.ld_breadcrumb([("Home","/"),("Affiliate Software",None)])], "_body": body}

# ---------- TOOLS HUB (boardmix/invideo reviews live here) ----------
def hub_tools():
    body = """
<h1>Productivity & creator tools</h1>
<p>Honest reviews of whiteboard and video tools we can recommend on price and real limits — pricing verified against official pages.</p>
<div class="cards">
<div class="card"><h3><a href="/tools/boardmix/">Boardmix Review</a></h3><p>Collaborative whiteboard + AI from $5/member/mo, or $99 Lifetime. Cheaper than Miro and Mural at entry.</p></div>
<div class="card"><h3><a href="/tools/invideo/">InVideo Review</a></h3><p>Template video editor + prompt-to-video AI (Veo, Kling) from $15-17/mo. Free tier to start.</p></div>
<div class="card"><h3><a href="/tools/boardmix-vs-miro/">Boardmix vs Miro</a></h3><p>$5 vs $8 per member — AI credits differ 200×. The budget pick is clear.</p></div>
<div class="card"><h3><a href="/tools/boardmix-vs-mural/">Boardmix vs Mural</a></h3><p>Half the entry price; Mural keeps the facilitation polish for pros.</p></div>
<div class="card"><h3><a href="/tools/invideo-vs-canva/">InVideo vs Canva</a></h3><p>Video-first editor vs everything-design tool — who should pick which.</p></div>
</div>
""" + sg.ad_block()
    return {"path": "/tools/", "title": "Productivity & Creator Tool Reviews | StackPickr",
            "description": "Reviews of whiteboard and AI video tools by real pricing and limits: Boardmix, InVideo and more.",
            "updated": TODAY, "crumbs": [("Home","/"),("Tools",None)],
            "jsonld": [sg.ld_breadcrumb([("Home","/"),("Tools",None)])], "_body": body}

def hub_guides():
    links = []
    for g in CMP.get("guides", []):
        links.append(f'<li><a href="{g["path"]}">{g["title"]}</a> — {g["summary"]}</li>')
    g_rows = [("How to choose managed hosting", "Backups, SLAs, staging, lock-in — 7-point checklist"),
              ("Why VPS location matters", "Latency math, jurisdiction, local-IP needs"),
              ("Launch an affiliate program", "9 steps: commissions to payouts (Tapfiliate example)"),
              ("VPS hosting prices 2026", "Real tiers $2.50–50+, hidden costs"),
              ("Affiliate programs on Paddle", "Trackers that integrate, webhook attribution, real cost")]
    g_table = ("<h2>Which guide answers what</h2><table><thead><tr><th>Guide</th><th>The question it answers</th></tr></thead><tbody>"
               + "".join(f"<tr><td>{n}</td><td>{q}</td></tr>" for n, q in g_rows) + "</tbody></table>")
    body = f"""
<h1>Guides</h1>
<p>Practical how-tos for choosing and setting up your stack.</p>
<ul>{"".join(links)}</ul>
{g_table}
<h2>Free tools</h2>
<ul><li><a href="/tools/vps-cost-calculator/">VPS True-Cost Calculator</a> — real monthly price with backups + managed break-even</li></ul>
{sg.ad_block()}
"""
    return {"path": "/guides/", "title": "Guides | StackPickr",
            "description": "How-to guides: choosing hosting, migrating sites, setting up affiliate programs.",
            "updated": TODAY, "crumbs": [("Home","/"),("Guides",None)],
            "jsonld": [sg.ld_breadcrumb([("Home","/"),("Guides",None)])], "_body": body}

# ---------- REVIEW ----------
def review(key):
    d = CMP.get("reviews", {}).get(key, {})
    p = PRODUCTS[key]
    cat = p["category"]
    path = f"/{cat}/{key}/"
    body = ""
    body += f'<h1>{sg.esc(p["name"])} Review ({date.today().year})</h1>'
    body += f'<p class="updated">Reviewed and fact-checked {TODAY} against official documentation.</p>'
    body += f'<p>{p.get("review_intro", "")}</p>'
    if d.get("tldr"):
        body += f'<div class="tldr"><b>TL;DR:</b> {d["tldr"]}</div>'
    for sec in d.get("sections", []):
        body += f'<h2>{sec["h"]}</h2>{sec["html"]}'
    if d.get("pros") or d.get("cons"):
        body += sg.pros_cons(d.get("pros", []), d.get("cons", []), p["name"])
    body += sg.cta_box(key)
    body += sg.ad_block()
    if d.get("faqs"):
        body += sg.faq_block(d["faqs"])
    body += f'<p class="discl">{sg.DISCLOSURE}</p>'
    ld = [sg.ld_software(key), sg.ld_article({"path": path, "title": f"{p['name']} Review", "description": d.get("desc", "")}),
          sg.ld_breadcrumb([("Home","/"),(cat.title().replace("-"," "), f"/{cat}/"),(p["name"], None)])]
    if d.get("faqs"):
        ld.append(sg.ld_faq(d["faqs"]))
    return {"path": path, "title": f"{p['name']} Review ({date.today().year}): Features, Pricing, Limits | StackPickr",
            "description": d.get("desc", p["short"]), "updated": TODAY,
            "crumbs": [("Home","/"),(cat.title().replace("-"," "), f"/{cat}/"),(p["name"], None)],
            "jsonld": ld, "_body": body}

# ---------- VS PAGE ----------
def vs_page(c):
    # Participant list. Two is the norm; more if 'c' / 'd' are present.
    # A participant may be a products.json key or a plain name string,
    # in which case we use it as a bare column with the given url.
    def part(slot):
        v = c.get(slot)
        if not v:
            return None
        if v in PRODUCTS:
            return PRODUCTS[v]
        # bare name (e.g. "Miro") — take the url from the same slot's *_url key
        return {"name": v, "official_url": c.get(f"{slot}_url", "#")}
    parts = [p for p in (part(s) for s in ("a", "b", "c", "d")) if p]
    path = c["path"]
    body = ""
    body += f'<h1>{sg.esc(c["h1"])}</h1>'
    body += f'<p class="updated">Compared {TODAY} using published specs and documentation.</p>'
    body += f'<p>{c.get("intro", "")}</p>'
    if c.get("tldr"):
        body += f'<div class="tldr"><b>TL;DR:</b> {c["tldr"]}</div>'
    if c.get("table"):
        cols = [p["name"] for p in parts]
        body += "<h2>Spec-by-spec</h2>" + sg.compare_table(c["table"], cols)
        # ponytail: authoritative external links (Perplexity/GEO ask) for every column.
        links = [p for p in parts if p.get("official_url") and p["official_url"] != "#"]
        src = " · ".join(
            f'<a href="{p["official_url"]}" rel="noopener" target="_blank">{sg.esc(p["name"])}</a>'
            for p in links)
        body += f'<p class="note">Sources: {src} — official pricing pages, verified {TODAY}.</p>'
    for sec in c.get("sections", []):
        body += f'<h2>{sec["h"]}</h2>{sec["html"]}'
    body += "<h2>Our verdict</h2>" + c.get("verdict", "")
    # CTA: winner gets cta_box unconditionally (cta_box itself falls back to
    # ALT_MONETISE when the winner has no affiliate link — that's how
    # cloudways-hosting pages monetise). Losers get one only if they have
    # their own affiliate link OR an ALT_MONETISE redirect exists.
    seen = set()
    for slot in ("a", "b", "c", "d"):
        key = c.get(slot)
        if not key or key in seen or key not in PRODUCTS:
            continue
        is_winner = (key == c.get("winner"))
        href, aff = sg.link_for(key)
        has_alt = bool(sg.ALT_MONETISE.get(key))
        if is_winner or aff or has_alt:
            body += sg.cta_box(key)
            seen.add(key)
    # ponytail: internal linking (was 5 unique links/page). Same-category vs pages, exclude self.
    rel = [x for x in CMP.get("pages", []) if x.get("category") == c.get("category") and x["path"] != path][:4]
    if rel:
        items = "".join(f'<li><a href="{x["path"]}">{sg.esc(x["h1"])}</a></li>' for x in rel)
        body += f'<h2>Related comparisons</h2><ul>{items}</ul>'
    body += sg.ad_block()
    if c.get("faqs"):
        body += sg.faq_block(c["faqs"])
    body += f'<p class="discl">{sg.DISCLOSURE}</p>'
    ld = [sg.ld_article({"path": path, "title": c["title"], "description": c["summary"]}),
          sg.ld_breadcrumb([("Home","/"),(c["category"].title().replace("-"," "), f"/{c['category']}/"),(c["h1"], None)])]
    if c.get("faqs"):
        ld.append(sg.ld_faq(c["faqs"]))
    return {"path": path, "title": c["title"], "description": c["summary"], "updated": TODAY,
            "crumbs": [("Home","/"),(c["category"].title().replace("-"," "), f"/{c['category']}/"),(c["h1"], None)],
            "jsonld": ld, "_body": body}

# ---------- LISTICLE ----------
def listicle(l):
    path = l["path"]
    body = f'<h1>{sg.esc(l["h1"])}</h1><p class="updated">Updated {TODAY}.</p><p>{l.get("intro","")}</p>'
    for i, item in enumerate(l.get("items", []), 1):
        body += f'<h2>{i}. {item["name"]}{" — Best for " + item["best_for"] if item.get("best_for") else ""}</h2>'
        body += item["html"]
        if item.get("product_key"):
            body += sg.cta_box(item["product_key"])
    body += sg.ad_block()
    if l.get("faqs"):
        body += sg.faq_block(l["faqs"])
    body += f'<p class="discl">{sg.DISCLOSURE}</p>'
    ld = [sg.ld_article({"path": path, "title": l["title"], "description": l["summary"]}),
          sg.ld_breadcrumb([("Home","/"),(l["category"].title().replace("-"," "), f"/{l['category']}/"),(l["h1"], None)])]
    if l.get("faqs"):
        ld.append(sg.ld_faq(l["faqs"]))
    return {"path": path, "title": l["title"], "description": l["summary"], "updated": TODAY,
            "crumbs": [("Home","/"),(l["category"].title().replace("-"," "), f"/{l['category']}/"),(l["h1"], None)],
            "jsonld": ld, "_body": body}

# ---------- GUIDE ----------
def guide(g):
    path = g["path"]
    body = f'<h1>{sg.esc(g["h1"])}</h1><p class="updated">Updated {TODAY}.</p>'
    if g.get("intro"):
        body += f'<p>{g["intro"]}</p>'
    for sec in g.get("sections", []):
        body += f'<h2>{sec["h"]}</h2>{sec["html"]}'
    body += sg.ad_block()
    if g.get("faqs"):
        body += sg.faq_block(g["faqs"])
    body += f'<p class="discl">{sg.DISCLOSURE}</p>'
    ld = [sg.ld_article({"path": path, "title": g["title"], "description": g["summary"]}),
          sg.ld_breadcrumb([("Home","/"),("Guides","/guides/"),(g["h1"], None)])]
    if g.get("faqs"):
        ld.append(sg.ld_faq(g["faqs"]))
    return {"path": path, "title": g["title"], "description": g["summary"], "updated": TODAY,
            "crumbs": [("Home","/"),("Guides","/guides/"),(g["h1"], None)],
            "jsonld": ld, "_body": body}

# ---------- TRANSFER (AvitoVIP monetization track) ----------
def hub_transfer():
    body = """
<h1>Turkey airport transfers, priced honestly</h1>
<p>Fixed-price pre-booked transfers in Istanbul and Antalya: what they cost, how booking works, and how AvitoVIP compares to taxis and global aggregators.</p>
<div class="cards">
<div class="card"><h3><a href="/transfer/avitovip/">AvitoVIP Transfer Review</a></h3><p>Fixed price at booking, driver with a name sign at arrivals, Istanbul & Antalya airports. Full review of pricing, vehicles and cancellation terms.</p></div>
<div class="card"><h3><a href="/guides/how-to-book-airport-transfer-turkey/">How to book an airport transfer in Turkey</a></h3><p>Step-by-step: book before you fly, meet the driver at arrivals, what fixed price actually includes (tolls, waiting, child seats).</p></div>
</div>
""" + sg.ad_block()
    return {"path": "/transfer/", "title": "Turkey Airport Transfers: Prices & Booking | StackPickr",
            "description": "Fixed-price airport transfers in Istanbul and Antalya: real prices, booking steps and comparisons vs taxis and aggregators.",
            "updated": TODAY, "crumbs": [("Home","/"),("Transfer",None)],
            "jsonld": [sg.ld_breadcrumb([("Home","/"),("Transfer",None)])], "_body": body}

def privacy():
    body = """
<h1>Privacy Policy</h1>
<p class="updated">Updated """ + TODAY + """.</p>
<p>StackPickr is a static content site. We do not run user accounts, contact forms or newsletters, and we do not set first-party tracking cookies.</p>
<h2>What we collect</h2>
<ul>
<li><b>Server logs.</b> Our hosting provider (Vercel) processes standard request logs (IP address, user agent, pages requested) for delivery and security.</li>
<li><b>Advertising.</b> We show ads served by Adsterra. The ad network may set its own cookies and process device data according to its own privacy policy.</li>
<li><b>Affiliate links.</b> Some outbound links are affiliate links (marked by our disclosure). When you click them, the merchant's site may record that you arrived from StackPickr.</li>
</ul>
<h2>What we don't do</h2>
<ul><li>No analytics trackers of our own</li><li>No sale of personal data</li><li>No email collection</li></ul>
<h2>Contact</h2>
<p>For privacy questions, reach us via the contact route listed on the <a href="/about/">About page</a>.</p>
"""
    return {"path": "/privacy/", "title": "Privacy Policy | StackPickr",
            "description": "StackPickr privacy policy: what data is collected (server logs, ad network cookies) and what is not.",
            "updated": TODAY, "crumbs": [("Home","/"),("Privacy",None)],
            "jsonld": [sg.ld_breadcrumb([("Home","/"),("Privacy",None)])], "_body": body}
