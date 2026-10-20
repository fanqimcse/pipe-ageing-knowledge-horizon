# -*- coding: utf-8 -*-
"""第三轮：试已知的开放副本直链（PMC / Project Euclid / arXiv / 仓储）。

只写入确认为 PDF（%PDF 头且 >8 KB）的文件；其余记为 blocked。
"""
import io
import json
import os

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(HERE, "pdf")
os.makedirs(PDF, exist_ok=True)
HDR = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                     "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}

CAND = {
    "Tsiatis1975": [
        "https://pmc.ncbi.nlm.nih.gov/articles/PMC432231/pdf/pnas00135-0020.pdf",
        "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC432231/pdf/pnas00135-0020.pdf",
        "https://www.pnas.org/doi/pdf/10.1073/pnas.72.1.20"],
    "Aalen1978": [
        "https://projecteuclid.org/journals/annals-of-statistics/volume-6/issue-4/"
        "Nonparametric-Inference-for-a-Family-of-Counting-Processes/"
        "10.1214/aos/1176344247.pdf"],
    "Lin1995": [
        "https://projecteuclid.org/journals/annals-of-statistics/volume-23/issue-5/"
        "Semiparametric-Analysis-of-General-Additive-Multiplicative-Hazard-Models-for/"
        "10.1214/aos/1176324320.pdf"],
    "Scheidegger2013": [
        "http://www.dora.lib4ri.ch/eawag/dload/eawag%3A7286/PDF2/"
        "Scheidegger-2013-Extension_of_pipe_failure_models-(accepted_version).pdf",
        "https://www.dora.lib4ri.ch/eawag/islandora/object/eawag%3A7286/datastream/PDF2/download"],
    "Hardt2025": [
        "https://projecteuclid.org/journals/statistical-science/volume-40/issue-3/"
        "Performative-Prediction--Past-and-Future/10.1214/25-STS986.pdf"],
    "Bartlett2014": [
        "https://europepmc.org/articles/PMC4052147?pdf=render",
        "https://academic.oup.com/biostatistics/article-pdf/15/4/719/17749099/kxu023.pdf"],
    "Wang2001": [
        "https://www.tandfonline.com/doi/pdf/10.1198/016214501753209031"],
    "Crowder1994": [
        "https://www.jstor.org/stable/pdf/1403768.pdf"],
    "Drent2020": [
        "https://pure.tue.nl/ws/portalfiles/portal/144738349/1_s2.0_S0167637720301678_main.pdf"],
    "Scheidegger2015": [
        "http://www.dora.lib4ri.ch/eawag/dload/eawag%3A8185/PDF2/"
        "Scheidegger-2015-Statistical_failure_models-(accepted_version).pdf"],
}


def main():
    rows = []
    for key, urls in CAND.items():
        fn = os.path.join(PDF, key + ".pdf")
        if os.path.exists(fn) and os.path.getsize(fn) > 8000:
            rows.append((key, "ok", "cached"))
            print("%-20s ok (cached)" % key)
            continue
        done = None
        last = "no url"
        for u in urls:
            try:
                r = requests.get(u, headers=HDR, timeout=70,
                                 allow_redirects=True)
            except Exception as e:
                last = "%s: %s" % (type(e).__name__, str(e)[:70])
                continue
            d = r.content
            if r.status_code == 200 and len(d) > 8000 and d[:4] == b"%PDF":
                with open(fn, "wb") as f:
                    f.write(d)
                done = "%d bytes | %s" % (len(d), u[:80])
                break
            last = "HTTP %d, %d bytes, type=%s" % (
                r.status_code, len(d), d[:8])
        if done:
            rows.append((key, "ok", done))
            print("%-20s ok   %s" % (key, done))
        else:
            rows.append((key, "blocked", last))
            print("%-20s FAIL %s" % (key, last[:100]))
    io.open(os.path.join(HERE, "download_manifest3.txt"), "w",
            encoding="utf-8").write(
        "\n".join("%-20s %-10s %s" % r for r in rows))
    print("\n[pdf] %d/%d" % (sum(1 for r in rows if r[1] == "ok"), len(rows)))


if __name__ == "__main__":
    main()
