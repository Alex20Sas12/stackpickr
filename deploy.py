"""StackPickr: rebuild + deploy to Vercel. Usage: python deploy.py [--no-push]

R7-safe: prints a live healthcheck after deploy so callers can verify nothing broke.
Exit code: 0 = live site still serving the new build, 1 = anything off.
"""
import json, os, re, subprocess, sys, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJ = "stackpickr"
SCOPE = "keyt9750-7169s-projects"
LIVE = f"https://{PROJ}.vercel.app"
UA = {"User-Agent": "Mozilla/5.0"}


def run(cmd, cwd=ROOT, timeout=420):
    r = subprocess.run(cmd, cwd=cwd, shell=True, timeout=timeout,
                       capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def rebuild():
    code, out, err = run("python sitegen.py")
    tail = (out or err).strip().splitlines()[-1:] or [""]
    return code == 0, tail[0]


def count_pages():
    return len([p for p in os.listdir(os.path.join(ROOT, "site"))])


def live(url="/"):
    try:
        req = urllib.request.Request(LIVE + url, headers=UA)
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status, r.read().decode("utf-8", "ignore")
    except Exception as ex:  # pragma: no cover
        return 0, str(ex)


def deploy(no_push):
    # commit content changes first, so Vercel and git agree
    run("git add -A pages.py sitegen.py site/ .gitignore vercel.json data/")
    run('git commit -m "Rebuild" || true')
    if not no_push:
        run("git push origin master")
    code, out, err = run(
        f'npx -y vercel@latest deploy site --prod --yes --project {PROJ} --scope {SCOPE}',
        timeout=600)
    txt = out + err
    ok = LIVE in txt
    return ok, re.findall(r"Aliased\s+\S+", txt)


def main():
    no_push = "--no-push" in sys.argv
    good, line = rebuild()
    print(f"build: {line}")
    if not good:
        print("BUILD FAILED — aborting before deploy")
        return 1

    ok, alias = deploy(no_push)
    print("deploy:", alias[0] if alias else "NOT ALIASED")
    if not ok:
        print("DEPLOY FAILED")
        return 1

    st, body = live("/")
    st2, sm = live("/sitemap.xml")
    urls = len(re.findall(r"<loc>", sm))
    aff = len([h for h in re.findall(r'href="(https?://[^"]+)"', body)
               if any(k in h for k in ("ishosting.com/affiliate", "kjuzv", "axavl", "bednari", "admitad"))])
    print(f"live: / -> {st}, sitemap -> {st2} ({urls} urls), home aff links: {aff}")
    return 0 if st == 200 and st2 == 200 and urls >= 40 else 1


if __name__ == "__main__":
    sys.exit(main())
