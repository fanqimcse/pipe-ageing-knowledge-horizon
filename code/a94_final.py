# -*- coding: utf-8 -*-
"""a94 · 论文数字的单一来源（R24 → Water Research 稿件）

纪律：稿件正文中出现的每一个数字都必须来自本脚本写出的
results/paper_numbers.json；图与表由该文件生成，正文不手写数字。

内容：
  P1 理论核验（命题 A/B/B′ 与 T2 均匀界）
  P2 数据质量发现 #3 的普查与 φ̂ 冲击测试
  P3 完整史子队列：首次失效信息曲线、B 态暴露保留曲线、γ 标定(bootstrap CI)
  P4 耗竭方向复核
  P5 两世界分歧与视界外部分识别
  P6 T4 哨兵随机延迟设计的功效带
  P7 导出 CSV 供绘图
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
from a85_combine import mh_ratio          # noqa: E402
from a89_horizon import irls_poisson      # noqa: E402


def fit_beta(Ev, Yv, a_lo, a_hi):
    """Poisson log-rate: log mu = c + beta*log a (a in [a_lo,a_hi])."""
    aw = np.arange(a_lo, a_hi + 1)
    E = np.asarray(Ev)[a_lo:a_hi + 1].astype(float)
    Y = np.asarray(Yv)[a_lo:a_hi + 1].astype(float)
    ok = E > 0
    x = np.log(aw[ok].astype(float))
    X = np.column_stack([np.ones(x.size), x])
    off = np.log(E[ok])
    th, se = irls_poisson(X, Y[ok], off)
    return dict(c=float(th[0]), beta=float(th[1]), se_c=float(se[0]),
                se=float(se[1]), n_ev=float(Y.sum()))

from a95_si import SI                     # noqa: E402

OUT = os.path.join(HERE, "results")
LOG = []


def P(s=""):
    print(s)
    LOG.append(str(s))


# ----------------------------------------------------------------------
def horizon(o, kappa, amax):
    """H(κ) = sup{a : inf_{u≤a} S_I(u) ≥ κ}，上限 amax（未达到返回 amax）。"""
    s = o.SI
    run = np.minimum.accumulate(s)
    ok = run >= kappa
    if not np.any(ok):
        return 0.0
    idx = int(np.max(np.nonzero(ok)[0]))
    a = o.ages
    if idx >= a.size - 1:
        return float(amax)
    r0, r1 = run[idx], run[idx + 1]
    if r1 < r0 - 1e-15:
        t = (r0 - kappa) / max(r0 - r1, 1e-300)
        return float(min(a[idx] + t * (a[idx + 1] - a[idx]), amax))
    return float(min(a[idx], amax))


# ======================================================================
def part1_theory():
    P("=" * 76)
    P("P1 · 理论核验（命题 A / B / B′ 与 T2 均匀界）")
    P("=" * 76)
    ages = np.arange(0.5, 200.001, 0.25)
    amax = 200.0
    maxSI, minSI = -np.inf, np.inf
    dpos = dneg = 0
    fd_err = 0.0
    da_pos = da_tot = 0
    for beta in (1.5, 2.0, 2.5, 3.0):
        lam = 40.0 * beta / (100.0 ** beta)
        for gam in (0.0, 0.002, 0.01, 0.05, 0.2, 0.5):
            o = SI(beta, lam, gam, ages)
            s = o.SI
            assert np.all(np.isfinite(s)), (beta, gam)
            maxSI = max(maxSI, float(np.max(s)))
            minSI = min(minSI, float(np.min(s)))
            d = o.dSI
            dpos += int(np.sum(d > 1e-14))
            dneg += int(np.sum(d < -1e-14))
            if gam > 0:
                eps = gam * 1e-4
                o2 = SI(beta, lam, gam + eps, ages)
                fd = (o2.SI - s) / eps
                m = np.abs(d) > 1e-6
                if np.any(m):
                    fd_err = max(fd_err, float(np.max(
                        np.abs(fd[m] - d[m]) / np.abs(d[m]))))
            dd = np.diff(s)
            da_pos += int(np.sum(dd > 1e-12))
            da_tot += dd.size
    P("  命题 A（S_I ≤ 1）：max S_I = %.12f ；min S_I = %.6f" % (maxSI, minSI))
    P("  命题 B（∂S_I/∂γ ≤ 0）：∂/∂γ>0 的点 %d ；<0 的点 %d" % (dpos, dneg))
    P("  命题 B 解析↔有限差：最大相对误差 = %.3e" % fd_err)
    P("  （非命题，诚实报告）dS_I/da > 0 的点 = %d / %d" % (da_pos, da_tot))
    okA = maxSI <= 1.0 + 1e-9
    okB = (dpos == 0) and (fd_err < 1e-3)
    P("  ⇒ 命题 A %s ；命题 B %s" % ("通过" if okA else "未通过",
                                     "通过" if okB else "未通过"))

    # 命题 B′：H(κ;γ) 对 γ 非增
    gams = [0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
    viol = tot = 0
    rows = []
    for beta in (1.5, 2.0, 2.5, 2.907):
        r = []
        for gam in gams:
            lam = 40.0 * beta / (100.0 ** beta)
            o = SI(beta, lam, gam, ages)
            r.append(horizon(o, 0.5, amax))
        for i in range(len(r) - 1):
            tot += 1
            if r[i + 1] > r[i] + 1e-9:
                viol += 1
        rows.append((beta, r))
    P("")
    P("  命题 B′（H(0.5;γ) 对 γ 非增；未达到 200 岁者按 200 右删）：")
    P("    β      " + "".join("%8.3f" % g for g in gams))
    for beta, r in rows:
        P("    %-6.3f " % beta + "".join("%8.1f" % v for v in r))
    P("    违反 = %d / %d" % (viol, tot))
    okBp = (viol == 0)
    P("  ⇒ 命题 B′ %s" % ("通过" if okBp else "未通过"))

    # T2 均匀界
    P("")
    P("  T2 均匀界 |D| ≤ |φ−1|·max(1, 1/φ)：")
    ages2 = np.arange(0.5, 120.001, 0.5)
    worst, best, n = -np.inf, 0.0, 0
    for beta in (1.5, 2.0, 2.5):
        for lam in (1e-5, 1e-4, 1e-3):
            for r0 in (0.005, 0.02, 0.05):
                for s in (1.0, 2.0, 5.0, 20.0):
                    for phi in (0.5, 0.8, 1.5, 3.0, 8.0):
                        n += 1
                        bnd = abs(phi - 1.0) * max(1.0 / phi, 1.0)
                        gam = r0 * (s - 1.0)
                        o = SI(beta, lam, gam, ages2)
                        La = lam * np.power(ages2, beta) / beta
                        F = 1.0 - np.exp(-La)
                        SN = np.exp(-La) * np.exp(-r0 * ages2)
                        SB = F * o.SI * SN * np.exp(-gam * ages2)
                        p = SB / np.maximum(SN + SB, 1e-300)
                        D = (phi - 1.0) * (p - F) / (1.0 + (phi - 1.0) * F)
                        m = np.isfinite(D)
                        worst = max(worst, float(np.max(np.abs(D[m]) - bnd)))
                        best = max(best, float(np.max(np.abs(D[m])) / bnd))
    P("    %d 组合：max(|D| − 界) = %.4e（应 ≤ 0）；max |D|/界 = %.4f"
      % (n, worst, best))
    okT2 = worst <= 1e-9
    P("  ⇒ T2 均匀界 %s" % ("通过" if okT2 else "未通过"))
    return dict(propA=dict(maxSI=float(maxSI), minSI=float(minSI), ok=bool(okA)),
                propB=dict(d_pos=dpos, d_neg=dneg, fd_err=float(fd_err),
                           ok=bool(okB)),
                da_nonmono=dict(n=da_pos, tot=da_tot),
                propBp=dict(gammas=gams,
                            rows=[dict(beta=b, H=[float(x) for x in r])
                                  for b, r in rows],
                            viol=viol, tot=tot, ok=bool(okBp)),
                t2=dict(n=n, worst=float(worst), ratio=float(best),
                        ok=bool(okT2)))


# ======================================================================
def part2_data(d, d_fix, y1, bk_fix, ymap, lmap):
    P("")
    P("=" * 76)
    P("P2 · 数据质量发现 #3 与 φ̂ 冲击测试")
    P("=" * 76)
    tot_ev = sum(len(v) for v in d["bk"].values())
    n_poll = sum(1 for w, bl in d["bk"].items()
                 if ymap.get(w, 0) > 1900
                 and len([t for t in bl if t >= ymap[w] + 1]) < len(bl))
    n_ev_drop = tot_ev - sum(len(v) for v in bk_fix.values())
    len_poll = sum(lmap.get(w, 0.0) for w, bl in d["bk"].items()
                   if ymap.get(w, 0) > 1900
                   and len([t for t in bl if t >= ymap[w] + 1]) < len(bl))
    P("  受污染管 %d / %d（%.1f%%）；删除安装前事件 %d / %d（%.1f%%）；"
      "涉及 %.1f km" % (n_poll, len(d["bk"]), 100.0 * n_poll / len(d["bk"]),
                        n_ev_drop, tot_ev, 100.0 * n_ev_drop / tot_ev,
                        len_poll / 1000.0))
    # 负年龄分布（图 2 数据）
    neg = []
    for w, bl in d["bk"].items():
        yi = ymap.get(w, 0)
        if yi <= 1900:
            continue
        for t in bl:
            if t < yi + 1:
                neg.append(yi + 1 - t)
    neg = np.asarray(neg, dtype=int)
    P("  被删记录的「安装前年数」分布：n=%d，中位=%d，最大=%d"
      % (neg.size, int(np.median(neg)) if neg.size else 0,
         int(neg.max()) if neg.size else 0))
    # φ̂ 前后
    phis = {}
    for tag, dd in (("before", d), ("after", d_fix)):
        fl = A.kw_flat(dd, censor="last", y0=1997, y1=y1, amax=130)
        EN, FN, EB, FB = B.state_tables(fl, 130)
        phi, se = mh_ratio(EN, FN, EB, FB)
        phis[tag] = dict(phi=float(phi), se_log=float(se),
                         lo=float(math.exp(math.log(phi) - 1.96 * se)),
                         hi=float(math.exp(math.log(phi) + 1.96 * se)),
                         nFN=float(FN.sum()), nFB=float(FB.sum()),
                         EB=float(EB[1:131].sum()))
        P("  φ̂ %-6s = %.4f [%.4f, %.4f]  FN=%.0f FB=%.0f EB=%.0f m·yr"
          % (tag, phi, phis[tag]["lo"], phis[tag]["hi"], FN.sum(), FB.sum(),
             EB[1:131].sum()))
    kept = phis["after"]["lo"] > 1.0
    P("  ⇒ 修复后 95%%CI 下界 %.4f %s 1 ⇒ 符号判据%s"
      % (phis["after"]["lo"], ">" if kept else "≤",
         "保住" if kept else "失效"))
    return dict(census=dict(n_poll=int(n_poll), n_ever=int(len(d["bk"])),
                            n_ev_drop=int(n_ev_drop), n_ev_total=int(tot_ev),
                            len_poll_km=float(len_poll / 1000.0)),
                neg_years=dict(n=int(neg.size),
                               median=int(np.median(neg)) if neg.size else 0,
                               max=int(neg.max()) if neg.size else 0,
                               hist={str(k): int(v) for k, v in
                                     zip(*np.unique(np.clip(neg, 1, 40),
                                                    return_counts=True))}
                               if neg.size else {}),
                phi=phis, sign_kept=bool(kept))


# ======================================================================
def _tables(d2, y1, amax, censor_o="last", censor_c="none"):
    fl_o = A.kw_flat(d2, censor=censor_o, y0=1997, y1=y1, amax=amax)
    fl_c = A.kw_flat(d2, censor=censor_c, y0=1997, y1=y1, amax=amax)
    EN, FN, EB, FB = B.state_tables(fl_o, amax)
    ENc, FNc, EBc, FBc = B.state_tables(fl_c, amax)
    return EN, FN, EB, FB, ENc, FNc, EBc, FBc, fl_o["n_unit"]


def part3_cohort(d_fix, y1, amax=28):
    P("")
    P("=" * 76)
    P("P3 · 完整史子队列（安装 ≥1997，修复后）")
    P("=" * 76)
    d2 = B.subcohort(d_fix, 1997)
    EN, FN, EB, FB, ENc, FNc, EBc, FBc, n_unit = _tables(d2, y1, amax)
    aw = np.arange(1, amax + 1)
    P("  单元 %d ｜ FN=%.0f FB=%.0f ｜ FNc=%.0f FBc=%.0f"
      % (n_unit, FN.sum(), FB.sum(), FNc.sum(), FBc.sum()))
    winfo = FN[1:] / max(FN[1:].sum(), 1e-12)
    cum = np.cumsum(winfo)
    H80 = int(aw[min(int(np.searchsorted(cum, 0.8)), aw.size - 1)])
    last_ev = int(max([a for a in aw if FN[a] > 0] or [0]))
    P("  首次失效信息 80%% ≤ %d 岁；有事件最大年龄 %d 岁" % (H80, last_ev))
    EBv = EB[1:amax + 1].astype(float)
    EBcv = EBc[1:amax + 1].astype(float)
    ret = np.where(EBcv > 0, EBv / np.maximum(EBcv, 1e-12), np.nan)
    agg = float(EBv.sum() / max(EBcv.sum(), 1e-12))
    P("  B 态暴露保留率（聚合）= %.4f" % agg)
    P("  逐龄保留（1–14 岁）：" + " ".join("%.2f" % r for r in ret[:14]))

    # γ 标定：聚合匹配 Σ w(a) S_I(a;γ) = agg ；β 场景
    Lam28 = -math.log1p(-float(FN.sum()) / max(n_unit, 1))
    P("  Λ(28) = %.5f" % Lam28)
    wgt = EBcv / max(EBcv.sum(), 1e-12)
    scen = []
    for beta in (1.5, 2.0, 2.5, 2.907):
        lam = Lam28 * beta / (28.0 ** beta)
        lo_, hi_ = 1e-5, 3.0
        for _ in range(80):
            mid = 0.5 * (lo_ + hi_)
            o = SI(beta, lam, mid, aw.astype(float))
            if float(np.dot(wgt, o.SI)) > agg:
                lo_ = mid
            else:
                hi_ = mid
        g = 0.5 * (lo_ + hi_)
        ages_f = np.arange(0.5, 250.001, 0.5)
        o2 = SI(beta, lam, g, ages_f)
        h05 = horizon(o2, 0.5, 250.0)
        h02 = horizon(o2, 0.2, 250.0)
        om = SI(beta, lam, g, aw.astype(float))
        mod = om.SI
        obs = ret.copy()
        m = np.isfinite(obs) & np.isfinite(mod)
        mae = float(np.mean(np.abs(obs[m] - mod[m]))) if np.any(m) else float("nan")
        wmae = float(np.sum(wgt[m] * np.abs(obs[m] - mod[m])) / np.sum(wgt[m])) \
            if np.any(m) else float("nan")
        scen.append(dict(beta=float(beta), lam=float(lam), gam=float(g),
                         H05=float(h05), H02=float(h02),
                         shape_mae=mae, shape_wmae=wmae,
                         model_by_age=[float(x) for x in mod],
                         SI_at=[float(SI(beta, lam, g, np.array([a])).SI[0])
                                for a in (5, 10, 15, 20, 28)]))
        P("    β=%5.3f ⇒ γ̂=%.4f /yr  H(0.5)=%6.1f  H(0.2)=%6.1f  "
          "逐龄 MAE=%.3f（加权 %.3f）" % (beta, g, h05, h02, mae, wmae))

    # bootstrap CI（按管重抽样）
    R = 200
    rng = np.random.default_rng(20261020)
    wid = [str(d2["wid"][i]) for i in range(d2["n"])]
    gams_b = []
    for _ in range(R):
        idx = rng.integers(0, d2["n"], d2["n"])
        db = dict(d2)
        db["wid"] = [wid[i] for i in idx]
        db["yv"] = [int(d2["yv"][i]) for i in idx]
        db["lg"] = [float(d2["lg"][i]) for i in idx]
        db["n"] = d2["n"]
        try:
            ENo, FNo, EBo, FBo, ENc2, FNc2, EBc2, FBc2, nu = _tables(db, y1, amax)
        except Exception:
            continue
        EBo = EBo[1:amax + 1].astype(float)
        EBc2 = EBc2[1:amax + 1].astype(float)
        if EBc2.sum() <= 0:
            continue
        a_ = float(EBo.sum() / max(EBc2.sum(), 1e-12))
        if not np.isfinite(a_) or a_ >= 1.0:
            gams_b.append(0.0)
            continue
        beta = 2.0
        lam = Lam28 * beta / (28.0 ** beta)
        w2 = EBc2 / max(EBc2.sum(), 1e-12)
        lo_, hi_ = 1e-5, 3.0
        for _ in range(60):
            mid = 0.5 * (lo_ + hi_)
            o = SI(beta, lam, mid, aw.astype(float))
            if float(np.dot(w2, o.SI)) > a_:
                lo_ = mid
            else:
                hi_ = mid
        gams_b.append(0.5 * (lo_ + hi_))
    gams_b = np.asarray(gams_b, dtype=float)
    if gams_b.size:
        q = {str(k): float(np.percentile(gams_b, k)) for k in (2.5, 50, 97.5)}
        P("  聚类 bootstrap（R=%d，β=2 场景）：γ̂ 中位 %.4f，"
          "95%%CI [%.4f, %.4f]" % (gams_b.size, q["50"], q["2.5"], q["97.5"]))
    else:
        q = {}
    return dict(n_unit=int(n_unit), FN=float(FN.sum()), FB=float(FB.sum()),
                FNc=float(FNc.sum()), FBc=float(FBc.sum()),
                H80=int(H80), last_ev=last_ev,
                retention_agg=agg,
                retention_by_age=[None if np.isnan(r) else float(r)
                                  for r in ret],
                EBc_by_age=[float(x) for x in EBcv],
                gamma_scenarios=scen,
                gamma_boot=dict(R=int(gams_b.size), **q) if q else {},
                Lam28=float(Lam28), amax=amax), d2


# ======================================================================
def part5_worlds(d_fix, d2, y1, amax=28):
    P("")
    P("=" * 76)
    P("P5 · 两世界分歧（全存量 vs 完整史）")
    P("=" * 76)
    fl_full = A.kw_flat(d_fix, censor="last", y0=1997, y1=y1, amax=130)
    ENf, FNf, EBf, FBf = B.state_tables(fl_full, 130)
    bF = fit_beta(ENf + EBf, FNf + FBf, 2, 130)
    EN, FN, EB, FB, ENc, FNc, EBc, FBc, nu = _tables(d2, y1, amax)
    bY = fit_beta(ENc + EBc, FNc + FBc, 2, amax)
    P("  世界 F（全存量，左截断）：β=%.3f±%.3f  事件 %.0f"
      % (bF["beta"], bF["se"], bF["n_ev"]))
    P("  世界 Y（完整史子队列）：β=%.3f±%.3f  事件 %.0f"
      % (bY["beta"], bY["se"], bY["n_ev"]))
    rows = []
    for a in (30, 40, 50, 57, 70, 90):
        r = math.exp(bF["c"] - bY["c"]) * a ** (bF["beta"] - bY["beta"])
        rows.append(dict(age=a, ratio=float(r),
                         hF=float(math.exp(bF["c"]) * a ** bF["beta"]),
                         hY=float(math.exp(bY["c"]) * a ** bY["beta"])))
        P("    a=%3d 岁：h_F/h_Y = %8.1f ×" % (a, r))
    return dict(bF=bF, bY=bY, ratios=rows)


# ======================================================================
def part6_t4(d_fix, d, y1, bk_fix, ymap, lmap, bF, bY, phi_new, amax=28):
    P("")
    P("=" * 76)
    P("P6 · T4 哨兵随机延迟设计：两世界功效带")
    P("=" * 76)
    ea = []
    for w, bl in bk_fix.items():
        if w in d["gone"] and bl:
            cands = [v for v in (ymap.get(w, 0), d["ayear"].get(w, 0))
                     if v > 1900]
            if not cands:
                continue
            yi = min(cands)
            if yi <= min(bl):
                ea.append((max(bl) - yi, lmap.get(w, 60.0)))
    P("  可靠定年的失效触发退出 n = %d" % len(ea))

    def m_world(bw, rho, Delta):
        m = 0.0
        ex = 0.0
        for ai, Li in ea:
            dd = min(float(Delta), max(130.0 - ai, 0.0))
            if dd <= 0:
                continue
            a0, a1 = ai, ai + dd
            integ = math.exp(bw["c"]) * (a1 ** (bw["beta"] + 1)
                                         - a0 ** (bw["beta"] + 1)) \
                / (bw["beta"] + 1)
            m += phi_new * Li * integ
            ex += Li * dd
        return rho * m, rho * ex

    rows = []
    for rho in (0.05, 0.10, 0.20):
        for Delta in (5.0, 10.0, 15.0):
            mF, exF = m_world(bF, rho, Delta)
            mY, exY = m_world(bY, rho, Delta)
            rows.append(dict(rho=rho, Delta=Delta, mF=float(mF), mY=float(mY),
                             exposed_kmyr=float(exF),
                             precF=float(1.0 / math.sqrt(mF)) if mF > 0 else None,
                             precY=float(1.0 / math.sqrt(mY)) if mY > 0 else None))
            P("  ρ=%.2f Δ=%2.0f ⇒ m_F=%6.1f  m_Y=%6.2f  精度 %.1f%%"
              % (rho, Delta, mF, mY,
                 100.0 / math.sqrt(mF) if mF > 0 else float("nan")))
    return dict(n_exit=len(ea), phi=float(phi_new), rows=rows)


# ======================================================================
def main():
    res = {"probe": "a94_paper_numbers",
           "system": "Kitchener (ON, Canada) water distribution network"}
    y1 = 2025
    d = A.load_kitchener()
    ymap = {str(d["wid"][i]): int(d["yv"][i]) for i in range(d["n"])}
    lmap = {str(d["wid"][i]): float(d["lg"][i]) for i in range(d["n"])}
    bk_fix = {}
    for w, bl in d["bk"].items():
        yi = ymap.get(w, 0)
        bk_fix[w] = [t for t in bl if t >= yi + 1] if yi > 1900 else list(bl)
    d_fix = dict(d)
    d_fix["bk"] = bk_fix

    res["theory"] = part1_theory()
    res["datafix"] = part2_data(d, d_fix, y1, bk_fix, ymap, lmap)
    res["cohort"], d2 = part3_cohort(d_fix, y1)

    # P4 耗竭方向
    P("")
    P("=" * 76)
    P("P4 · 耗竭方向复核")
    P("=" * 76)
    amax = 28
    EN, FN, EB, FB, ENc, FNc, EBc, FBc, nu = _tables(d2, y1, amax)
    pobs = EB[1:amax + 1] / np.maximum(EN[1:amax + 1] + EB[1:amax + 1], 1e-12)
    pcf = EBc[1:amax + 1] / np.maximum(ENc[1:amax + 1] + EBc[1:amax + 1], 1e-12)
    inner = [i for i in range(amax) if abs(pcf[i] - pobs[i]) > 1e-9
             and np.isfinite(pobs[i])]
    nneg = int(sum(1 for i in inner if pobs[i] < pcf[i]))
    P("  非退化年龄 %d 个，其中 p_obs < p_cf 的 %d 个（%.0f%%）"
      % (len(inner), nneg, 100.0 * nneg / max(len(inner), 1)))
    res["exhaust_dir"] = dict(n_inner=len(inner), n_neg=nneg)

    res["worlds"] = part5_worlds(d_fix, d2, y1)
    res["t4"] = part6_t4(d_fix, d, y1, bk_fix, ymap, lmap,
                         res["worlds"]["bF"], res["worlds"]["bY"],
                         res["datafix"]["phi"]["after"]["phi"])

    # 存量年龄分布（图用）
    ages_stock = np.asarray([max(y1 - ymap.get(str(d["wid"][i]), 0), 0)
                             for i in range(d["n"])], dtype=float)
    lg = np.asarray([float(d["lg"][i]) for i in range(d["n"])])
    m = (ymap.get(str(d["wid"][0]), 0) > 0) or True
    ok = np.array([ymap.get(str(d["wid"][i]), 0) > 1900 for i in range(d["n"])])
    aw = ages_stock[ok]
    lw = lg[ok]
    order = np.argsort(aw)
    aw_s, lw_s = aw[order], lw[order]
    cw = np.cumsum(lw_s) / max(lw_s.sum(), 1e-12)
    qs = {str(q): float(aw_s[int(np.searchsorted(cw, q / 100.0))])
          for q in (25, 50, 75, 90)}
    dark = float(lw[aw > 28].sum() / max(lw.sum(), 1e-12))
    P("")
    P("  存量年龄 P25/50/75/90 = %.0f/%.0f/%.0f/%.0f 岁；暗区（>28 岁）占比 %.1f%%"
      % (qs["25"], qs["50"], qs["75"], qs["90"], 100 * dark))
    res["stock"] = dict(quantiles=qs, dark_fraction=float(dark),
                        n_pipes=int(ok.sum()),
                        total_km=float(lw.sum() / 1000.0))

    with io.open(os.path.join(OUT, "paper_numbers.json"), "w",
                 encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    with io.open(os.path.join(OUT, "a94_log.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(LOG))
    P("")
    P("[written] results/paper_numbers.json + results/a94_log.txt")


if __name__ == "__main__":
    main()
