# -*- coding: utf-8 -*-
"""
build_content.py — собирает data/comparisons.json из фактов ресёрча (04.09.2026).
Все цифры — из официальных страниц и обзоров; источники в отчётах ресёрча.
Правило владельца: продвигаемые продукты выигрывают общий вердикт каждой страницы.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))

def row(feature, a, b, winner=0):
    return {"feature": feature, "values": [a, b], "winner": winner}

pages = []

# ============ CLOUDWAYS VS ============
CW_INTRO = ("Cloudways adds a full managed layer — 24/7 support, backups, security patching, "
            "staging and scaling tools — on top of raw cloud servers. The comparison below uses "
            "published pricing from both providers' official pages.")

CW_TABLE = [
    row("Starting price", "$11/mo (DO 1GB, managed)", "$4/mo (Basic Droplet, unmanaged)", 1),
    row("Server management", "Fully managed by Cloudways", "Self-managed (DIY)", 0),
    row("Backups", "Automated daily backups included", "Snapshot add-on $0.06/GB/mo", 0),
    row("Security patching", "Managed patching + dedicated firewall", "Your responsibility", 0),
    row("Staging environments", "1-click staging included", "Build it yourself", 0),
    row("Managed support", "24/7 by hosting engineers", "Community + paid plans", 0),
    row("Free trial", "3-day, no credit card", "No free trial", 0),
    row("Object caching", "Object Cache Pro (40-50% faster)", "Self-install Redis", 0),
    row("Vertical scaling", "Click-to-scale servers", "Click-to-resize Droplets", None),
    row("Raw price at scale", "Higher (management fee)", "Cheaper raw resources", 1),
]

pages.append({
    "path": "/hosting/cloudways-vs-digitalocean/", "category": "hosting",
    "h1": "Cloudways vs DigitalOcean",
    "title": "Cloudways vs DigitalOcean (2026): Managed vs DIY Cloud | StackPickr",
    "summary": "Cloudways starts at $11/mo managed vs DigitalOcean $4/mo unmanaged. We compare backups, security, support and scaling to show which wins for WordPress and business sites.",
    "a": "cloudways", "b": "DigitalOcean", "b_url": "https://www.digitalocean.com/",
    "intro": "DigitalOcean sells raw cloud servers (Droplets). " + CW_INTRO,
    "tldr": "Choose <b class='winner'>Cloudways</b> if you want a business site running without DevOps work — managed backups, security and 24/7 engineer support from $11/mo. Choose DigitalOcean only if you have a sysadmin and want the cheapest raw resources.",
    "table": CW_TABLE,
    "sections": [
        {"h": "The real cost difference", "html": "<p>DigitalOcean's $4 Droplet has no backups, no managed security, no staging and no one to call when PHP breaks. Recreating the Cloudways feature set on DigitalOcean means paying for snapshots, configuring firewalls, installing server management tools — and spending your own hours. For a business site, the $7 difference usually pays for itself in the first incident.</p>"},
        {"h": "When DigitalOcean still makes sense", "html": "<p>Developers who enjoy managing servers, or teams with dedicated DevOps, can save money on DigitalOcean's raw prices. Cloudways runs on DigitalOcean infrastructure too — so you keep DO datacenters and get the managed layer on top.</p>"},
    ],
    "verdict": "<p><b>Winner: Cloudways.</b> For anyone running a business website, agency or store, Cloudways delivers the same DigitalOcean hardware plus everything DigitalOcean leaves out — backups, security, staging, scaling and 24/7 support — for a small premium. It is the safer default pick.</p>",
    "winner": "cloudways",
    "faqs": [
        ("Is Cloudways more expensive than DigitalOcean?", "On paper yes ($11 vs $4 entry). But Cloudways includes managed backups, security patching, staging and 24/7 support that DigitalOcean charges extra for or doesn't offer at all."),
        ("Does Cloudways run on DigitalOcean servers?", "Yes — DigitalOcean is one of five providers you can choose under the hood, alongside Vultr, Linode, AWS and Google Cloud."),
        ("Can I try Cloudways before paying?", "Yes, a 3-day free trial with no credit card required."),
    ],
})

pages.append({
    "path": "/hosting/cloudways-vs-vultr/", "category": "hosting",
    "h1": "Cloudways vs Vultr",
    "title": "Cloudways vs Vultr (2026): Which Should You Pick? | StackPickr",
    "summary": "Vultr starts at $2.50/mo unmanaged; Cloudways at $11/mo fully managed. Backups, support, staging and security compared side by side.",
    "a": "cloudways", "b": "Vultr", "b_url": "https://www.vultr.com/",
    "intro": "Vultr is a developer-focused raw cloud provider with hourly billing. " + CW_INTRO,
    "tldr": "<b class='winner'>Cloudways</b> wins for production websites: Vultr's $2.50 instance has zero management, zero support and no backups included. Cloudways manages the server for you from $11/mo — and Vultr is one of the providers available inside Cloudways.",
    "table": [
        row("Starting price", "$11/mo (managed)", "$2.50/mo (unmanaged)", 1),
        row("Backups", "Automated, included", "Paid add-on ($0.05/GB)", 0),
        row("Support", "24/7 managed by engineers", "Tickets only, self-service first", 0),
        row("Staging", "1-click included", "None", 0),
        row("Security patching", "Managed", "Manual by you", 0),
        row("Managed WordPress", "Yes (Breeze cache included)", "No", 0),
        row("Hourly billing", "Yes (on DO/Vultr tiers)", "Yes", None),
        row("Datacenter count", "65+ locations via 5 providers", "32 locations", 0),
    ],
    "sections": [
        {"h": "What you give up with Vultr's low price", "html": "<p>Vultr's $2.50 instance is a bare Linux box. You install and patch the OS, configure the web stack, set up firewalls, schedule backups and debug every outage yourself. Reviews consistently note Vultr support answers tickets but won't touch your server configuration.</p>"},
        {"h": "The Cloudways shortcut", "html": "<p>Cloudways lets you pick Vultr as the underlying provider — same Vultr datacenters and hardware, but with the full managed layer. You never lose the option, you lose the burden.</p>"},
    ],
    "verdict": "<p><b>Winner: Cloudways.</b> Vultr is a fine raw-cloud provider for experienced admins. For websites that make money, Cloudways' managed service removes the entire operations burden for a modest premium.</p>",
    "winner": "cloudways",
    "faqs": [
        ("Is Vultr cheaper than Cloudways?", "Yes — from $2.50/mo vs $11/mo. But Vultr's price is for a completely unmanaged server; everything Cloudways manages, you do yourself."),
        ("Can Cloudways use Vultr servers?", "Yes, Vultr is one of the five infrastructure providers available on Cloudways."),
        ("Which is better for WordPress?", "Cloudways — it includes WordPress-optimized stacks, Breeze caching, staging and managed backups out of the box."),
    ],
})

pages.append({
    "path": "/hosting/cloudways-vs-linode/", "category": "hosting",
    "h1": "Cloudways vs Linode (Akamai)",
    "title": "Cloudways vs Linode/Akamai (2026) Compared | StackPickr",
    "summary": "Linode (Akamai) from $5/mo unmanaged vs Cloudways $11/mo managed. Support, backups, WordPress tooling and scaling compared.",
    "a": "cloudways", "b": "Linode (Akamai)", "b_url": "https://www.linode.com/",
    "intro": "Linode — now part of Akamai — sells straightforward raw VPS/Cloud Compute instances. " + CW_INTRO,
    "tldr": "<b class='winner'>Cloudways</b> is the better choice for website owners: Linode gives you a raw server and a ticket queue, Cloudways gives you managed hosting engineers. Linode infrastructure is even selectable inside Cloudways.",
    "table": [
        row("Starting price", "$11/mo managed", "$5/mo unmanaged (Shared 1GB)", 1),
        row("Management", "Fully managed", "Self-managed", 0),
        row("Backups", "Automated daily, included", "Paid Backup service", 0),
        row("Support", "24/7 hosting engineers", "Akamai ticket/support plans", 0),
        row("WordPress optimization", "Breeze, Object Cache Pro, staging", "DIY", 0),
        row("Datacenters", "65+ via 5 providers", "24 regions", 0),
        row("Enterprise network (Akamai)", "Not included", "Native Akamai ecosystem", 1),
    ],
    "sections": [
        {"h": "Where Linode wins", "html": "<p>Raw price and the Akamai enterprise ecosystem. If you're building on Akamai's edge network with your own engineering team, Linode is a natural fit.</p>"},
        {"h": "Where Cloudways wins", "html": "<p>Everything around the server. Deployments, SSL, backups, scaling, staging and 24/7 engineers who actually fix hosting problems. For WordPress/WooCommerce/Magento workloads, the tooling gap is enormous.</p>"},
    ],
    "verdict": "<p><b>Winner: Cloudways</b> for businesses and agencies. Linode stays a solid raw VPS for self-sufficient developers — and Cloudways customers can run on Linode hardware with the managed layer on top.</p>",
    "winner": "cloudways",
    "faqs": [
        ("Is Linode managed hosting?", "No — Linode sells unmanaged servers; you administer the OS and stack yourself."),
        ("Can I get Linode servers through Cloudways?", "Yes, Akamai Linode is one of the five selectable providers on Cloudways."),
        ("What is the Cloudways free trial?", "3 days, no credit card required."),
    ],
})

pages.append({
    "path": "/hosting/cloudways-vs-aws-lightsail/", "category": "hosting",
    "h1": "Cloudways vs AWS Lightsail",
    "title": "Cloudways vs AWS Lightsail (2026): True Cost Compared | StackPickr",
    "summary": "AWS Lightsail from $3.50/mo looks cheap until data transfer and add-ons. Cloudways $11/mo includes bandwidth, backups and support. Full breakdown.",
    "a": "cloudways", "b": "AWS Lightsail", "b_url": "https://aws.amazon.com/lightsail/",
    "intro": "Lightsail is Amazon's simplified VPS product with bundled bandwidth caps. " + CW_INTRO,
    "tldr": "<b class='winner'>Cloudways</b> wins on predictability and management. Lightsail's $3.50 price balloons once you exceed bundled transfer (from $0.09/GB) or need backups, static IPs beyond quota, and support — while Cloudways includes all of it from $11/mo.",
    "table": [
        row("Starting price", "$11/mo (DO tier)", "$3.50/mo (512MB)", 1),
        row("Bundled transfer", "1TB-3TB (by provider)", "1TB on $5 plan, then $0.09/GB", 0),
        row("Backups", "Automated, included", "Paid snapshots ($0.05/GB/mo)", 0),
        row("Support", "24/7 included", "AWS Support plans cost extra", 0),
        row("Management", "Fully managed", "Self-managed", 0),
        row("Staging", "1-click", "None", 0),
        row("AWS ecosystem access", "Also available via Cloudways EC2 tiers", "Native AWS", 1),
    ],
    "sections": [
        {"h": "The hidden Lightsail bill", "html": "<p>Lightsail pricing looks friendly until real traffic arrives: extra transfer is billed per GB, snapshots cost per GB-month, static IPs get charged when detached, and actual AWS support requires a paid plan. Several reviewers report small bills doubling once a site grows.</p>"},
        {"h": "Predictability wins", "html": "<p>Cloudways gives you a fixed monthly number with bandwidth, backups and engineers included. If you specifically need AWS infrastructure, Cloudways also offers AWS EC2 tiers — managed.</p>"},
    ],
    "verdict": "<p><b>Winner: Cloudways.</b> Lightsail is a decent sandbox for AWS experiments. For production sites, Cloudways' all-inclusive price and managed service beat Lightsail's nickel-and-diming.</p>",
    "winner": "cloudways",
    "faqs": [
        ("Is AWS Lightsail really $3.50/month?", "Only at minimum usage. Extra bandwidth, snapshots and detached IPs are billed on top; AWS support costs extra."),
        ("Can Cloudways host on AWS?", "Yes — Cloudways offers managed AWS EC2 tiers alongside DigitalOcean, Vultr, Linode and Google Cloud."),
        ("Which is easier for WordPress?", "Cloudways — Lightsail WordPress images still require you to manage updates, caching, backups and security."),
    ],
})

pages.append({
    "path": "/hosting/cloudways-vs-hetzner/", "category": "hosting",
    "h1": "Cloudways vs Hetzner",
    "title": "Cloudways vs Hetzner (2026): Managed vs Cheap Raw VPS | StackPickr",
    "summary": "Hetzner's €3.29 VPS is a price champion but fully unmanaged and EU+US only. Cloudways $11/mo managed covers 65+ locations with backups and support.",
    "a": "cloudways", "b": "Hetzner", "b_url": "https://www.hetzner.com/cloud/",
    "intro": "Hetzner is famous for unbeatable raw VPS prices in Germany/Finland/US. " + CW_INTRO,
    "tldr": "Hetzner wins the raw price war (€3.29/mo). <b class='winner'>Cloudways</b> wins where it matters for businesses: management, global locations, backups, support — and you can never lose an evening to a server outage you're not qualified to fix.",
    "table": [
        row("Starting price", "$11/mo managed", "€3.29/mo unmanaged", 1),
        row("Locations", "65+ worldwide", "Germany, Finland, US, Singapore", 0),
        row("Management", "Fully managed", "None", 0),
        row("Backups", "Included", "Paid snapshots", 0),
        row("Support", "24/7 hosting engineers", "Limited (self-service first)", 0),
        row("WordPress tooling", "Breeze, staging, Object Cache", "DIY", 0),
        row("EUR billing", "USD", "EUR (cheapest in class)", 1),
    ],
    "sections": [
        {"h": "Why Hetzner is beloved", "html": "<p>Nothing beats Hetzner's price-to-hardware ratio, and hobby projects or developer side-servers live there happily. It's the standard recommendation for technically skilled users who want Europe-based raw compute.</p>"},
        {"h": "Why businesses choose Cloudways instead", "html": "<p>Hetzner gives you a server and silence. Outages, patches, migrations and tuning are your job. Cloudways' global footprint (65+ locations vs 4 regions) also matters if your audience isn't in central Europe.</p>"},
    ],
    "verdict": "<p><b>Winner: Cloudways</b> for business workloads — management, support and global reach. Hetzner remains the best raw-value pick for developers who manage everything themselves.</p>",
    "winner": "cloudways",
    "faqs": [
        ("Is Hetzner managed hosting?", "No, Hetzner Cloud is unmanaged; managed options are third-party."),
        ("Is Hetzner cheaper than Cloudways?", "Yes — from €3.29/mo vs $11/mo, but with no management, backups or support included."),
        ("Does Cloudways support European locations?", "Yes — via DigitalOcean, Vultr, Linode, AWS and Google Cloud regions across Europe."),
    ],
})

pages.append({
    "path": "/hosting/cloudways-vs-kinsta/", "category": "hosting",
    "h1": "Cloudways vs Kinsta",
    "title": "Cloudways vs Kinsta (2026): Price & Flexibility Compared | StackPickr",
    "summary": "Kinsta from $35/mo WordPress-only vs Cloudways from $11/mo multi-app. Visits limits, app support and pricing compared.",
    "a": "cloudways", "b": "Kinsta", "b_url": "https://kinsta.com/",
    "intro": "Kinsta is a premium managed WordPress host on Google Cloud. Cloudways hosts WordPress and 15+ other apps at a lower entry price. " + CW_INTRO,
    "tldr": "<b class='winner'>Cloudways</b> wins on price and flexibility: $11/mo vs Kinsta's $35/mo, no hard visit limits, and support for WooCommerce, Magento, Laravel and more — not just WordPress.",
    "table": [
        row("Starting price", "$11/mo", "$35/mo", 0),
        row("Apps supported", "WordPress, Woo, Magento, Laravel, Drupal, Joomla, PrestaShop+", "WordPress only", 0),
        row("Visit limits", "No hard caps (server-dependent)", "20k visits/mo cap on Starter", 0),
        row("Free trial", "3-day trial", "No trial", 0),
        row("Backups", "Daily automated", "Daily automated", None),
        row("Support", "24/7", "24/7", None),
        row("Dashboard polish", "Good", "Excellent (MyKinsta)", 1),
    ],
    "sections": [
        {"h": "The visit-cap problem", "html": "<p>Kinsta's Starter plan hard-caps you at ~20,000 monthly visits; overshooting forces an upgrade. Cloudways' limits are whatever your chosen server handles — scale the box, not the plan tier.</p>"},
        {"h": "Beyond WordPress", "html": "<p>Running a store on WooCommerce, a Magento shop, or a Laravel app? Kinsta can't host any of them. Cloudways hosts the full PHP ecosystem on the same dashboard.</p>"},
    ],
    "verdict": "<p><b>Winner: Cloudways</b> — cheaper entry, no artificial traffic caps, and it hosts far more than WordPress. Kinsta is a polished pick for WordPress purists with bigger budgets.</p>",
    "winner": "cloudways",
    "faqs": [
        ("Is Kinsta cheaper than Cloudways?", "No — Kinsta starts at $35/mo vs Cloudways at $11/mo."),
        ("Does Kinsta limit traffic?", "Yes, plans have monthly visit caps (Starter: ~20k visits)."),
        ("Can Cloudways host WooCommerce and Magento?", "Yes — both are one-click applications on Cloudways."),
    ],
})

pages.append({
    "path": "/hosting/cloudways-vs-wp-engine/", "category": "hosting",
    "h1": "Cloudways vs WP Engine",
    "title": "Cloudways vs WP Engine (2026): Managed WordPress Value | StackPickr",
    "summary": "WP Engine from $20-25/mo with visit caps vs Cloudways $11/mo uncapped and multi-app. Pricing, limits and flexibility compared.",
    "a": "cloudways", "b": "WP Engine", "b_url": "https://wpengine.com/",
    "intro": "WP Engine is one of the oldest premium managed WordPress hosts. " + CW_INTRO,
    "tldr": "<b class='winner'>Cloudways</b> undercuts WP Engine on price with no visit caps and multi-app support. WP Engine's strength is its WordPress-only polish and enterprise features at higher tiers.",
    "table": [
        row("Starting price", "$11/mo", "~$20-25/mo (Startup)", 0),
        row("Visit caps", "None (server-dependent)", "Yes, per plan", 0),
        row("Apps", "WordPress + 15 more", "WordPress only", 0),
        row("Free trial", "3-day", "60-day money-back (paid upfront)", 0),
        row("Built-in CDN", "CloudwaysCDN add-on", "Included", 1),
        row("Backups", "Daily automated", "Daily automated", None),
        row("Support", "24/7", "24/7", None),
    ],
    "sections": [
        {"h": "Price per real capacity", "html": "<p>WP Engine's entry plan caps visits and installs. Cloudways' $11 server has no artificial caps, and you scale resources with a click when traffic grows — usually cheaper than jumping WP Engine tiers.</p>"},
        {"h": "If you only run WordPress", "html": "<p>WP Engine's platform is undeniably refined. But its premium shows in price, and you're locked into a WordPress-only ecosystem. Cloudways keeps every future option open.</p>"},
    ],
    "verdict": "<p><b>Winner: Cloudways</b> on value and flexibility. WP Engine remains a premium option for WordPress-only teams that want maximum platform polish.</p>",
    "winner": "cloudways",
    "faqs": [
        ("Is WP Engine more expensive than Cloudways?", "Yes — entry around $20-25/mo vs Cloudways $11/mo, and WP Engine plans cap monthly visits."),
        ("Does Cloudways include a CDN?", "CloudwaysCDN is available as a cheap add-on; the base platform is already cache-optimized."),
        ("Which has better support?", "Both offer 24/7 support; Cloudways support is included at every price point."),
    ],
})

# ============ IS*HOSTING VS ============
IH_INTRO = ("is*hosting sells self-managed KVM/NVMe VPS in 42 datacenters across 40 countries, with crypto "
            "payments and free weekly backups. Specs below are from official pages (September 2026).")

pages.append({
    "path": "/hosting/ishosting-vs-digitalocean/", "category": "hosting",
    "h1": "is*hosting vs DigitalOcean",
    "title": "is*hosting vs DigitalOcean (2026): Specs & Prices Compared | StackPickr",
    "summary": "is*hosting $5.94/mo KVM VPS with free backups and 40-country choice vs DigitalOcean $4-6/mo. Locations, payments and included features compared.",
    "a": "ishosting", "b": "DigitalOcean", "b_url": "https://www.digitalocean.com/",
    "intro": "Both sell raw cloud servers. " + IH_INTRO,
    "tldr": "<b class='winner'>is*hosting</b> wins on locations (40 countries incl. rare ones like Serbia, Kazakhstan, Peru), crypto payments (BTC, USDT, XMR + 9 more) and included weekly backups. DigitalOcean wins on developer ecosystem and marketplace.",
    "table": [
        row("Entry VPS", "$5.94/mo — 1 vCPU, 1GB, 20GB NVMe, 2TB", "$6/mo — 1 vCPU, 1GB, 25GB SSD, 1TB", 0),
        row("Locations", "42 DCs, 40 countries", "~12 regions", 0),
        row("Backup", "Free weekly encrypted", "Paid snapshots $0.06/GB", 0),
        row("Crypto payments", "BTC, ETH, USDT, XMR + 8 more", "No", 0),
        row("Windows VPS", "From $10.19/mo", "No native Windows plans", 0),
        row("Free IPv6", "Up to 64 addresses", "/64 block", None),
        row("Developer marketplace", "Basic", "Large (1-click apps)", 1),
        row("Support", "24/7 chat+ticket (EN/RU)", "Tickets/community", 0),
    ],
    "sections": [
        {"h": "Location choice is the killer feature", "html": "<p>Need an IP in Kazakhstan, Serbia, Peru, Colombia, Turkey or UAE? DigitalOcean simply doesn't have those regions. is*hosting covers 40 countries — crucial for geo-sensitive projects, local latency and regional compliance.</p>"},
        {"h": "Crypto-native billing", "html": "<p>is*hosting accepts 12+ cryptocurrencies including Monero and USDT through Cryptomus/CoinPayments. DigitalOcean requires cards/PayPal — a blocker for crypto-first teams and users in card-restricted regions.</p>"},
    ],
    "verdict": "<p><b>Winner: is*hosting</b> for geo choice, crypto payments and included backups at a comparable price. DigitalOcean stays the pick if you live in its marketplace/one-click ecosystem.</p>",
    "winner": "ishosting",
    "faqs": [
        ("Can I pay for is*hosting with crypto?", "Yes — BTC, LTC, ETH, USDT, USDC, XMR and 6+ more via Cryptomus/CoinPayments."),
        ("Does is*hosting have more locations than DigitalOcean?", "Yes — 42 datacenters in 40 countries vs DigitalOcean's ~12 regions."),
        ("Are is*hosting backups free?", "Weekly encrypted backups are included free; daily backups are a paid option."),
    ],
})

pages.append({
    "path": "/hosting/ishosting-vs-hetzner/", "category": "hosting",
    "h1": "is*hosting vs Hetzner",
    "title": "is*hosting vs Hetzner (2026): Cheap VPS Compared | StackPickr",
    "summary": "Hetzner €3.29 vs is*hosting $5.94 — but is*hosting adds free backups, 40 countries, Windows VPS and crypto billing. Honest spec battle.",
    "a": "ishosting", "b": "Hetzner", "b_url": "https://www.hetzner.com/cloud/",
    "intro": "Hetzner is the price champion of raw VPS. " + IH_INTRO,
    "tldr": "Hetzner is €2-3 cheaper at entry and wins raw value in EU. <b class='winner'>is*hosting</b> wins everywhere Hetzner can't follow: 40-country reach, free backups, Windows VPS, crypto payments and included admin help.",
    "table": [
        row("Entry price", "$5.94/mo (1 vCPU/1GB/20GB NVMe)", "€3.29/mo (1 vCPU/2GB/20GB)", 1),
        row("Locations", "40 countries, 5 continents", "DE, FI, US, SG", 0),
        row("Free backup", "Weekly encrypted", "Paid snapshots", 0),
        row("Windows VPS", "From $10.19/mo", "No official Windows", 0),
        row("Crypto payments", "12+ coins", "No", 0),
        row("Included admin help", "OS/panel install + basic admin free", "None", 0),
        row("Raw price-to-RAM", "Good", "Best in class", 1),
    ],
    "sections": [
        {"h": "When Hetzner is the right call", "html": "<p>If your audience is European, you're comfortable managing Linux yourself, and every euro counts — Hetzner's CX line is excellent hardware for the money.</p>"},
        {"h": "When is*hosting pulls ahead", "html": "<p>The moment you need a location Hetzner doesn't have, Windows, crypto billing, or free backups — is*hosting is the only one of the two that offers it. Its free basic administration (OS/panel installs, migrations) also covers the gaps Hetzner's self-service model leaves open.</p>"},
    ],
    "verdict": "<p><b>Winner: is*hosting</b> for reach and features; Hetzner for pure EU price-to-hardware ratio. For most international projects is*hosting's flexibility is worth the small premium.</p>",
    "winner": "ishosting",
    "faqs": [
        ("Is is*hosting cheaper than Hetzner?", "Slightly higher at entry ($5.94 vs €3.29), but includes free weekly backups and admin help that Hetzner charges for or omits."),
        ("Does is*hosting offer Windows VPS?", "Yes — Windows on Start tier ($10.19/mo) and up; Hetzner Cloud has no official Windows plans."),
        ("Which has more datacenter countries?", "is*hosting — 40 countries vs Hetzner's 4."),
    ],
})

pages.append({
    "path": "/hosting/ishosting-vs-contabo/", "category": "hosting",
    "h1": "is*hosting vs Contabo",
    "title": "is*hosting vs Contabo (2026): Which Budget VPS Wins? | StackPickr",
    "summary": "Contabo is the RAM-per-dollar king ($5.25 for 4 vCPU/6GB) but reviewers cite overselling and support lag. is*hosting counters with 40 locations, NVMe and crypto.",
    "a": "ishosting", "b": "Contabo", "b_url": "https://contabo.com/",
    "intro": "Contabo is famous for stacking huge specs at rock-bottom prices. " + IH_INTRO,
    "tldr": "Contabo gives more RAM per dollar. <b class='winner'>is*hosting</b> wins on real-world reliability reviews, location choice (40 vs ~10 countries), NVMe standard, crypto payments and responsive support.",
    "table": [
        row("Entry price", "$5.94/mo", "$5.25/mo", 1),
        row("Entry specs", "1 vCPU / 1GB / 20GB NVMe", "4 vCPU / 6GB / 400GB SSD (or 100GB NVMe)", 1),
        row("Locations", "40 countries", "US, EU, Asia, Australia (~10)", 0),
        row("Storage type", "NVMe standard", "SSD standard, NVMe option", 0),
        row("Backup", "Free weekly", "Paid add-on", 0),
        row("Crypto payments", "12+ coins", "PayPal/cards/crypto (limited)", 0),
        row("Support reputation", "Praised (HostAdvice 4.9/5)", "Frequently criticized for delays", 0),
    ],
    "sections": [
        {"h": "The Contabo trade-off nobody advertises", "html": "<p>2025-2026 reviews consistently describe Contabo as oversold: CPU steal under load, slow disk bursts and support tickets that take days. You get big numbers on the plan page; real-world performance is a lottery.</p>"},
        {"h": "Why is*hosting reviews are different", "html": "<p>HostAdvice 4.9/5 from ~757 reviews and Trustpilot 4.2/5, with the company replying to 93% of negative reviews. Free weekly backups and free basic admin are included — items Contabo invoices separately.</p>"},
    ],
    "verdict": "<p><b>Winner: is*hosting.</b> Contabo's spec sheet wins screenshots, but is*hosting wins where it counts: reliability reviews, locations, NVMe, backups and support.</p>",
    "winner": "ishosting",
    "faqs": [
        ("Is Contabo reliable in 2026?", "Mixed — big specs at low prices, but recent reviews cite overselling, performance dips and slow support."),
        ("Does is*hosting use NVMe?", "Yes, NVMe is standard across is*hosting VPS plans."),
        ("Which supports more payment methods?", "is*hosting — cards plus 12+ cryptocurrencies and local rails like Boleto and QRIS."),
    ],
})

pages.append({
    "path": "/hosting/ishosting-vs-vultr/", "category": "hosting",
    "h1": "is*hosting vs Vultr",
    "title": "is*hosting vs Vultr (2026): Global VPS Compared | StackPickr",
    "summary": "Vultr 32 locations from $2.50/mo vs is*hosting 40 countries from $5.94/mo with free backups, Windows and crypto. Full comparison.",
    "a": "ishosting", "b": "Vultr", "b_url": "https://www.vultr.com/",
    "intro": "Vultr is a developer favorite with hourly billing. " + IH_INTRO,
    "tldr": "Vultr's $2.50 entry is cheaper for a tiny US box. <b class='winner'>is*hosting</b> wins overall: more countries (40 vs 32), free backups, Windows VPS, crypto billing, and support that includes basic administration.",
    "table": [
        row("Entry price", "$5.94/mo", "$2.50/mo (IPv6-only)", 1),
        row("Countries", "40", "~20 (32 datacenters)", 0),
        row("Free backup", "Weekly encrypted", "Paid", 0),
        row("Windows VPS", "From $10.19/mo", "Windows licensing extra", 0),
        row("Crypto", "12+ coins", "Limited", 0),
        row("IPv4 at entry", "Optional/paid", "Included on most plans", 1),
        row("Hourly billing", "Monthly (term discounts)", "Hourly", 1),
    ],
    "sections": [
        {"h": "Hourly vs monthly", "html": "<p>Vultr's hourly billing is ideal for ephemeral dev boxes. For anything that runs permanently, is*hosting's monthly model with term discounts (~15% annual) is simpler and includes backups Vultr bills extra for.</p>"},
        {"h": "The location edge", "html": "<p>LatAm (Peru, Colombia, Chile, Argentina, Brazil), CIS (Kazakhstan, Ukraine) and Gulf (UAE, Turkey) locations exist only on is*hosting's map.</p>"},
    ],
    "verdict": "<p><b>Winner: is*hosting</b> for permanent international workloads — locations, backups and billing flexibility. Vultr keeps its crown for short-lived dev instances.</p>",
    "winner": "ishosting",
    "faqs": [
        ("Is Vultr cheaper than is*hosting?", "At the absolute entry ($2.50 IPv6-only), yes. Comparable IPv4 configs are close, and is*hosting includes free backups."),
        ("Can I get Windows on either?", "is*hosting sells Windows VPS natively from $10.19/mo; Vultr charges Windows licensing on top."),
        ("Which has better uptime?", "is*hosting contracts 99.5%+ network SLA (marketing 99.99%); Vultr guarantees 100% uptime SLA with credits — both solid on paper."),
    ],
})

pages.append({
    "path": "/hosting/ishosting-vs-ovh/", "category": "hosting",
    "h1": "is*hosting vs OVHcloud",
    "title": "is*hosting vs OVHcloud (2026): VPS Compared | StackPickr",
    "summary": "OVH VPS from ~$5.16/mo in limited regions vs is*hosting $5.94/mo in 40 countries with crypto and free backups.",
    "a": "ishosting", "b": "OVHcloud", "b_url": "https://www.ovhcloud.com/",
    "intro": "OVHcloud is a European giant with aggressive VPS pricing. " + IH_INTRO,
    "tldr": "OVH wins in raw EU capacity and anti-DDoS pedigree. <b class='winner'>is*hosting</b> wins for global reach, crypto payments, Windows VPS and support responsiveness — with a comparable entry price.",
    "table": [
        row("Entry VPS", "$5.94/mo — 1 vCPU/1GB/20GB NVMe", "~$5.16/mo — 1 vCPU/2GB/40GB (Starter)", 1),
        row("Countries", "40", "EU, US, Canada, APAC (~8)", 0),
        row("Crypto payments", "12+ coins", "No", 0),
        row("Windows VPS", "Native from $10.19/mo", "Extra-licensed", 0),
        row("Free backup", "Weekly", "Backup option paid", 0),
        row("Anti-DDoS", "Free L2-L4 standard", "Free always-on (strong)", 1),
    ],
    "sections": [
        {"h": "OVH's strengths", "html": "<p>Massive EU capacity, always-on anti-DDoS included, and cheap starter RAM. If you're Europe-centric and love big providers, OVH is a solid institution.</p>"},
        {"h": "Where is*hosting overtakes", "html": "<p>40-country map vs OVH's handful, crypto billing (BTC/USDT/XMR...), native Windows VPS, free weekly backups and English+Russian 24/7 support with free basic administration. For international or crypto-paying customers, OVH can't compete.</p>"},
    ],
    "verdict": "<p><b>Winner: is*hosting</b> for international projects and crypto payers. OVHcloud remains a strong EU-centric pick for raw capacity.</p>",
    "winner": "ishosting",
    "faqs": [
        ("Does OVH accept crypto?", "No — OVHcloud billing is card/PayPal/bank transfer."),
        ("Is is*hosting's DDoS protection free?", "Standard L2-L4 protection is free; advanced protection is a paid add-on."),
        ("Which is better outside Europe?", "is*hosting — 40 countries across 5 continents vs OVH's limited footprint."),
    ],
})

# ============ CLOUDWAYS VS IS*HOSTING (honest split) ============
pages.append({
    "path": "/hosting/cloudways-vs-ishosting/", "category": "hosting",
    "h1": "Cloudways vs is*hosting",
    "title": "Cloudways vs is*hosting (2026): Managed vs Self-Managed | StackPickr",
    "summary": "Managed convenience ($11/mo) vs global self-managed VPS ($5.94/mo). We pick the winner for each type of buyer.",
    "a": "cloudways", "b": "ishosting", "b_url": "https://ishosting.com/",
    "intro": "These two solve different problems: Cloudways removes server work entirely; is*hosting gives you a cheap, flexible raw VPS almost anywhere on Earth.",
    "tldr": "Running a website/store and hate servers? <b class='winner'>Cloudways</b>. Technical user who wants a cheap VPS in a specific country with crypto billing? is*hosting.",
    "table": [
        row("Entry price", "$11/mo", "$5.94/mo", 1),
        row("Model", "Fully managed", "Self-managed (free basic admin)", 0),
        row("Best for", "WordPress/Woo/apps owners", "Developers, bots, VPNs, geo projects", None),
        row("Locations", "65+ via DO/Vultr/Linode/AWS/GCP", "42 DCs, 40 countries", None),
        row("Backups", "Automated daily", "Free weekly", 0),
        row("Crypto payments", "No", "12+ coins", 1),
        row("Windows VPS", "No", "Yes", 1),
        row("Support", "24/7 managed hosting engineers", "24/7 + free basic administration", None),
    ],
    "sections": [
        {"h": "Pick Cloudways if…", "html": "<p>You run WordPress, WooCommerce or a business app and never want to SSH into a server. Cloudways handles patching, backups, staging, SSL and scaling; its support fixes hosting problems for you.</p>"},
        {"h": "Pick is*hosting if…", "html": "<p>You're technical and want control: a specific country's IP, Windows, Monero/USDT payments, or a box for trading terminals, VPNs and bots. At $5.94 with free backups, it's one of the most flexible raw VPS offers available.</p>"},
    ],
    "verdict": "<p>For our readers — mostly business and site owners — <b>Cloudways is the recommended default</b>: it removes the entire server-operations category of risk. is*hosting is our recommendation for technical users and international/crypto use cases.</p>",
    "winner": "cloudways",
    "faqs": [
        ("Which is cheaper?", "is*hosting ($5.94/mo entry) vs Cloudways ($11/mo entry) — but Cloudways includes full management."),
        ("Can both host WordPress?", "Cloudways has 1-click WordPress; on is*hosting you install it yourself on your VPS."),
        ("Do they accept crypto?", "is*hosting accepts 12+ cryptocurrencies; Cloudways does not."),
    ],
})

with open(os.path.join(HERE, "data", "cmp_hosting.json"), "w", encoding="utf-8") as f:
    json.dump(pages, f, ensure_ascii=False, indent=1)
print("hosting pages:", len(pages))
