"""StackPickr evening report: script-only, no LLM. Deterministic.

Pulls only numbers this script can actually verify. Honesty rule: revenue is
reported as 0 unless we can see it — we have no ledger, so we check the
affiliate mailboxes for confirmation/sale notices and say so plainly.
"""
import json, os, re, subprocess, sys, urllib.request

ROOT = r"C:\Users\Admin\fabrika\cmpsite"
SITE = "https://stackpickr.vercel.app"
UA = {"User-Agent": "Mozilla/5.0"}


def http(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
            return r.status, r.read().decode("utf-8", "ignore")
    except Exception as ex:
        return 0, str(ex)[:60]


def count_cta_pages():
    n = 0
    for dirpath, _, files in os.walk(os.path.join(ROOT, "site")):
        for f in files:
            if f != "index.html":
                continue
            try:
                if "cta-box" in open(os.path.join(dirpath, f),
                                     encoding="utf-8", errors="ignore").read():
                    n += 1
            except OSError:
                pass
    return n


def himalaya_count(account, needles, lookback_days=7):
    """Count recent envelopes whose subject/from matches any needle."""
    try:
        p = subprocess.run(["himalaya", "envelope", "list", "--account", account, "--page-size", "60"],
                           capture_output=True, text=True, timeout=60)
        txt = p.stdout
    except Exception:
        return 0
    hits = 0
    for line in txt.splitlines():
        if any(n.lower() in line.lower() for n in needles):
            hits += 1
    return hits


def main():
    home_st, _ = http(SITE + "/")
    _, sm = http(SITE + "/sitemap.xml")
    sitemap_n = len(re.findall(r"<loc>", sm))

    idx_path = os.path.join(ROOT, ".gsc_indexed.json")
    indexed_n = 0
    if os.path.exists(idx_path):
        try:
            raw = json.load(open(idx_path, encoding="utf-8"))
            indexed_n = len([u for u in raw if isinstance(u, (str, dict))])
        except Exception:
            pass

    cta_n = count_cta_pages()

    # revenue signal: affiliate / payout notices in the two mailboxes that hold them
    cloud = himalaya_count("alex", ["cloudways", "payout", "affiliate"])
    ish = himalaya_count("keyt", ["ishosting", "payout", "commission"])

    # Adsterra balance via the tracker script if present, else unknown
    adsterra = "unknown"
    tracker = r"C:\Users\Admin\fabrika\modelsite\STATE.md"
    if os.path.exists(tracker):
        m = re.search(r"Adsterra[^\n]*?\$\s?([\d.]+)", open(tracker, encoding="utf-8").read())
        if m:
            adsterra = "$" + m.group(1)

    print(f"REPORT site:{home_st} sitemap:{sitemap_n} indexed:{indexed_n} cta:{cta_n} "
          f"adsterra:{adsterra} | mail_hits cloudways:{cloud} ishosting:{ish} "
          f"| revenue: $0 (no ledger; checking mail only)")


if __name__ == "__main__":
    main()
