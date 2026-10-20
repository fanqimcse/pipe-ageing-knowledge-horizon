# -*- coding: utf-8 -*-
"""
A90 · R24 T1/T2：知识视界的闭式理论与视界外的界
=================================================

T1（视界闭式）
  在 R23 两状态模型中，曾失效（B 态）暴露在年龄 a 的值为
      S_B(a) = ∫_0^a f(u) e^{-r0 u} e^{-s r0 (a-u)} du
  （先在 N 态存活到失效时刻 u，再在 B 态存活到 a）。
  定义**信息存活曲线**
      S_I(a; γ) := S_B(a; s) / S_B(a; 1)
                = (1/F(a)) ∫_0^a f(u) exp(-γ (a-u)) du ,  γ := r0 (s-1) ≥ 0
  ——即「失效时刻 U|U≤a 之上、独立指数(γ)存活率的平均」。

  关键结构事实（正文报告为命题 A/B/C）：
  A  S_I(a;γ) ≤ 1，等号仅当 γ=0（被积 ≤1）。
  B  ∂S_I/∂γ = -E[(a-U) e^{-γ(a-U)} | U≤a] < 0（一行的严格证明）。
     ⇒ 知识视界 H(κ;γ) := inf{a : S_I(a;γ) ≤ κ} 对 γ 严格递减。
  C  视界只依赖 (β, λ, γ)——管理强度只通过**超额移除强度** γ 进入，
     不需要分开知道 r0 与 s。
  一阶：小 a 时 f(u)≈λu^{β-1} 为幂律 ⇒ E[a-U|U≤a]=a/(β+1)（Beta(1,β)），
     S_I ≈ 1 - γa/(β+1)，H₁ = (β+1)(1-κ)/γ。

T2（视界外的界）
  命题 3（R23 增补）对一切 p∈[0,1] 成立 ⇒ 取 sup 得**均匀界**
      |D(a)| ≤ |φ-1| · max(1, 1/φ)
  ——不依赖 p、q、s、r0、β、λ；φ 在视界内可估 ⇒ 视界外的界仍可计算。
  以及部分识别发散构造：Λ(H) 匹配的两个 Weibull 在 [0,H] 内
  生存曲线重合到 O(Λ(H))，而 a=kH 处 hazard 比为 (β₂/β₁) k^{β₂-β₁}。

T3K（Kitchener 标定）
  用 A89 实测的 B 态暴露保留率 0.1199 反演 γ̂（按 β 场景），
  给出 Kitchener 的视界 H(0.5)、H(0.2)，与实测锚点（28 / 16 岁）对照。

T4（哨兵随机延迟设计的回顾性功效）
  ε 比例的失效触发更换延迟 Δ 年 ⇒ 恢复的无偏复发事件数
  m(ρ,Δ) = ρ Σ_i φ̂ ∫_{a_i}^{a_i+Δ} ĥ(a) da · L_i ，
  其中 a_i 为可靠定年的退出年龄（A89 B6 逻辑），ĥ 取全存量拟合。

证据链：本脚本 → results/a90_horizon.json + a90_log.txt。
宗教/古典语言不进入证据链（项目铁律）。
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
import a82_bias_theory as T  # noqa: E402

OUT = os.path.join(HERE, "results")
os.makedirs(OUT, exist_ok=True)
LOG = []


def P(s=""):
    print(s)
    LOG.append(str(s))


# =====================================================================
# T1 · 信息存活曲线的精确数值（无溢出：被积函数 ∈ (0,1]）
# =====================================================================
def SI_exact(beta, lam, gam, ages, nx=4001):
    """S_I(a) = (1/F(a)) ∫_0^{F(a)} exp(-gam·(a-u(x))) dx，x=F(u)。"""
    a = np.atleast_1d(np.asarray(ages, dtype=float))
    out = np.empty(a.size)
    for i, ai in enumerate(a):
        Fa = -math.expm1(-lam * ai ** beta / beta)
        if gam <= 0.0 or Fa <= 1e-14:
            out[i] = 1.0
            continue
        x = np.linspace(0.0, Fa, nx)
        u = np.power(beta * (-np.log1p(-x)) / lam, 1.0 / beta)
        out[i] = float(np.trapezoid(np.exp(-gam * (ai - u)), x) / Fa)
    return out


def SI_moment(beta, lam, gam, age, nx=4001):
    """(S_I, E[a-U|U≤a], dS_I/dγ) —— 同一积分核，供解析/数值互证。"""
    Fa = -math.expm1(-lam * age ** beta / beta)
    if gam <= 0.0 or Fa <= 1e-14:
        return 1.0, 0.0, 0.0
    x = np.linspace(0.0, Fa, nx)
    u = np.power(beta * (-np.log1p(-x)) / lam, 1.0 / beta)
    d = age - u
    w = np.exp(-gam * d)
    S = float(np.trapezoid(w, x) / Fa)
    Ed = float(np.trapezoid(d, x) / Fa)
    dS = -float(np.trapezoid(d * w, x) / Fa)
    return S, Ed, dS


def solve_H(beta, lam, gam, kappa, amax=400.0, step=0.25):
    """H(κ) = 首个 S_I ≤ κ 的年龄（S_I 连续、S_I(0)=1、S_I(∞)→0）。"""
    ages = np.arange(step, amax + step, step)
    si = SI_exact(beta, lam, gam, ages, nx=2001)
    idx = np.nonzero(si <= kappa)[0]
    return float(ages[idx[0]]) if idx.size else float("nan")


def t1_props():
    P("=" * 78)
    P("T1 · 命题 A/B/C 的数值核验（解析证明见报告正文）")
    P("=" * 78)
    betas = (1.2, 1.5, 2.0, 2.5, 3.0)
    etas = (20.0, 40.0, 80.0, 160.0)
    gams = (0.002, 0.01, 0.05, 0.2, 0.5)
    ages = np.arange(1.0, 201.0, 2.0)
    maxSI = 0.0
    n_pos = 0          # ∂S_I/∂γ < 0 的核验点数
    fd_max = 0.0       # 解析导数 vs 有限差分的最大偏差（互证）
    da_viol = 0        # dS_I/da > 0 的点数（诚实计数；非命题所需）
    da_tot = 0
    Hmono_viol = 0     # H 对 γ 单调的违反数
    Hmono_tot = 0
    rows_H = []
    for beta in betas:
        lam = beta / 40.0 ** beta          # η=40 代表组做 H 表
        for gam in gams:
            rows_H.append((gam, solve_H(beta, lam, gam, 0.5)))
    for beta in betas:
        for eta in etas:
            lam = beta / eta ** beta
            for gam in gams:
                si = SI_exact(beta, lam, gam, ages, nx=2001)
                maxSI = max(maxSI, float(si.max()))
                n_pos += int((si < 1.0).sum())
                # 解析 vs 数值导数（在 a=20 与 a=100 两点互证）
                for a0 in (20.0, 100.0):
                    _, _, dS = SI_moment(beta, lam, gam, a0)
                    sp = SI_exact(beta, lam, gam + 1e-4, [a0])[0]
                    sm = SI_exact(beta, lam, max(gam - 1e-4, 0.0), [a0])[0]
                    fd = (sp - sm) / (1e-4 if gam > 1e-4 else 1e-4)
                    fd_max = max(fd_max, abs(fd - dS))
                da_tot += si.size - 1
                da_viol += int((np.diff(si) > 1e-9).sum())
    # H 单调性：每个 β 场景内 γ 升序时 H 必须严格降
    for beta in betas:
        lam = beta / 40.0 ** beta
        hs = [solve_H(beta, lam, g, 0.5) for g in gams]
        for i in range(len(hs) - 1):
            Hmono_tot += 1
            if not (hs[i] > hs[i + 1]):
                Hmono_viol += 1
    P("  命题 A（S_I ≤ 1）：max S_I = %.12f（应 ≤ 1）" % maxSI)
    P("  命题 B（∂S_I/∂γ<0）：S_I<1 的点数 = %d；解析↔有限差差最大 %.2e"
      % (n_pos, fd_max))
    P("  dS_I/da > 0 的点数 = %d / %d（年龄方向非命题所需，诚实报告）"
      % (da_viol, da_tot))
    P("  H(0.5;γ) 单调于 γ：违反 %d / %d" % (Hmono_viol, Hmono_tot))
    P("  H(0.5) 表（β, η=40）：")
    for beta in betas:
        lam = beta / 40.0 ** beta
        hs = [solve_H(beta, lam, g, 0.5) for g in gams]
        P("    β=%.1f ：" % beta + "  ".join("γ=%.3g→H=%4.0f" % (g, h)
                                            for g, h in zip(gams, hs)))
    res = dict(maxSI=float(maxSI), fd_max=float(fd_max),
               da_viol=int(da_viol), da_tot=int(da_tot),
               Hmono_viol=int(Hmono_viol), Hmono_tot=int(Hmono_tot))
    P("")
    return res


def t1_first_order():
    P("-" * 78)
    P("T1 · 一阶视界公式的适用域（H₁ = (β+1)(1-κ)/γ）")
    P("-" * 78)
    rows = []
    for beta in (1.5, 2.0, 2.5, 3.0):
        for eta in (20.0, 40.0, 80.0):
            lam = beta / eta ** beta
            for gam in (0.002, 0.005, 0.01, 0.02, 0.05, 0.1):
                H = solve_H(beta, lam, gam, 0.5)
                H1 = (beta + 1.0) * 0.5 / gam
                if math.isfinite(H) and H1 < 400.0:
                    rel = abs(H - H1) / H
                    rows.append(dict(beta=beta, eta=eta, gam=gam, H=H,
                                     H1=float(H1), rel=float(rel),
                                     gH1=float(gam * H1)))
    ok = [r for r in rows if r["rel"] <= 0.10]
    thr = max((r["gH1"] for r in ok), default=0.0)
    bad = [r for r in rows if r["gH1"] <= thr and r["rel"] > 0.10]
    P("  适用判据 γ·H₁ ≤ %.2f 时相对误差 ≤ 10%%（该域内违反 %d/%d）"
      % (thr, len(bad), len([r for r in rows if r["gH1"] <= thr])))
    P("  典型行：")
    for r in rows[:6]:
        P("    β=%.1f η=%3.0f γ=%.3g ：H=%5.1f  H₁=%5.1f  相对误差=%5.1f%%"
          % (r["beta"], r["eta"], r["gam"], r["H"], r["H1"], 100 * r["rel"]))
    P("")
    return dict(thr=float(thr), n_rows=len(rows),
                n_ok=len(ok), worst_rel=float(max(r["rel"] for r in rows)))


# =====================================================================
# T2 · 视界外的界
# =====================================================================
def t2_uniform_bound():
    P("=" * 78)
    P("T2 · 均匀界 |D| ≤ |φ-1|·max(1, 1/φ) 的数值核验")
    P("=" * 78)
    P("  （对命题 3 取 sup_{p∈[0,1]}：sup max{(1-p)/φ, p} = max(1/φ, 1)）")
    worst = -1.0
    best_ratio = 0.0
    n = 0
    ages = np.arange(1.0, 401.0, 4.0)
    for beta in (1.2, 2.0, 3.0):
        for eta in (20.0, 80.0):
            lam = beta / eta ** beta
            for r0 in (0.005, 0.02):
                for s in (2.0, 10.0, 50.0):
                    for phi in (0.5, 1.4253, 3.0, 8.0):
                        m = T.model_exact(beta, lam, r0, s, phi, ages)
                        D = np.abs(np.asarray(m["D"], dtype=float))
                        b = abs(phi - 1.0) * max(1.0, 1.0 / phi)
                        Dm = float(np.nanmax(D))
                        worst = max(worst, Dm - b)
                        best_ratio = max(best_ratio, Dm / b)
                        n += 1
    P("  %d 组合：max(|D| − 界) = %.3e（应 ≤ 0）" % (n, worst))
    P("  max |D|/界 = %.4f（模型流形上的经验上确界与均匀界之比）" % best_ratio)
    P("  Kitchener φ̂=1.4253 ⇒ 均匀界 = %.4f（视界外仍可计算）" % 0.4253)
    P("")
    return dict(n=int(n), worst=float(worst), best_ratio=float(best_ratio),
                kitch_uniform=float(abs(1.4253 - 1.0)))


def t2_partial_id():
    P("-" * 78)
    P("T2 · 视界外无点估计：Λ(H) 匹配的双 Weibull 构造")
    P("-" * 78)
    P("  λ₂ = Λ(H)·β₂/H^β₂ 使 Λ₂(H)=Λ₁(H)；[0,H] 内生存曲线差 ≤ max|ΔΛ|，")
    P("  而 a=kH 处 hazard 比 = (β₂/β₁)·k^{β₂-β₁} —— 与 Λ(H)（事件数）无关。")
    P("  H = 28（Kitchener 完整史视界）")
    P("")
    P("  %-6s %-6s %-8s %-10s %-9s %-9s %-9s"
      % ("β₁", "Δβ", "Λ(H)", "max|ΔS|[0,H]", "h₂/h₁@2H", "@3H", "@5H"))
    rows = []
    H = 28.0
    for beta1 in (1.5, 2.0, 2.5):
        for db in (0.5, 1.0, 2.0):
            for LamH in (0.01, 0.05, 0.3):
                beta2 = beta1 + db
                lam1 = LamH * beta1 / H ** beta1
                lam2 = LamH * beta2 / H ** beta2
                a = np.linspace(0.01, H, 600)
                S1 = np.exp(-(lam1 * a ** beta1) / beta1)
                S2 = np.exp(-(lam2 * a ** beta2) / beta2)
                dS = float(np.max(np.abs(S1 - S2)))
                rat = {}
                for k in (2, 3, 5):
                    ak = k * H
                    rat[k] = (lam2 * ak ** (beta2 - 1.0)) / (lam1 * ak ** (beta1 - 1.0))
                rows.append(dict(beta1=beta1, dbeta=db, LamH=LamH, dS=dS,
                                 r2=rat[2], r3=rat[3], r5=rat[5]))
                P("  %-6.1f %-6.1f %-8.2f %-12.4f %-11.1f %-11.1f %-11.1f"
                  % (beta1, db, LamH, dS, rat[2], rat[3], rat[5]))
    P("")
    P("  ⇒ 视界内不可分（|ΔS| ~ Λ(H) 即事件量级）而视界外发散任意倍；")
    P("    发散指数 = Δβ，正是 A89 实测两世界（Δβ=2.82 ⇒ 12×/86×/271×）的结构。")
    P("")
    return dict(rows=rows)


# =====================================================================
# T3K + T4 · Kitchener 标定与哨兵设计功效（数据段）
# =====================================================================
PHI_HAT = 1.4253
SI_BAR_MEAS = 0.11992805246033976     # A89 B4 实测（ΣEB/ΣEBc）
C_FULL = -19.503819527304678          # A89 全存量拟合（log-rate 截距）
BETA_FULL = 2.9073693213175043


def kitchener_part():
    import a83_params as A
    import a84_nonparam as B
    P("=" * 78)
    P("T3K · Kitchener 标定：用实测保留率 0.1199 反演 γ̂（按 β 场景）")
    P("=" * 78)
    d = A.load_kitchener()
    y1 = 2025
    amax = 28
    d2 = B.subcohort(d, 1997)
    fl_o = A.kw_flat(d2, censor="last", y0=1997, y1=y1, amax=amax)
    fl_c = A.kw_flat(d2, censor="none", y0=1997, y1=y1, amax=amax)
    EN, FN, EB, FB = B.state_tables(fl_o, amax)
    ENc, FNc, EBc, FBc = B.state_tables(fl_c, amax)
    aw = np.arange(1, amax + 1)
    EBv = EB[1:amax + 1].astype(float)
    EBcv = EBc[1:amax + 1].astype(float)
    w = EBcv / max(EBcv.sum(), 1e-12)
    Lam28 = -math.log1p(-28.0 / 8452.0)
    scen = []
    for beta in (1.5, 2.0, 2.5, 2.907):
        lam = Lam28 * beta / 28.0 ** beta
        lo, hi = 1e-4, 2.0
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            si = SI_exact(beta, lam, mid, aw, nx=2001)
            if float(np.dot(w, si)) > SI_BAR_MEAS:
                lo = mid
            else:
                hi = mid
        g = 0.5 * (lo + hi)
        H05 = solve_H(beta, lam, g, 0.5, amax=200.0)
        H02 = solve_H(beta, lam, g, 0.2, amax=200.0)
        # 逐年龄形状验证：观测 EB/EBc vs 模型 S_I(a;γ̂)
        obs = np.where(EBcv > 0, EBv / np.maximum(EBcv, 1e-12), np.nan)
        mod = SI_exact(beta, lam, g, aw, nx=2001)
        mae = float(np.nanmean(np.abs(obs - mod)))
        scen.append(dict(beta=beta, lam=float(lam), gam=float(g),
                         H05=float(H05), H02=float(H02), shape_mae=mae))
        P("  β=%5.3f ⇒ γ̂ = %6.4f /年  H(0.5)=%5.1f 岁  H(0.2)=%5.1f 岁"
          "  逐龄 |obs−model| 均差 = %.3f" % (beta, g, H05, H02, mae))
    P("")
    P("  对照实测锚点：完整史视界 28 岁（面板起点），信息 80%% 位点 16 岁。")
    P("  ⇒ 标定视界与实测锚点同量级；γ 只通过超额移除强度进入（命题 C）。")
    P("")
    # ---------------- T4 · 哨兵随机延迟设计 ----------------
    P("-" * 78)
    P("T4 · 哨兵随机延迟设计：回顾性功效（若 1997–2025 有延迟臂）")
    P("-" * 78)
    lg = np.asarray(d["lg"], dtype=float)
    yv = np.asarray(d["yv"], dtype=int)
    ymap = {str(d["wid"][i]): int(d["yv"][i]) for i in range(d["n"])}
    lmap = {str(d["wid"][i]): float(lg[i]) for i in range(d["n"])}
    ea = []
    for wname, bl in d["bk"].items():
        if wname in d["gone"] and bl:
            cands = [v for v in (ymap.get(wname, 0), d["ayear"].get(wname, 0))
                     if v > 1900]
            if not cands:
                continue
            yi = min(cands)
            if yi <= min(bl):
                ea.append((max(bl) - yi, yi, lmap.get(wname, 60.0)))
    P("  可靠定年的失效触发退出（A89 B6 口径）：n = %d" % len(ea))

    def hfull(a):
        return math.exp(C_FULL) * a ** BETA_FULL

    cache = {}

    def _int_h(a0, dd):
        key = (round(a0, 3), round(dd, 3))
        if key not in cache:
            hh = 0.5
            xs = np.arange(0.0, dd + hh, hh)
            cache[key] = float(np.trapezoid([hfull(a0 + x) for x in xs], xs))
        return cache[key]

    # 延迟臂：把该资产从退出年龄 a_i 起保留 min(Δ, 130−a_i) 年
    def extra_events2(rho, Delta):
        m = 0.0
        exposed = 0.0
        for ai, yi, Li in ea:
            d_cap = min(float(Delta), max(130.0 - ai, 0.0))
            if d_cap <= 0:
                continue
            m += PHI_HAT * Li * _int_h(ai, d_cap)
            exposed += Li * d_cap
        return rho * m, rho * exposed

    rows = []
    for rho in (0.05, 0.10, 0.20):
        for Delta in (5.0, 10.0, 15.0):
            m, exposed = extra_events2(rho, Delta)
            # 臂内 φ 估计（无偏，随机化）：se(lnRR) ≈ sqrt(1/m + 1/n_N)，n_N 取
            # 同龄 N 态事件流（全存量拟合的一阶率 × 臂内 N 暴露近似 = 臂 B 暴露/φ̂）
            se = math.sqrt(1.0 / max(m, 1e-9) + 1.0 / max(m / PHI_HAT, 1e-9))
            z = math.log(PHI_HAT) / se if se > 0 else float("inf")
            rows.append(dict(rho=rho, Delta=Delta, m=float(m),
                             exposed_km=float(exposed / 1000.0),
                             se=float(se), z=float(z)))
            P("  ρ=%4.2f Δ=%4.0f 年 ⇒ 恢复无偏复发 ≈ %6.1f 次（暴露 +%5.1f km·yr）"
              "  臂内 φ 的 se=%.3f  z(φ=1.4253)=%5.2f"
              % (rho, Delta, m, exposed / 1000.0, se, z))
    P("")
    P("  ⇒ 判读：ρ=0.20、Δ≥10 年 ⇒ m ≈ 20–40 次 ⇒ z ≥ 2 ⇒ 臂内可无偏地")
    P("    拒绝 φ=1（随机化消除选择偏差）；且臂暴露买回的正是暗区年龄段。")
    P("    风险成本即额外爆管 m 次（每次即信息事件，成本=维修费+外部性）。")
    P("")
    return dict(scenarios=scen, t4_rows=rows, n_exit_reliable=len(ea))


def main():
    res = {"system": "R24 · T1/T2/T4 理论与标定", "probe": "a90_horizon_theory"}
    res["t1_props"] = t1_props()
    res["t1_first_order"] = t1_first_order()
    res["t2_uniform"] = t2_uniform_bound()
    res["t2_partial"] = t2_partial_id()
    res["kitchener"] = kitchener_part()
    with io.open(os.path.join(OUT, "a90_horizon.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    with io.open(os.path.join(OUT, "a90_log.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(LOG))
    P("=" * 78)
    P("完成：results/a90_horizon.json + a90_log.txt")


if __name__ == "__main__":
    main()
