# -*- coding: utf-8 -*-
"""a97 · 表 1 所需的补充统计量（全部来自原始数据，写入 paper_numbers.json）。"""
import io
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
R23 = os.path.normpath(os.path.join(HERE, "..", "review23"))
sys.path.insert(0, R23)
sys.path.insert(0, HERE)
import a83_params as A          # noqa: E402
import a84_nonparam as B        # noqa: E402

OUT = os.path.join(HERE, "results")
PN = os.path.join(OUT, "paper_numbers.json")


def main():
    y1, amax = 2025, 130
    d = A.load_kitchener()
    ymap = {str(d["wid"][i]): int(d["yv"][i]) for i in range(d["n"])}
    bk_fix = {}
    for w, bl in d["bk"].items():
        yi = ymap.get(w, 0)
        bk_fix[w] = [t for t in bl if t >= yi + 1] if yi > 1900 else list(bl)
    d_fix = dict(d)
    d_fix["bk"] = bk_fix

    lg = np.asarray([float(d["lg"][i]) for i in range(d["n"])])
    ok = np.array([ymap.get(str(d["wid"][i]), 0) > 1900 for i in range(d["n"])])
    yrs = np.asarray([ymap.get(str(d["wid"][i]), 0) for i in range(d["n"])])

    fl = A.kw_flat(d_fix, censor="last", y0=1997, y1=y1, amax=amax)
    EN, FN, EB, FB = B.state_tables(fl, amax)
    full = dict(n_unit=int(fl["n_unit"]), km=float(lg[ok].sum() / 1000.0),
                n_pipes=int(ok.sum()),
                FN=float(FN.sum()), FB=float(FB.sum()),
                EB=float(EB[1:amax + 1].sum()),
                EN=float(EN[1:amax + 1].sum()),
                install_min=int(yrs[ok].min()), install_max=int(yrs[ok].max()))

    d2 = B.subcohort(d_fix, 1997)
    fl2 = A.kw_flat(d2, censor="last", y0=1997, y1=y1, amax=28)
    w2 = np.asarray([str(d2["wid"][i]) for i in range(d2["n"])])
    yv2 = np.asarray([int(d2["yv"][i]) for i in range(d2["n"])])
    lg2 = np.asarray([float(d2["lg"][i]) for i in range(d2["n"])])
    mem = yrs >= 1997
    coh = dict(n_unit=int(fl2["n_unit"]), km=float(lg[mem].sum() / 1000.0),
               n_pipes=int(mem.sum()),
               FN=None, FB=None, EB=None,
               install_min=int(yrs[mem].min()), install_max=int(yrs[mem].max()))

    res = json.load(io.open(PN, encoding="utf-8"))
    res["table1"] = dict(full=full, cohort=coh, window=(1997, y1))
    io.open(PN, "w", encoding="utf-8").write(
        json.dumps(res, ensure_ascii=False, indent=1))
    print("full:", full)
    print("cohort:", coh)


if __name__ == "__main__":
    main()
