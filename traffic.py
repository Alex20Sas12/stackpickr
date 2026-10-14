"""StackPickr traffic: script-only, no LLM. Deterministic.

Grows indexation the two ways that actually work in 2026:
  1. GSC IndexNow queue (rate-limit 2 URLs/site/day — GSC quota is shared)
  2. IndexNow bulk push for any sitemap URL not yet known to be indexed
     (cheap, no quota problem, works from anywhere)

Prints one summary line. Exit 0 always — this is a daily growth job, not a
failure detector, and a hiccup should not spam the digest.
"""
import json, os, re, sys, urllib.request

ROOT = r"C:\Users\Admin\fabrika\cmpsite"
SITE = "https://stackpickr.vercel.app"
UA = {"User-Agent": "Mozilla/5.0"}
os.chdir(ROOT)  # gsc_index_queue.py reads/writes .gsc_indexed.json in cwd


def push_indexnow(urls):
    """Push a batch to IndexNow. Returns (http_status, ok_count_hint)."""
    if not urls:
        return 0, 0
    try:
        key = open("site/indexnow_key.txt", encoding="utf-8").read().strip()
        body = json.dumps({"host": "stackpickr.vercel.app", "key": key,
                           "urlList": urls}).encode()
        r = urllib.request.Request("https://api.indexnow.org/indexnow", data=body,
                                   headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(r, timeout=30) as resp:
            return resp.status, len(urls)
    except Exception as ex:
        return 0, str(ex)[:80]


def main():
    # sitemap (source of truth: what's published)
    try:
        with urllib.request.urlopen(urllib.request.Request(SITE + "/sitemap.xml", headers=UA), timeout=25) as r:
            sm = r.read().decode("utf-8", "ignore")
        published = re.findall(r"<loc>([^<]+)</loc>", sm)
    except Exception:
        # fall back to local build
        sm = open(os.path.join(ROOT, "site", "sitemap.xml"), encoding="utf-8").read()
        published = re.findall(r"<loc>([^<]+)</loc>", sm)

    # what we already know is indexed
    idx_path = os.path.join(ROOT, ".gsc_indexed.json")
    indexed = []
    if os.path.exists(idx_path):
        try:
            # entries are plain URL strings (list of str)
            raw = json.load(open(idx_path, encoding="utf-8"))
            indexed = [u if isinstance(u, str) else u.get("url")
                       for u in raw if isinstance(u, (str, dict))]
        except Exception:
            indexed = []
    unknown = [u for u in published if u not in indexed]

    gsc_out = "skip"
    try:
        # gsc_index_queue.py spawns its own Chrome CDP window; give it time.
        import subprocess
        p = subprocess.run([sys.executable, "gsc_index_queue.py"],
                           capture_output=True, text=True, timeout=420)
        gsc_out = f"exit{p.returncode} " + (p.stdout.strip().splitlines() or [""])[-1][:60]
    except Exception as ex:
        gsc_out = f"err {str(ex)[:50]}"

    st, info = push_indexnow(unknown[:25])
    print(f"OK sitemap:{len(published)} known_indexed:{len(indexed)} "
          f"new_pushed:{info if st == 200 else st} gsc:{gsc_out}")


if __name__ == "__main__":
    main()
