# -*- coding: utf-8 -*-
"""按 DOI 从 Crossref 拉取权威记录生成 .bib，并尝试下载开放获取全文。

纪律：refs.bib 中任何书目字段都不手写，全部取自 Crossref API 返回。
下载：优先 Unpaywall 报告的 OA PDF；失败则记录原因，不伪造。
"""
import io
import json
import os
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
PDFDIR = os.path.join(HERE, "pdf")
os.makedirs(PDFDIR, exist_ok=True)
MAILTO = "openresearch@example.org"
UA = "RefBuild/1.0 (mailto:%s)" % MAILTO

# (citekey, DOI, 备注：该文献在稿件中支撑的具体论断)
REFS = [
    ("Scheidegger2013", "10.1016/j.watres.2013.04.017",
     "被更换管道造成的数据缺失；failure model + replacement model 联合似然"),
    ("Scheidegger2015", "10.1016/j.watres.2015.06.027",
     "管道失效统计模型综述（统一视角）"),
    ("LeGat2013", "10.1080/1573062x.2013.783088",
     "LEYP2s：失效后修复概率 + Yule 因子；我们的 φ 是其退化特例"),
    ("LeGat2000", "10.1016/s1462-0758(00)00057-1",
     "用维修记录预测供水网络失效（早期非齐次 Poisson / 队列方法）"),
    ("Renaud2012", "10.2166/ws.2012.040",
     "破裂预测模型用于资产管理：从研究到实践"),
    ("Renaud2014", "10.2166/wpt.2014.032",
     "「寿命」不是管道更新策略的恰当概念"),
    ("LeGat2013b", "10.2166/ws.2013.089",
     "服务寿命与失效率是否相关（更换与失效的耦合）"),
    ("Kleiner2001", "10.1016/s1462-0758(01)00033-4",
     "水管理化统计模型综述（领域背景）"),
    ("Kleiner2002", "10.1061/(asce)1076-0342(2002)8:4(122)",
     "爆管的时间变化与趋势预测（领域背景）"),
    ("Rajani2012", "10.1080/1573062x.2011.630093",
     "爆管与温度协变量（领域背景）"),
    ("Alvisi2010", "10.1080/10286600802224064",
     "两种概率型爆管模型的比较（领域背景）"),
    ("Winkler2018", "10.1080/15732479.2018.1443145",
     "boosted decision trees 爆管建模（领域背景）"),
    ("Ouellet2018", "10.1080/1573062x.2018.1455883",
     "在排水管道劣化建模中考虑已更换管（与本文同一问题、不同介质）"),
    ("Cox1972", "10.1111/j.2517-6161.1972.tb00899.x",
     "比例风险回归（方法背景）"),
    ("Mantel1959", "10.1093/jnci/22.4.719",
     "分层率比估计（本文 φ̂ 的估计量）"),
    ("Aalen1978", "10.1214/aos/1176344247",
     "计数过程非参数推断（Nelson–Aalen 的理论基础）"),
    ("Nelson1969", "10.1080/00224065.1969.11980344",
     "不完全失效数据的危险率作图（Nelson–Aalen 估计）"),
    ("Prentice1981", "10.1093/biomet/68.2.373",
     "多变量失效时间数据的回归分析（复发事件的 marginal/conditional 框架）"),
    ("Andersen1993", "10.1007/978-1-4612-4348-9",
     "基于计数过程的统计模型（方法背景）"),
    ("Kalbfleisch2002", "10.1002/9781118032985",
     "失效时间数据的统计分析（删失/截断教科书）"),
    ("KleinMoeschberger2003", "10.1007/b97377",
     "删失与截断数据的生存分析（左截断处理）"),
    ("Slud1983", "10.1093/biomet/70.3.643",
     "相依竞争风险与边缘生存曲线不可识别（信息性删失的定性后果已知）"),
    ("Zheng1995", "10.1093/biomet/82.1.127",
     "基于 copula 的相依竞争风险边缘生存估计"),
    ("Tsiatis1975", "10.1073/pnas.72.1.20",
     "竞争风险的不可识别性（部分识别的思想源头）"),
    ("Crowder1994", "10.2307/1403768",
     "竞争风险中的可识别性危机"),
    ("Scharfstein1999", "10.1080/01621459.1999.10473862",
     "非可忽略退出的半参数非响应模型（敏感性分析范式）"),
    ("Wang2001", "10.1198/016214501753209031",
     "带信息性删失的复发事件数据分析"),
    ("Lin1995", "10.1214/aos/1176324320",
     "加性—乘性危险模型的半参数分析"),
    ("Bartlett2014", "10.1093/biostatistics/kxu023",
     "缺失非随机时完整病例分析的效率改进；明确用于审计既往研究的偏差量级"),
    ("Manski2003", "10.1007/b97478",
     "部分识别（bounding）范式"),
    ("Tamer2010", "10.1146/annurev.economics.050708.143401",
     "计量经济学中的部分识别综述"),
    ("Hardt2025", "10.1214/25-sts986",
     "Performative prediction（政策—数据反馈回路已被命名）"),
    ("Drent2020", "10.1016/j.orl.2020.10.005",
     "删失寿命学习：贝叶斯年龄更换（单机视角的近邻工作）"),
    ("BarlowProschan1965", "10.1137/1.9781611971194",
     "可靠性数学理论（年龄更换教科书公式）"),
]


