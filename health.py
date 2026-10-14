"""StackPickr health check: script-only, no LLM. Deterministic.

Prints one line: OK ... | WARN ... | ALRM ...
Empty stdout = silent success (watchdog pattern for cron no_agent jobs).
Prints non-empty only when something is off, so cron output stays clean.

Checks (all real HTTP / filesystem, nothing assumed):
  1. / = 200, /hosting/ = 200, /sitemap.xml = 200
  2. sitemap URL count >= 40
  3. pages in site/ with cta-box but NO affiliate link = monetisation leak (must be 0)
  4. pages with cta-box: total >= 30
Exit: always 0 for a cron watcher; failures are reported in text, not exit code,
so that a broken site does not spam blocked_config-style noise.
"""
import glob, json, os, re, sys, urllib.request

SITE = "https://stackpickr.vercel.app"
ROOT = r"C:\Users\Admin\fabrika\cmpsite"  # ponytail: script lives in hermes/scripts, project path is fixed
UA = {"User-Agent": "Mozilla/5.0"}
AFF = ("ishosting.com/affiliate", "kjuzv", "axavl", "bednari", "admitad",
       "cloudways.com/en/?id=")  # id= query string is the Cloudways affiliate marker
MIN_PAGES = 40
MIN_CTA_PAGES = 30


def get(url, timeout=25):
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "ignore")
    except Exception as ex:
        return 0, str(ex)


def main():
    probs = []

    # 1. key pages reachable
    for path in ("/", "/hosting/", "/hosting/cloudways/", "/sitemap.xml"):
        st, _ = get(SITE + path)
        if st != 200:
            probs.append(f"{path} -> {st or 'unreachable'}")

    # 2. sitemap size
    st, sm = get(SITE + "/sitemap.xml")
    urls = len(re.findall(r"<loc>", sm)) if st == 200 else 0
    if urls < MIN_PAGES:
        probs.append(f"sitemap {urls} urls (< {MIN_PAGES})")

    # 3/4. monetisation coverage on the built site
    cta = leak = 0
    for f in glob.glob(os.path.join(ROOT, "site", "**", "index.html"), recursive=True):
        try:
            h = open(f, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        if "cta-box" not in h:
            continue
        cta += 1
        if not any(a in h for a in AFF):
            leak += 1
    if leak:
        probs.append(f"{leak} pages with CTA but NO affiliate link (money leak)")
    if cta < MIN_CTA_PAGES:
        probs.append(f"only {cta} pages with CTA (< {MIN_CTA_PAGES})")

    if probs:
        print("ALRM " + "; ".join(probs))
    else:
        print(f"OK site:200 sitemap:{urls} cta:{cta} leaks:0")


if __name__ == "__main__":
    main()
