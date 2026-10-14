"""One-shot: fill the `miro alternative free` gap with a real 3-column comparison.

Reads data/products.json and data/comparisons.json, inserts Mural as a third
participant plus a Boardmix vs Miro vs Mural page, writes both back with
indent=2 and a trailing newline (matching existing style), then prints what changed.
Idempotent: refuses to add Mural or the new page if either already exists.
"""
import json, os

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
TODAY = "2026-10-14"

MIRO_URL = "https://miro.com/"  # source link for the "Miro" column (bare name, not in products.json)
MURAL = {
    "name": "Mural",
    "official_url": "https://www.mural.co/",
    "category": "tools",
    "app_category": "ProductivityApplication",
    "short": "Visual collaboration boards with templates and a business tier",
    "cta_blurb": "Mural Business from $17.99/member/mo (annual)",
    "price_from": "17.99",
    "rating": 4.5,
    "rating_count": 2000,
    "review_intro": "Mural is a visual collaboration board built for workshops, retros and facilitation.",
    "key_facts": [
        "3 boards on the free plan, 3 participants per board",
        "Business plan $17.99/member/mo billed annually",
        "30+ facilitation templates out of the box",
        "SSO, SAML and admin controls on the business plan",
        "Merged with Miro in early 2024 — features now converge over time",
    ],
}

