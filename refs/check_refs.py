# -*- coding: utf-8 -*-
"""用 Crossref REST API 逐条校验参考文献的真实元数据（作者/刊/年/卷/页/DOI）。

不手写任何 bibliographic 字段：全部取自 Crossref 返回的权威记录。
"""
import io
import os
import json
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
MAILTO = "openresearch@example.org"
UA = "WaterResearchManuscriptRefCheck/1.0 (mailto:%s)" % MAILTO

# key -> 用于 Crossref 检索的 bibliographic 字符串
QUERIES = [
    ("scheidegger2013", "Extension of pipe failure models to consider the absence of data from replaced pipes Scheidegger Water Research"),
    ("legat2014", "Extending the Yule process to model recurrent pipe failures in water supply networks Le Gat"),
    ("renaud2011", "Selective survival bias pipe failure model Renaud Le Gat Poulton"),
    ("kleiner2001", "Comprehensive review of structural deterioration of water mains statistical models Kleiner Rajani"),
    ("kleiner2002", "Forecasting variations and trends in water-main breaks Kleiner Rajani"),
    ("legat2000", "Using maintenance records to forecast failures in water networks Le Gat Eisenbeis"),
    ("rostum2000", "Statistical modelling of pipe failures in water networks Rostum"),
    ("alvisi2010", "Probabilistic pipe failure model water distribution network Alvisi Franchini"),
    ("winkler2018", "Pipe failure modelling water distribution networks review Winkler"),
    ("mailhot2000", "Calibration deterioration model water distribution system Mailhot"),
    ("cox1972", "Regression models and life tables Cox"),
    ("mantel1959", "Statistical aspects of the analysis of data from retrospective studies of disease Mantel Haenszel"),
    ("aalen1978", "Nonparametric inference for a family of counting processes Aalen"),
    ("nelson1969", "Hazard plotting for incomplete failure data Nelson"),
    ("slud1983", "Dependent competing risks and the exponential model Slud Rubinstein"),
    ("zheng1995", "Estimates of marginal survival for dependent competing risks based on an assumed copula Zheng Klein"),
    ("scharfstein1999", "Adjusting for nonignorable drop-out using semiparametric nonresponse models Scharfstein Rotnitzky Robins"),
    ("wang2001", "Analyzing recurrent event data with informative censoring Wang Qin Chiang"),
    ("tsiatis1975", "A nonidentifiability aspect of the problem of competing risks Tsiatis"),
    ("crowder1991", "On the identifiability crisis in competing risks analysis Crowder"),
    ("bartlett2014", "Improving upon the efficiency of complete case analysis when covariates are missing not at random Bartlett Carpenter Tilling Vansteelandt"),
    ("perdomo2020", "Performative prediction Perdomo Zrnic Mendler-Dunner Hardt"),
    ("drent2020", "Censored lifetime learning Drent Kapodistria Boxma"),
    ("manski2003", "Partial identification of probability distributions Manski"),
    ("tamer2010", "Partial identification in econometrics Tamer"),
    ("cook2007", "The statistical analysis of recurrent events Cook Lawless"),
    ("kleinschmidt", "Survival analysis techniques for censored and truncated data Klein Moeschberger"),
    ("kalbfleisch2002", "The statistical analysis of failure time data Kalbfleisch Prentice"),
    ("barlow1965", "Mathematical theory of reliability Barlow Proschan"),
    ("prentice1981", "On the regression analysis of multivariate failure time data Prentice Williams Peterson"),
    ("lin1994", "Semiparametric analysis of general additive-multiplicative hazard models Lin Ying"),
    ("andersen1993", "Statistical models based on counting processes Andersen Borgan Gill Keiding"),
    ("grigg2012", "Infrastructure finance reporting Grigg"),
    ("burningham2015", "Asset management water utility buried infrastructure burningham"),
    ("marlow2010", "Condition assessment strategies water pipelines Marlow"),
]


def fetch(q, rows=3):
    url = ("https://api.crossref.org/works?query.bibliographic="
           + urllib.parse.quote(q) + "&rows=%d&mailto=%s" % (rows, MAILTO))
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read().decode("utf-8"))


def shorten(item):
    au = []
    for a in (item.get("author") or [])[:4]:
        au.append(((a.get("family") or "") + ", " + (a.get("given") or ""))[:40])
    if len(item.get("author") or []) > 4:
        au.append("et al.")
    return dict(
        title=" ".join((item.get("title") or [""])[0].split())[:160],
        authors="; ".join(au),
        container=" ".join((item.get("container-title") or [""])[0].split())[:90],
        year=(item.get("issued", {}).get("date-parts") or [[None]])[0][0],
        volume=item.get("volume"),
        issue=item.get("issue"),
        page=item.get("page"),
        type=item.get("type"),
        doi=item.get("DOI"),
        score=round(float(item.get("score", 0.0)), 1),
    )


def main():
    out = {}
    lines = []
    for key, q in QUERIES:
        try:
            d = fetch(q)
        except Exception as e:
            lines.append("%-20s ERROR %s" % (key, e))
            out[key] = dict(error=str(e))
            time.sleep(1.0)
            continue
        items = d.get("message", {}).get("items", [])
        cands = [shorten(it) for it in items[:3]]
        out[key] = cands
        lines.append("### %s" % key)
        for c in cands:
            lines.append("   score=%-6s %s | %s | %s %s(%s):%s | doi=%s"
                         % (c["score"], c["authors"][:70], c["title"][:95],
                            c["container"][:45], c["year"], c["volume"] or "-",
                            c["page"] or "-", c["doi"]))
        lines.append("")
        time.sleep(0.4)
    io.open(os.path.join(HERE, "crossref_raw.json"), "w",
            encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
    io.open(os.path.join(HERE, "crossref_raw.txt"), "w",
            encoding="utf-8").write("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
