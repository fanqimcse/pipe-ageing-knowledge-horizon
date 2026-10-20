# -*- coding: utf-8 -*-
"""第二轮下载：OpenAlex best_oa_location → Unpaywall oa_locations → 已知仓储直链。

结果写入 download_manifest2.txt（逐条状态），不伪造任何「已下载」。
"""
import io
import json
import os
import time
import urllib.parse

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
PDFDIR = os.path.join(HERE, "pdf")
os.makedirs(PDFDIR, exist_ok=True)
MAILTO = "openresearch@example.org"
HDR = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/pdf,text/html;q=0.9,*/*;q=0.8",
}

DOIS = {}
for ln in io.open(os.path.join(HERE, "refs.bib"), encoding="utf-8"):
    ln = ln.strip()
    if ln.startswith("doi"):
        continue
for blk in io.open(os.path.join(HERE, "refs.bib"), encoding="utf-8").read().split("@"):
    if not blk.strip():
        continue
    key = blk.split("{", 1)[1].split(",", 1)[0].strip()
    for ln in blk.splitlines():
        if ln.strip().startswith("doi"):
            DOIS[key] = ln.split("{", 1)[1].rstrip("},").strip()
            break

# 已知可直连的开放获取副本（人工核对过的仓储链接）
MANUAL = {
    "Scheidegger2013": "https://www.dora.lib4ri.ch/eawag/dload/eawag%3A7286/PDF2/"
                       "Scheidegger-2013-Extension_of_pipe_failure_models-(accepted_version).pdf",
    "Tsiatis1975": "https://www.pnas.org/doi/pdf/10.1073/pnas.72.1.20",
    "Aalen1978": "https://projecteuclid.org/journals/annals-of-statistics/volume-6/"
                 "issue-4/Nonparametric-Inference-for-a-Family-of-Counting-Processes/"
                 "10.1214/aos/1176344247.pdf",
    "Mantel1959": "https://academic.oup.com/jnci/article-pdf/22/4/719/1105986/22-4-719.pdf",
}


def openalex(doi):
    try:
        r = requests.get("https://api.openalex.org/works/doi:" + doi,
                         params={"mailto": MAILTO}, headers=HDR, timeout=45)
        if r.status_code != 200:
            return []
        j = r.json()
        urls = []
        for k in ("best_oa_location", "primary_location"):
            v = j.get(k) or {}
            if v.get("pdf_url"):
                urls.append(v["pdf_url"])
        for v in (j.get("locations") or []):
            if v.get("pdf_url"):
                urls.append(v["pdf_url"])
            if v.get("landing_page_url"):
                urls.append(v["landing_page_url"])
        return urls
    except Exception:
        return []


def unpaywall(doi):
    try:
        r = requests.get("https://api.unpaywall.org/v2/%s" % doi,
                         params={"email": MAILTO}, headers=HDR, timeout=45)
        if r.status_code != 200:
            return []
        j = r.json()
        urls = []
        for v in (j.get("oa_locations") or []):
            for k in ("url_for_pdf", "url"):
                if v.get(k):
                    urls.append(v[k])
        return urls
    except Exception:
        return []


def grab(url, fn):
    try:
        r = requests.get(url, headers=HDR, timeout=90, allow_redirects=True,
                         stream=False)
    except Exception as e:
        return False, "%s: %s" % (type(e).__name__, str(e)[:90])
    if r.status_code != 200:
        return False, "HTTP %d" % r.status_code
    d = r.content
    if len(d) < 8000 or d[:4] != b"%PDF":
        return False, "not a PDF (%d bytes, %s)" % (len(d), d[:12])
    with open(fn, "wb") as f:
        f.write(d)
    return True, "%d bytes" % len(d)


def main():
    rows = []
    for key, doi in DOIS.items():
        fn = os.path.join(PDFDIR, key + ".pdf")
        if os.path.exists(fn) and os.path.getsize(fn) > 8000:
            rows.append((key, doi, "ok", "cached %d bytes"
                         % os.path.getsize(fn)))
            print("%-24s ok (cached)" % key)
            continue
        cands = MANUAL.get(key, None)
        urls = ([cands] if cands else []) + openalex(doi) + unpaywall(doi)
        seen = set()
        got = None
        last = "no candidate url"
        for u in urls:
            if not u or u in seen:
                continue
            seen.add(u)
            ok, msg = grab(u, fn)
            if ok:
                got = (u, msg)
                break
            last = "%s -> %s" % (u[:70], msg)
        if got:
            rows.append((key, doi, "ok", "%s | %s" % (got[1], got[0][:80])))
            print("%-24s ok   %s" % (key, got[1]))
        else:
            rows.append((key, doi, "paywalled-or-blocked", last))
            print("%-24s FAIL %s" % (key, last[:100]))
        time.sleep(0.3)
    with io.open(os.path.join(HERE, "download_manifest2.txt"), "w",
                 encoding="utf-8") as f:
        f.write("%-24s %-36s %-22s %s\n" % ("citekey", "doi", "status", "detail"))
        for r in rows:
            f.write("%-24s %-36s %-22s %s\n" % r)
    io.open(os.path.join(HERE, "download_manifest2.json"), "w",
            encoding="utf-8").write(json.dumps(
                [dict(key=k, doi=d, status=s, detail=m) for k, d, s, m in rows],
                ensure_ascii=False, indent=1))
    print("\n[pdf] %d/%d" % (sum(1 for r in rows if r[2] == "ok"), len(rows)))


if __name__ == "__main__":
    main()
