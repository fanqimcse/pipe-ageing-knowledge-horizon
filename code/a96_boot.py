# -*- coding: utf-8 -*-
"""a96 · γ 标定的聚类 bootstrap（按管重抽样）

点估计：匹配修复后子队列的**聚合** B 态暴露保留率
        Σ_a w(a) S_I(a;γ) = R̄,   w(a) ∝ EB_c(a)
重抽样：以管（WATMAINID）为聚类单元有放回重抽样，重算面板与 R̄，重新解 γ。
"""
import io
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
R23 = os.path.normpath(os.path.join(HERE, "..", "review23"))
sys.path.insert(0, R23)
sys.path.insert(0, HERE)
import a83_params as A          # noqa: E402
import a84_nonparam as B        # noqa: E402
from a95_si import SI           # noqa: E402

OUT = os.path.join(HERE, "results")
LOG = []


def P(s=""):
    print(s)
    LOG.append(str(s))


def build(d, y1=2025, amax=28, ymin=1997):
    d2 = B.subcohort(d, ymin)
    fl_o = A.kw_flat(d2, censor="last", y0=ymin, y1=y1, amax=amax)
    fl_c = A.kw_flat(d2, censor="none", y0=ymin, y1=y1, amax=amax)
    EN, FN, EB, FB = B.state_tables(fl_o, amax)
    ENc, FNc, EBc, FBc = B.state_tables(fl_c, amax)
    return EB[1:amax + 1].astype(float), EBc[1:amax + 1].astype(float)


def solve_gamma(beta, lam, EB, EBc, agg, aw, lo=1e-6, hi=3.0, it=60):
    w = EBc / max(EBc.sum(), 1e-12)
    for _ in range(it):
        mid = 0.5 * (lo + hi)
        o = SI(beta, lam, mid, aw)
        if float(np.dot(w, o.SI)) > agg:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def main():
    y1, amax, ymin = 2025, 28, 1997
    aw = np.arange(1, amax + 1).astype(float)
    d = A.load_kitchener()
    ymap = {str(d["wid"][i]): int(d["yv"][i]) for i in range(d["n"])}
    bk_fix = {}
    for w_, bl in d["bk"].items():
        yi = ymap.get(w_, 0)
        bk_fix[w_] = [t for t in bl if t >= yi + 1] if yi > 1900 else list(bl)
    d_fix = dict(d)
    d_fix["bk"] = bk_fix

    EB, EBc = build(d_fix)
    agg = float(EB.sum() / max(EBc.sum(), 1e-12))
    Lam28 = 0.00388          # 由 a94 给出：Λ(28)=0.00388
    P("聚合保留率 R̄ = %.4f；Λ(28)=%.5f" % (agg, Lam28))

    res = dict(agg=agg, Lam28=Lam28, rows=[])
    rng = np.random.default_rng(20261020)
    n = d_fix["n"]
    wid = np.asarray([str(d_fix["wid"][i]) for i in range(n)])
    yv = np.asarray([int(d_fix["yv"][i]) for i in range(n)])
    lg = np.asarray([float(d_fix["lg"][i]) for i in range(n)])

    for beta in (2.0, 2.907):
        lam = Lam28 * beta / (28.0 ** beta)
        g0 = solve_gamma(beta, lam, EB, EBc, agg, aw)
        gs = []
        for _ in range(60):
            idx = rng.integers(0, n, n)
            db = dict(d_fix)
            db["wid"] = wid[idx]
            db["yv"] = yv[idx]
            db["lg"] = lg[idx]
            try:
                EBo, EBco = build(db)
            except Exception:
                continue
            if EBco.sum() <= 0:
                continue
            a_ = float(EBo.sum() / max(EBco.sum(), 1e-12))
            if not np.isfinite(a_) or a_ >= 1.0:
                gs.append(0.0)
                continue
            gs.append(solve_gamma(beta, lam, EBo, EBco, a_, aw, it=40))
        gs = np.asarray(gs, dtype=float)
        q = {str(k): float(np.percentile(gs, k)) for k in (2.5, 50, 97.5)} \
            if gs.size else {}
        # 视界 CI（把 γ 的 CI 端点映射到 H）
        hc = {}
        if q:
            ages_f = np.arange(0.5, 300.001, 0.5)
            for k in ("2.5", "97.5"):
                hc[k] = float(SI(beta, lam, q[k], ages_f).horizon(0.5, 300.0))
        P("  β=%5.3f  γ̂=%.4f  bootstrap 95%%CI [%.4f, %.4f] (R=%d)  "
          "H(0.5) ∈ [%.1f, %.1f]"
          % (beta, g0, q.get("2.5", float("nan")), q.get("97.5", float("nan")),
             gs.size, hc.get("97.5", float("nan")), hc.get("2.5", float("nan"))))
        res["rows"].append(dict(beta=float(beta), lam=float(lam), gam=float(g0),
                                boot=q, R=int(gs.size), H05_ci=hc))

    with io.open(os.path.join(OUT, "a96_boot.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    with io.open(os.path.join(OUT, "a96_log.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(LOG))
    P("[written] a96_boot.json")


if __name__ == "__main__":
    main()
