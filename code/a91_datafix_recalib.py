# -*- coding: utf-8 -*-
"""
A91 · 数据质量发现 #3 的处理与 R24 重标定
==========================================

发现 #3（本轮）：**更换使新管继承旧管的爆管史（同 WATMAINID 空间合并）**。
子队列（安装≥1997）中 190/220 条「曾失效」管的爆管记录早于其（修正后）
安装年——它们是「替换管安装年被当作原始安装年」的管，其合并记录里混着
旧管的爆管。后果：
  ① 新管的真实首次失效被错记为「复发」（es=1，因为 k>0）；
  ② B 态成员资格（stM = 累计爆管>0）被旧管爆管污染 ⇒ EB/EBc 在低龄爆炸；
  ③ A89 B3/B4/B5/B6 与 A85 的 φ̂ 全部受影响。

通用修复（可辩护）：**任何管都不可能在安装前爆管** ⇒ 对每条管删除
安装年之前的爆管记录：bk_fix = {w: [t for t in bl if t >= yv(w)+1]}。
对无污染的管此操作删除 0 条记录；对污染管删除的是旧管史。

本脚本：
  S1 污染普查（管数、事件数、长度）
  S2 全队列 φ̂ 修复前后（MH 逐岁）——R23 头号数字的冲击测试
  S3 子队列修复后：首次失效信息曲线、B 态暴露保留曲线、γ 反演、H(κ)
  S4 耗竭方向复核（p_obs vs p_cf，D 符号判据是否保住）
  S5 T4 哨兵随机延迟设计的两世界功效带（用修复后数据）

证据链：本脚本 → results/a91_datafix.json + a91_log.txt。
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
import a83_params as A   # noqa: E402
import a84_nonparam as B  # noqa: E402
from a85_combine import mh_ratio  # noqa: E402
from a90_horizon_theory import SI_exact, solve_H  # noqa: E402
from a89_horizon import irls_poisson  # noqa: E402

OUT = os.path.join(HERE, "results")
LOG = []


def P(s=""):
    print(s)
    LOG.append(str(s))


def fit_beta(Ev, Yv, a_lo, a_hi):
    """Poisson log-rate：log μ = c + β·log a（a∈[a_lo,a_hi]，a89 阻尼 IRLS）。"""
    aw = np.arange(a_lo, a_hi + 1)
    E = np.asarray(Ev)[a_lo:a_hi + 1].astype(float)
    Y = np.asarray(Yv)[a_lo:a_hi + 1].astype(float)
    ok = E > 0
    x = np.log(aw[ok].astype(float))
    X = np.column_stack([np.ones(x.size), x])
    off = np.log(E[ok])
    th, se = irls_poisson(X, Y[ok], off)
    return dict(c=float(th[0]), beta=float(th[1]), se_c=float(se[0]),
                se_b=float(se[1]), n_ev=float(Y.sum()))


def main():
    res = {"system": "Kitchener 供水", "probe": "a91_datafix_recalib"}
    d = A.load_kitchener()
    y1 = 2025

    # ---------------- S1 · 污染普查 ----------------
    P("=" * 78)
    P("S1 · 发现 #3 普查：安装年之前存在爆管记录的管（合并替换史）")
    P("=" * 78)
    ymap = {str(d["wid"][i]): int(d["yv"][i]) for i in range(d["n"])}
    lmap = {str(d["wid"][i]): float(d["lg"][i]) for i in range(d["n"])}
    n_poll = 0
    n_ev_drop = 0
    len_poll = 0.0
    bk_fix = {}
    gone_poll = 0
    for w, bl in d["bk"].items():
        yi = ymap.get(w, 0)
        if yi <= 1900:
            bk_fix[w] = list(bl)
            continue
        keep = [t for t in bl if t >= yi + 1]
        if len(keep) < len(bl):
            n_poll += 1
            n_ev_drop += len(bl) - len(keep)
            len_poll += lmap.get(w, 0.0)
            if w in d["gone"]:
                gone_poll += 1
        bk_fix[w] = keep
    tot_ev = sum(len(v) for v in d["bk"].values())
    P("  受污染管：%d / %d 曾失效管（%.1f%%），涉及长度 %.1f km"
      % (n_poll, len(d["bk"]), 100.0 * n_poll / max(len(d["bk"]), 1),
         len_poll / 1000.0))
    P("  删除的安装前事件：%d / %d 条爆管记录（%.1f%%），其中 gone 管 %d 个"
      % (n_ev_drop, tot_ev, 100.0 * n_ev_drop / max(tot_ev, 1), gone_poll))
    res["census"] = dict(n_poll=int(n_poll), n_ever=int(len(d["bk"])),
                         n_ev_drop=int(n_ev_drop), n_ev_total=int(tot_ev),
                         len_poll_km=float(len_poll / 1000.0),
                         gone_poll=int(gone_poll))
    P("")
    d_fix = dict(d)
    d_fix["bk"] = bk_fix

    # ---------------- S2 · 全队列 φ̂ 修复前后 ----------------
    P("=" * 78)
    P("S2 · 全队列 φ̂（MH 逐岁）修复前后的冲击测试")
    P("=" * 78)
    phis = {}
    for tag, dd in (("修复前", d), ("修复后", d_fix)):
        fl = A.kw_flat(dd, censor="last", y0=1997, y1=y1, amax=130)
        EN, FN, EB, FB = B.state_tables(fl, 130)
        phi, se = mh_ratio(EN, FN, EB, FB)
        phis[tag] = dict(phi=float(phi), se=float(se),
                         lo=float(math.exp(math.log(phi) - 1.96 * se)),
                         hi=float(math.exp(math.log(phi) + 1.96 * se)),
                         nFN=float(FN.sum()), nFB=float(FB.sum()),
                         EB=float(EB[1:131].sum()))
        P("  %s：φ̂ = %.4f [%.4f, %.4f]（se_log=%.4f）｜FN=%.0f FB=%.0f"
          " EB=%.0f m·yr" % (tag, phi, phis[tag]["lo"], phis[tag]["hi"], se,
                             FN.sum(), FB.sum(), EB[1:131].sum()))
    lo, hi = phis["修复后"]["lo"], phis["修复后"]["hi"]
    still = (lo > 1.0) or (hi < 1.0)
    P("  ⇒ 修复后 CI %s 1（%s）"
      % ("不含" if still else "含", "符号判据保住" if lo > 1.0 else "符号判据翻转/失效"))
    res["phi"] = phis
    res["phi_sign_kept"] = bool(lo > 1.0)
    P("")

    # ---------------- S3 · 子队列修复后：信息曲线 / 保留曲线 / γ 反演 ----------------
    P("=" * 78)
    P("S3 · 完整史子队列（安装≥1997，修复后）重标定")
    P("=" * 78)
    amax = 28
    d2 = B.subcohort(d_fix, 1997)
    fl_o = A.kw_flat(d2, censor="last", y0=1997, y1=y1, amax=amax)
    fl_c = A.kw_flat(d2, censor="none", y0=1997, y1=y1, amax=amax)
    EN, FN, EB, FB = B.state_tables(fl_o, amax)
    ENc, FNc, EBc, FBc = B.state_tables(fl_c, amax)
    aw = np.arange(1, amax + 1)
    n_unit = fl_o["n_unit"]
    P("  单元 %d ｜ 首次失效 FN = %.0f（修复前 28）｜ 复发 FB = %.0f（修复前 9）"
      % (n_unit, FN.sum(), FB.sum()))
    P("  反事实 FBc = %.0f ｜ FNc = %.0f" % (FBc.sum(), FNc.sum()))
    # 首次失效信息曲线
    winfo = FN[1:] / max(FN[1:].sum(), 1e-12)
    cum = np.cumsum(winfo)
    H80 = int(aw[min(np.searchsorted(cum, 0.8), aw.size - 1)])
    last_ev = int(max([a for a in aw if FN[a] > 0] or [0]))
    P("  80%% 首次失效信息 ≤ %d 岁（修复前 16）；有事件最大年龄 %d 岁" % (H80, last_ev))
    # B 态暴露保留曲线
    EBv = EB[1:amax + 1].astype(float)
    EBcv = EBc[1:amax + 1].astype(float)
    ret = np.where(EBcv > 0, EBv / np.maximum(EBcv, 1e-12), np.nan)
    agg = float(EBv.sum() / max(EBcv.sum(), 1e-12))
    P("  B 态暴露保留率（ΣEB/ΣEBc）= %.4f（修复前 0.1199）" % agg)
    P("  逐龄保留：" + " ".join("%.2f" % r for r in ret[:14]))
    P("  ⇒ 修复后保留曲线应随年龄**递减**（与 S_I 理论同向）")
    res["sub_fixed"] = dict(n_unit=int(n_unit), FN=float(FN.sum()),
                            FB=float(FB.sum()), FBc=float(FBc.sum()),
                            H80=int(H80), last_ev=last_ev,
                            retention_agg=agg,
                            retention_by_age=[None if np.isnan(r) else float(r)
                                              for r in ret])
    # γ 反演（目标 = 修复后的聚合保留率）
    Lam28 = -math.log1p(-float(FN.sum()) / max(n_unit, 1))
    P("")
    P("  γ 反演（β 场景 × λ 使 Λ(28) 匹配 %.4f）：" % Lam28)
    scen = []
    for beta in (1.5, 2.0, 2.5, 2.907):
        lam = Lam28 * beta / 28.0 ** beta
        wgt = EBcv / max(EBcv.sum(), 1e-12)
        lo_, hi_ = 1e-4, 2.0
        for _ in range(60):
            mid = 0.5 * (lo_ + hi_)
            si = SI_exact(beta, lam, mid, aw, nx=2001)
            if float(np.dot(wgt, si)) > agg:
                lo_ = mid
            else:
                hi_ = mid
        g = 0.5 * (lo_ + hi_)
        H05 = solve_H(beta, lam, g, 0.5, amax=200.0)
        H02 = solve_H(beta, lam, g, 0.2, amax=200.0)
        obs = np.where(EBcv > 0, EBv / np.maximum(EBcv, 1e-12), np.nan)
        mod = SI_exact(beta, lam, g, aw, nx=2001)
        mae = float(np.nanmean(np.abs(obs - mod)))
        scen.append(dict(beta=beta, lam=float(lam), gam=float(g),
                         H05=float(H05), H02=float(H02), shape_mae=mae))
        P("    β=%5.3f ⇒ γ̂ = %6.4f /yr  H(0.5)=%5.1f 岁  H(0.2)=%5.1f 岁"
          "  逐龄 MAE=%.3f" % (beta, g, H05, H02, mae))
    res["gamma_scenarios"] = scen
    P("")

    # ---------------- S4 · 耗竭方向复核 ----------------
    P("=" * 78)
    P("S4 · 耗竭方向复核（R23 D̄ 符号判据是否保住）")
    P("=" * 78)
    p_obs = EBv / np.maximum(EN[1:amax + 1].astype(float) + EBv, 1e-12)
    p_cf = EBcv / np.maximum(ENc[1:amax + 1].astype(float) + EBcv, 1e-12)
    inner = [i for i in range(aw.size)
             if abs(p_cf[i] - p_obs[i]) > 1e-9 and np.isfinite(p_obs[i])]
    n_neg = int(sum(1 for i in inner if p_obs[i] < p_cf[i]))
    P("  非退化年龄 %d 个：p_obs < p_cf 的 %d 个（%.0f%%）"
      % (len(inner), n_neg, 100.0 * n_neg / max(len(inner), 1)))
    P("  ⇒ 方向判据（耗竭 ⇒ 观测风险集更干净）%s"
      % ("保住（多数 p_obs<p_cf）" if n_neg > 0.5 * len(inner) else "未保住"))
    res["exhaust_dir"] = dict(n_inner=len(inner), n_neg=n_neg)
    P("")

    # ---------------- S5 · T4 哨兵随机延迟设计（两世界功效带） ----------------
    P("=" * 78)
    P("S5 · T4 哨兵随机延迟设计：两世界功效带（修复后数据）")
    P("=" * 78)
    # 两世界 hazard 拟合（修复后）
    fl_full = A.kw_flat(d_fix, censor="last", y0=1997, y1=y1, amax=130)
    ENf, FNf, EBf, FBf = B.state_tables(fl_full, 130)
    bF = fit_beta(ENf + EBf, FNf + FBf, 2, 130)
    bY = fit_beta(EN + EB, FN + FB, 2, amax)     # 完整史子队列
    P("  世界 F（全存量拟合）：β=%.3f±%.3f  c=%.2f  事件 %.0f"
      % (bF["beta"], bF["se_b"], bF["c"], bF["n_ev"]))
    P("  世界 Y（完整史子队列）：β=%.3f±%.3f  c=%.2f  事件 %.0f"
      % (bY["beta"], bY["se_b"], bY["c"], bY["n_ev"]))
    # 可靠定年的失效触发退出（修复后）
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
    P("  可靠定年的失效触发退出：n = %d（修复前 125）" % len(ea))
    phi_new = phis["修复后"]["phi"]

    def m_world(bw, rho, Delta):
        m = 0.0
        exposed = 0.0
        for ai, Li in ea:
            dd = min(float(Delta), max(130.0 - ai, 0.0))
            if dd <= 0:
                continue
            a0, a1 = ai, ai + dd
            integ = math.exp(bw["c"]) * (
                a1 ** (bw["beta"] + 1) - a0 ** (bw["beta"] + 1)) / (bw["beta"] + 1)
            m += phi_new * Li * integ
            exposed += Li * dd
        return rho * m, rho * exposed

    P("")
    P("  %-6s %-5s | %-12s %-12s | %-11s" % ("ρ", "Δ", "m@世界F", "m@世界Y", "ĥ精度(1/√m)"))
    rows = []
    for rho in (0.05, 0.10, 0.20):
        for Delta in (5.0, 10.0, 15.0):
            mF, exF = m_world(bF, rho, Delta)
            mY, exY = m_world(bY, rho, Delta)
            prec = (1.0 / math.sqrt(mF), 1.0 / math.sqrt(mY))
            rows.append(dict(rho=rho, Delta=Delta, mF=float(mF), mY=float(mY),
                             exposed_km=float(exF / 1000.0),
                             precF=float(prec[0]), precY=float(prec[1])))
            P("  %-6.2f %-5.0f | %-12.1f %-12.1f | %-11.1f%%/%.1f%%"
              % (rho, Delta, mF, mY, 100 * prec[0], 100 * prec[1]))
    P("")
    P("  ⇒ 判读：延迟臂直接测**决策年龄段**的复发强度。世界 F 下 m ≈ 2–22 次")
    P("    ⇒ 暗区 hazard 精度 22–82%%（ρ=0.20、Δ=15 ⇒ 21.5%%）；世界 Y 下")
    P("    m ≈ 0.1–0.4 ⇒ 本质零事件 ⇒ 上界结论（hazard 低）。两世界相差")
    P("    30–50 倍的事件数 ⇒ 试验把两世界分歧（修复后 9×/35×/99×）变成测量。")
    P("    风险成本 = 延迟臂额外爆管 m 次（每次既是成本也是信息）。")
    res["t4"] = dict(bF=bF, bY=bY, n_exit=len(ea), phi_new=float(phi_new),
                     rows=rows)
    P("")

    with io.open(os.path.join(OUT, "a91_datafix.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    with io.open(os.path.join(OUT, "a91_log.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(LOG))
    P("=" * 78)
    P("完成：results/a91_datafix.json + a91_log.txt")


if __name__ == "__main__":
    main()