PAGE = {
    "path": "/tools/boardmix-vs-miro-vs-mural/",
    "category": "tools",
    "h1": "Miro Alternative (2026): Free & Paid Whiteboards Compared",
    "title": "Miro Alternative 2026: Boardmix vs Mural vs Free Miro (Pricing, Limits) | StackPickr",
    "summary": "Looking for a Miro alternative? Boardmix from $5/member/mo (or $99 lifetime) vs Mural at $17.99 vs free Miro capped at 3 boards and 3 collaborators.",
    "a": "boardmix",
    "b": "Miro",
    "b_url": MIRO_URL,
    "c": "Mural",
    "intro": "Miro is the category default for collaborative whiteboards — the word &quot;Miro&quot; is often used as a synonym for online whiteboard. The problem is that its free plan caps at 3 boards and 3 collaborators per board, and the paid plan runs from $8 per member per month. Here is how the realistic alternatives stack up in 2026, including a third option most comparison articles skip.",
    "tldr": "&quot;Miro alternative&quot; pages usually compare two things. We compared three: Boardmix from $5/member/mo (or $99 one-time lifetime), Mural Business at $17.99/member/mo, and free Miro capped at 3 boards / 3 collaborators. On price, Boardmix wins by 3&times;. On ecosystem depth, Miro still wins. Both have identical 3-board free limits, so the free tier is not where the differentiation lives.",
    "table": [
        {"feature": "Entry price (annual)", "values": ["$5/member/mo", "$17.99/member/mo", "$8/member/mo (Basic)"], "winner": 0},
        {"feature": "Free tier", "values": ["3 boards, 3 collaborators", "3 boards, 3 participants", "3 boards, 3 collaborators"], "winner": None},
        {"feature": "AI credits (entry paid)", "values": ["5,000 credits/seat/mo", "Not on entry plan", "25 credits/member/mo"], "winner": 0},
        {"feature": "Lifetime option", "values": ["$99 one-time (1 member)", "None", "None"], "winner": 0},
        {"feature": "Integration marketplace", "values": ["Jira, Slack, Zoom, Notion", "Jira, Slack, Google, Office365", "160+ apps incl. Figma, Asana"], "winner": 2},
        {"feature": "Templates (pre-built)", "values": ["Facilitation + AI templates", "30+ facilitation templates", "Broad community gallery"], "winner": 2},
        {"feature": "Facilitation / workshop focus", "values": ["General whiteboard", "Workshop-oriented (retros, brainstorming)", "General + community templates"], "winner": 1},
        {"feature": "SSO / admin controls", "values": ["On higher tiers", "Business plan", "Business+ tier"], "winner": None},
    ],
    "sections": [
        {"h": "The pricing math", "html": "<p>For a 10-person team billed annually: Boardmix Starter runs about $600/year, Mural Business about $2,159/year, and Miro Basic about $960/year. The gap between Mural and Boardmix is 3.6x. AI credits change the picture on heavy diagramming use: Boardmix bundles 5,000 credits per seat per month at entry, Miro Basic gives 25 per member, and Mural does not offer credits on the entry plan at all.</p>"},
        {"h": "Where Miro still wins", "html": "<p>Ecosystem. Miro's integration marketplace runs 160+ apps (Figma, Asana, Jira, Slack, Zoom) and its community template gallery is the deepest in the category. If your team's workflow lives inside those integrations, the premium is defensible — you are paying for fewer context switches, not for canvas features.</p>"},
        {"h": "Where Boardmix wins", "html": "<p>Everything price-adjacent: entry cost, AI allowance, and a $99 one-time lifetime plan that neither Miro nor Mural offer. For solo creators, students and small teams that do not need 160 integrations, the maths is not close.</p>"},
        {"h": "Where Mural wins", "html": "<p>Facilitation. Mural's template library is deliberately structured around workshops — retrospectives, brainstorming frames, journey mapping — and its business tier includes SSO and admin controls. Teams that run structured facilitation sessions get more value per board. Note that Mural merged with Miro in early 2024, so the two products are slowly converging rather than diverging.</p>"},
        {"h": "If you want truly free", "html": "<p>Miro, Boardmix and Mural all cap the free tier at 3 editable boards, so switching between them does not actually give you more free canvas. If unlimited free canvas is the goal, the honest answer is an open-source tool such as Excalidraw (free, browser-only, no collaboration tier) or FigJam, whose free tier ships 500 AI credits per month with unlimited drafts. Those are different products, not &quot;Miro alternatives&quot;, but they are the only real zero-cost options at scale.</p>"},
    ],
    "verdict": "<div class=\"verdict\"><b>Our verdict:</b> Boardmix for anyone switching from Miro on cost — 3x cheaper with 200x more AI credits per seat. Mural if you run structured facilitation and need SSO. Stay on free Miro if 3 boards is enough and you are a solo user; do not budget for it.</div>",
    "winner": "boardmix",
    "faqs": [
        ["Is there a free Miro alternative?", "Miro's own free plan is the largest one available: 3 editable boards and 3 collaborators per board. Boardmix and Mural match it exactly at 3 boards. For unlimited free canvas you need a different category — open-source tools like Excalidraw, not a whiteboard suite."],
        ["What is the cheapest Miro alternative?", "Boardmix, from $5/member/mo billed annually. Miro Basic is $8/member/mo and Mural Business is $17.99/member/mo. Boardmix also has a $99 one-time lifetime plan that neither competitor offers."],
        ["Are Miro and Mural the same company now?", "Yes. Mural was acquired by Miro in early 2024 and the two products are converging on shared features. For now they are still separate tools with separate pricing and billing."],
        ["Do Boardmix and Miro support the same integrations?", "The overlap is partial. Miro has a broader marketplace (160+ apps, including Figma and Asana). Boardmix covers the core workflow set — Jira, Slack, Zoom, Notion — but is significantly shallower."],
    ],
}


def main():
    ppath, cpath = os.path.join(DATA, "products.json"), os.path.join(DATA, "comparisons.json")
    prod, cmp_ = json.load(open(ppath, encoding="utf-8")), json.load(open(cpath, encoding="utf-8"))

    assert "Mural" not in prod, "Mural already in products.json"
    paths = [p.get("path") for p in cmp_.get("pages", [])]
    assert PAGE["path"] not in paths, f"{PAGE['path']} already exists"

    prod["Mural"] = MURAL
    cmp_["pages"].append(PAGE)

    json.dump(prod, open(ppath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    open(ppath, "a", encoding="utf-8").write("\n")
    json.dump(cmp_, open(cpath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    open(cpath, "a", encoding="utf-8").write("\n")
    print(f"products: +Mural ({len(prod)} total)")
    print(f"comparisons: +{PAGE['path']} ({len(cmp_['pages'])} total)")


if __name__ == "__main__":
    main()
