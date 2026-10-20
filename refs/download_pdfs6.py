# -*- coding: utf-8 -*-
"""第 6 轮：修正 arXiv 查询串（标题含 ' : ( ) 会被 API 判 400）。
仅按 arXiv 检索，命中即下载 PDF。逐条记录真实状态。"""
import io, os, re, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(HERE, "pdf")
os.makedirs(PDF, exist_ok=True)
BIB = io.open(os.path.join(HERE, "refs.bib"), encoding="utf-8").read()

ENT = {}
for blk in BIB.split("@")[1:]:
    key = blk.split("{", 1)[1].split(",", 1)[0].strip()
    m = re.search(r"title\s*=\s*\{(.*)\},?\s*$", blk, re.M)
    ENT[key] = m.group(1) if m else ""

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
log = []


def note(k, st, d):
    log.append("%-22s %-9s %s" % (k, st, d))
    print(log[-1], flush=True)


def fetch(url, timeout=40):
    r = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(r, timeout=timeout) as f:
        return f.read()


def sanitize(t):
    """arXiv API rejects raw ' : ( ) — keep alphanumerics and spaces."""
    t = re.sub(r"[^\w\s\-]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def norm(t):
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).split()


def sim(a, b):
    A, B = set(norm(a)), set(norm(b))
    return len(A & B) / max(1, len(A | B))


STOP = set("a an the of on in for and with from to by is are as at via using "
           "based approach model models analysis".split())


def arxiv_hit(title):
    q = sanitize(title)
    words = [w for w in q.split() if w.lower() not in STOP][:8]
    query = " AND ".join("all:%s" % w for w in words)
    url = ("http://export.arxiv.org/api/query?"
           + urllib.parse.urlencode({"search_query": query,
                                     "start": 0, "max_results": 5}))
    xml = fetch(url).decode("utf-8", "replace")
    ids = re.findall(r"<id>http://arxiv.org/abs/([^<]+)</id>", xml)
    tis = re.findall(r"<title>(.*?)</title>", xml, re.S)[1:]
    best, bs = None, 0.0
    for i, t in zip(ids, tis):
        s = sim(title, re.sub(r"\s+", " ", t))
        if s > bs:
            best, bs = i, s
    return best, bs


for key, title in ENT.items():
    dest = os.path.join(PDF, key + ".pdf")
    if os.path.exists(dest) and os.path.getsize(dest) > 4000:
        note(key, "OK", "already present")
        continue
    try:
        aid, s = arxiv_hit(title)
    except Exception as e:
        note(key, "blocked", "arxiv query %s" % type(e).__name__)
        time.sleep(2.0)
        continue
    if aid is None or s < 0.50:
        note(key, "blocked", "no arXiv preprint (best sim=%.2f)" % s)
        time.sleep(2.0)
        continue
    try:
        data = fetch("https://arxiv.org/pdf/" + aid, timeout=60)
    except Exception as e:
        note(key, "blocked", "arXiv:%s dl %s" % (aid, type(e).__name__))
        time.sleep(2.0)
        continue
    if data[:5] != b"%PDF-":
        note(key, "blocked", "arXiv:%s not a PDF (%d B)" % (aid, len(data)))
    else:
        io.open(dest, "wb").write(data)
        note(key, "OK", "arXiv:%s  %d B  (sim=%.2f)" % (aid, len(data), s))
    time.sleep(2.0)

io.open(os.path.join(HERE, "download_manifest6.txt"), "w", encoding="utf-8").write(
    "\n".join(log))
ok = sum(1 for l in log if l.split()[1:2] == ["OK"])
print("\ndownloaded this round: %d" % ok)
print("total PDFs on disk: %d" % len([f for f in os.listdir(PDF)
                                      if f.endswith(".pdf")
                                      and os.path.getsize(os.path.join(PDF, f)) > 4000]))