def get_json(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def texesc(s):
    s = str(s)
    for a, b in (("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"),
                 ("_", r"\_"), ("{", r"\{"), ("}", r"\}"), ("~", r"\textasciitilde{}"),
                 ("^", r"\textasciicircum{}")):
        s = s.replace(a, b)
    return s


def year_of(it):
    for k in ("published-print", "published-online", "issued"):
        v = it.get(k, {}).get("date-parts")
        if v and v[0] and v[0][0]:
            return int(v[0][0])
    return None


def build_bib(records):
    out = []
    for key, it, note in records:
        typ = it.get("type", "article")
        if typ in ("book", "monograph"):
            kind = "book"
        elif typ in ("book-chapter",):
            kind = "incollection"
        else:
            kind = "article"
        au = []
        for a in (it.get("author") or []):
            fam = (a.get("family") or "").strip()
            gvn = (a.get("given") or "").strip()
            au.append("%s, %s" % (fam, gvn) if fam else gvn)
        lines = ["@%s{%s," % (kind, key)]
        if au:
            lines.append("  author    = {%s}," % " and ".join(texesc(x) for x in au))
        t = (it.get("title") or [""])[0]
        lines.append("  title     = {%s}," % texesc(" ".join(t.split())))
        ct = (it.get("container-title") or [""])[0]
        if ct:
            lines.append("  journal   = {%s}," % texesc(" ".join(ct.split())))
        y = year_of(it)
        if y:
            lines.append("  year      = {%d}," % y)
        if it.get("volume"):
            lines.append("  volume    = {%s}," % texesc(it["volume"]))
        if it.get("issue"):
            lines.append("  number    = {%s}," % texesc(it["issue"]))
        if it.get("page"):
            lines.append("  pages     = {%s}," % texesc(str(it["page"]).replace("-", "--")))
        if it.get("publisher"):
            lines.append("  publisher = {%s}," % texesc(it["publisher"]))
        lines.append("  doi       = {%s}," % it.get("DOI", ""))
        lines.append("  note      = {%s}," % texesc(note))
        lines.append("}")
        out.append("\n".join(lines))
    return "\n\n".join(out) + "\n"


def try_download(doi, key):
    """Unpaywall → OA PDF；返回 (状态, 文件名或原因)。"""
    try:
        u = get_json("https://api.unpaywall.org/v2/%s?email=%s" % (doi, MAILTO))
    except Exception as e:
        return ("unpaywall-fail", str(e))
    best = None
    for loc in (u.get("oa_locations") or []):
        url = loc.get("url_for_pdf") or loc.get("url")
        if not url:
            continue
        if (loc.get("url_for_pdf") and best is None) or (
                loc.get("host_type") == "publisher"):
            best = url
        if best is None:
            best = url
    if not best:
        return ("no-oa", "no open-access location recorded")
    fn = os.path.join(PDFDIR, key + ".pdf")
    try:
        req = urllib.request.Request(best, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/122.0 Safari/537.36"})
        with urllib.request.urlopen(req, timeout=90) as r:
            data = r.read()
        if len(data) < 5000 or data[:4] != b"%PDF":
            return ("not-pdf", "downloaded %d bytes, not a PDF" % len(data))
        with open(fn, "wb") as f:
            f.write(data)
        return ("ok", os.path.basename(fn) + " (%d bytes) %s" % (len(data), best))
    except Exception as e:
        return ("download-fail", "%s | %s" % (type(e).__name__, e))


def main():
    records = []
    manifest = []
    for key, doi, note in REFS:
        try:
            d = get_json("https://api.crossref.org/works/"
                         + urllib.parse.quote(doi) + "?mailto=" + MAILTO)
            it = d["message"]
        except Exception as e:
            manifest.append((key, doi, "crossref-fail", str(e)))
            print("!! %s crossref fail %s" % (key, e))
            time.sleep(1.0)
            continue
        records.append((key, it, note))
        manifest.append((key, doi, "crossref-ok",
                         "%s | %s %s(%s):%s | %s" % (
                             " ".join((it.get("title") or [""])[0].split())[:70],
                             " ".join((it.get("container-title") or [""])[0].split())[:35],
                             year_of(it), it.get("volume") or "-",
                             it.get("page") or "-", it.get("DOI"))))
        time.sleep(0.3)

    bib = build_bib(records)
    io.open(os.path.join(HERE, "refs.bib"), "w", encoding="utf-8").write(bib)

    dl = []
    for key, doi, st, msg in manifest:
        if st != "crossref-ok":
            dl.append((key, doi, st, msg))
            continue
        s, m = try_download(doi, key)
        dl.append((key, doi, s, m))
        print("%-24s %-16s %s" % (key, s, str(m)[:110]))
        time.sleep(0.4)

    with io.open(os.path.join(HERE, "download_manifest.txt"), "w",
                 encoding="utf-8") as f:
        f.write("%-24s %-34s %-16s %s\n" % ("citekey", "doi", "pdf_status", "detail"))
        for r in dl:
            f.write("%-24s %-34s %-16s %s\n" % r)
    io.open(os.path.join(HERE, "download_manifest.json"), "w",
            encoding="utf-8").write(json.dumps(
                [dict(key=k, doi=d, status=s, detail=str(m)) for k, d, s, m in dl],
                ensure_ascii=False, indent=1))
    nok = sum(1 for r in dl if r[2] == "ok")
    print("\n[bib] %d entries -> refs.bib ; [pdf] %d/%d downloaded"
          % (len(records), nok, len(dl)))


if __name__ == "__main__":
    main()
