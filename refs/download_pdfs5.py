# -*- coding: utf-8 -*-
"""第 5 轮：定向开放渠道下载（arXiv API / PNAS 直链 / Project Euclid /
Oxford 开放存档）。逐条记录真实状态，绝不伪报成功。"""
import io, json, os, re, time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(HERE, "pdf")
os.makedirs(PDF, exist_ok=True)

BIB = io.open(os.path.join(HERE, "refs.bib"), encoding="utf-8").read()
ENT = {}
for blk in BIB.split("@")[1:]:
    key = blk.split("{", 1)[1].split(",", 1)[0].strip()
    g = lambda f: (re.search(f + r"\s*=\s*\{(.*)\},?\s*$", blk, re.M).group(1)
                   if re.search(f + r"\s*=\s*\{(.*)\},?\s*$", blk, re.M) else "")
    ENT[key] = dict(title=g("title"), doi=g("doi"), year=g("year"))

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
log = []


def note(key, status, detail):
    log.append("%-22s %-10s %s" % (key, status, detail))
    print(log[-1])


def grab(key, url, dest, timeout=45):
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": UA,
            "Accept": "application/pdf,*/*",
            "Accept-Language": "en-US,en;q=0.9",
        })
        with urllib.request.urlopen(req, timeout=timeout) as r:
            ct = (r.headers.get("Content-Type") or "").lower()
            data = r.read()
        if len(data) < 4000 or "pdf" not in ct and not data[:5] == b"%PDF-":
            if data[:5] != b"%PDF-":
                return "blocked", "not a PDF (ct=%s, %d B)" % (ct[:30], len(data))
        io.open(dest, "wb").write(data)
        return "OK", "%d B  %s" % (len(data), url)
    except Exception as e:
        return "blocked", "%s: %s" % (type(e).__name__, str(e)[:60])


def norm(t):
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()


def sim(a, b):
    A, B = set(norm(a).split()), set(norm(b).split())
    return len(A & B) / max(1, len(A | B))


# ---------------- 1) arXiv ----------------
def arxiv_search(title):
    q = urllib.parse.urlencode({
        "search_query": 'ti:"%s"' % title, "start": 0, "max_results": 3})
    url = "http://export.arxiv.org/api/query?" + q
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={
                "User-Agent": UA}), timeout=40) as r:
            xml = r.read().decode("utf-8", "replace")
    except Exception as e:
        return None, "arxiv query failed: %s" % type(e).__name__
    ids = re.findall(r"<id>http://arxiv.org/abs/([^<]+)</id>", xml)
    tis = re.findall(r"<title>(.*?)</title>", xml, re.S)
    if not ids:
        return None, "no arXiv hit"
    best, bs = None, 0.0
    for i, t in zip(ids, tis[1:]):
        s = sim(title, re.sub(r"\s+", " ", t))
        if s > bs:
            best, bs = i, s
    if bs < 0.55:
        return None, "best arXiv similarity %.2f < 0.55" % bs
    return best, "arXiv:%s (sim=%.2f)" % (best, bs)


# ---------------- 2) 已知开放直链 ----------------
DIRECT = {
    # Tsiatis 1975 PNAS: all PNAS content older than 6 months is free
    "Tsiatis1975": "https://www.pnas.org/doi/pdf/10.1073/pnas.72.1.20",
    # Aalen 1978 Ann. Statist. -> Project Euclid (open)
    "Aalen1978": "https://projecteuclid.org/journals/annals-of-statistics/volume-6/"
                 "issue-4/Nonparametric-Inference-for-a-Family-of-Counting-Processes/"
                 "10.1214/aos/1176344247.pdf",
    # Lin & Ying 1995 AoAS -> Project Euclid (open)
    "Lin1995": "https://projecteuclid.org/journals/annals-of-statistics/volume-23/"
               "issue-3/10.1214/aos/1176324320.pdf",
    # Hardt & Mendler-Dunner, Statistical Science 2025 (arXiv preprint)
    "Hardt2025": "https://arxiv.org/pdf/2310.16608",
}

for key, meta in ENT.items():
    dest = os.path.join(PDF, key + ".pdf")
    if os.path.exists(dest) and os.path.getsize(dest) > 4000:
        note(key, "OK", "already present")
        continue
    t = meta["title"]
    got = False

    if key in DIRECT:
        st, det = grab(key, DIRECT[key], dest)
        note(key, st, "direct: " + det)
        got = (st == "OK")

    if not got:
        aid, det = arxiv_search(t)
        if aid:
            st, det2 = grab(key, "https://arxiv.org/pdf/" + aid, dest)
            note(key, st, det + " -> " + det2)
            got = (st == "OK")
        else:
            note(key, "blocked", "arXiv: " + det)
    time.sleep(1.0)

io.open(os.path.join(HERE, "download_manifest5.txt"), "w", encoding="utf-8").write(
    "\n".join(log))
ok = sum(1 for l in log if l.split()[1:2] == ["OK"])
print("\ndownloaded: %d / %d" % (ok, len(log)))
