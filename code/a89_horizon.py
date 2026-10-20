# -*- coding: utf-8 -*-
"""
A89 · 「知识视界」可行性探针（R24 路线重设计的第一块试金石）

===================== 探针要回答的问题 =====================
重设计路线「管理即删失」的核心主张是：基础设施管理者面对的不是一个估计问题，
而是一个**可学习性**问题——更换决策所指向的资产年龄域，超出了失效数据所能
支持的**知识视界**。本探针在 Kitchener 上验证这个主张是否可计算：

  B1 · 完整失效史覆盖率：存量中有多少管段拥有「面板起点早于安装年」的完整史？
  B2 · 存量年龄结构 vs 完整史年龄上限：更换决策指向的「暗区」有多大？
  B3 · 首次失效信息的年龄分布：信息质量集中在哪个年龄以下？
  B4 · 风险集暴露的选择性耗竭：移除摧毁了多少 B 态（曾失效）暴露与预期复发流。
  B5 · 老化斜率的两个世界：完整史青年队列的外推 β vs 左截断全存量的表观 β，
       在更换决策年龄（30–90 岁）上差多少倍。
  B6 · 管理动作的年龄位置：退出发生在哪些年龄，多少在暗区。

===================== 口径声明（证据链） =====================
数据：KW = review18/data_kw（mains.geojson + breaks.geojson）。
年份修正沿用 R23 A83 的规则（mains.INSTALLATION_DATE 与爆管表
ASSET_YEAR_INSTALLED 取较小值；39.8% 记录晚于爆管年 ⇒ 语义为最近干预）。
「观测面板」= censor="last"（gone 资产暴露截于末次爆管年）；
「反事实面板」= censor="none"（暴露延至 2025，**不生成新事件**——
即反事实暴露是无移除下的下界）。φ̂ 取 R23 A85 全队列 MH 值 1.4253。
"""
import io
import json
import math
import os
import sys

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
R23 = os.path.normpath(os.path.join(HERE, "..", "review23"))
sys.path.insert(0, R23)
import a83_params as A  # noqa: E402
import a84_nonparam as B  # noqa: E402

RES = os.path.join(HERE, "results")
os.makedirs(RES, exist_ok=True)
OUT = []

PHI_HAT = 1.4253  # R23 A85 全队列 Mantel–Haenszel


def P(s=""):
    print(s)
    OUT.append(str(s))


def irls_poisson(X, y, off, iters=100):
    """Poisson 回归（阻尼 Newton + 步长减半），返回 (beta, se)。"""
    r = (y + 0.5) / np.exp(np.clip(off, -50, 50))
    beta = np.linalg.lstsq(X, np.log(np.clip(r, 1e-12, None)), rcond=None)[0]

    def ll(b):
        eta = off + X @ b
        return float(np.sum(y * eta - np.exp(np.clip(eta, -50, 50))))

    for _ in range(iters):
        eta = off + X @ beta
        mu = np.exp(np.clip(eta, -50, 50))
        g = X.T @ (y - mu)
        H = X.T @ (X * mu[:, None])
        try:
            step = np.linalg.solve(H, g)
        except np.linalg.LinAlgError:
            break
        t, ll0 = 1.0, ll(beta)
        for _ in range(40):
            cand = beta + t * step
            if ll(cand) >= ll0 - 1e-12:
                break
            t *= 0.5
        beta = beta + t * step
        if np.max(np.abs(t * step)) < 1e-10:
            break
    eta = off + X @ beta
    mu = np.exp(np.clip(eta, -50, 50))
    cov = np.linalg.inv(X.T @ (X * mu[:, None]))
    return beta, np.sqrt(np.diag(cov))


def wquant(x, w, q):
    o = np.argsort(x)
    xs, ws = np.asarray(x)[o], np.asarray(w)[o]
    cw = np.cumsum(ws) / np.sum(ws)
    return float(xs[min(np.searchsorted(cw, q, side="left"), xs.size - 1)])


def cum_from_top(v):
    return np.cumsum(v[::-1])[::-1]


def main():
    d = A.load_kitchener()
    y1 = 2025
    res = {}

    P("=" * 76)
    P("A89 · 知识视界可行性探针（Kitchener，面板 1997–%d）" % y1)
    P("=" * 76)
    P("  数据质量口径沿用 R23 A83：安装年 = min(mains 字段, 爆管表字段)。")
    P("  回填 %d 处，冲突取小 %d 处。φ̂ = %.4f（R23 A85）。"
      % (d["n_backfill"], d["n_conflict"], PHI_HAT))
    P("")

    # ---------------- B1/B2 · 覆盖率与存量年龄结构 ----------------
    lg = np.asarray(d["lg"], dtype=float)
    yv = np.asarray(d["yv"], dtype=int)
    m = yv > 1900
    tot_km = float(lg[m].sum())
    covs = {}
    P("-" * 76)
    P("B1 · 完整失效史覆盖率（安装年 ≥ 阈值 ⇒ 无左截断）")
    for ymin in (1997, 2000, 2005, 2010):
        cov = float(lg[m & (yv >= ymin)].sum() / tot_km)
        covs[str(ymin)] = cov
        P("  安装 ≥ %d ：%.1f%% 的存量（km 计）" % (ymin, 100 * cov))
    res["coverage_km"] = covs
    P("")

    ages_stock = (y1 - yv[m]).astype(float)
    km_stock = lg[m]
    qs = {str(q): wquant(ages_stock, km_stock, q / 100.0)
          for q in (25, 50, 75, 90)}
    H_COMP = y1 - 1997  # 完整史年龄上限 = 28
    dark_km = float(lg[m & (yv < 1997)].sum() / tot_km)
    P("B2 · 存量年龄结构（km 加权）：P25=%d  P50=%d  P75=%d  P90=%d 岁"
      % (qs["25"], qs["50"], qs["75"], qs["90"]))
    P("  完整史年龄上限（面板起点 1997 ⇒ 最老可完整观测 %d 岁）。" % H_COMP)
    P("  ⇒ 存量的 %.1f%%（km）年龄 > %d 岁：处于**无完整失效史的暗区**。"
      % (100 * dark_km, H_COMP))
    res["stock_age_quantiles"] = qs
    res["dark_fraction_km"] = dark_km
    res["H_complete"] = int(H_COMP)
    P("")

    # ---------------- B3/B4 · 1997 子队列的信息曲线 ----------------
    amax = H_COMP
    d2 = B.subcohort(d, 1997)
    fl_o = A.kw_flat(d2, censor="last", y0=1997, y1=y1, amax=amax)
    fl_c = A.kw_flat(d2, censor="none", y0=1997, y1=y1, amax=amax)
    EN, FN, EB, FB = B.state_tables(fl_o, amax)
    ENc, FNc, EBc, FBc = B.state_tables(fl_c, amax)

    P("-" * 76)
    P("B3 · 首次失效信息的年龄分布（1997 完整史子队列，%d 单元）"
      % int(fl_o["n_unit"]))
    P("  首次失效事件：观测 %d / 反事实 %d（相同——移除发生于失效之后，"
      "首次信息受限于右截断而非选择）" % (FN.sum(), FNc.sum()))
    aw = np.arange(1, amax + 1)
    winfo = FN[1:] / max(FN[1:].sum(), 1e-12)
    cum = np.cumsum(winfo)
    H80 = int(aw[min(np.searchsorted(cum, 0.8), aw.size - 1)])
    last_ev = int(max([a for a in aw if FN[a] > 0] or [0]))
    P("  80%% 的首次失效信息集中在年龄 ≤ %d 岁；有事件的最大年龄 = %d 岁。"
      % (H80, last_ev))
    res["first_info"] = dict(total_obs=float(FN.sum()),
                             H80=H80, last_age=last_ev)
    P("")

    P("B4 · 风险集暴露与复发信息流的选择性耗竭")
    eb_ret = float(EB.sum() / max(EBc.sum(), 1e-12))
    P("  B 态（曾失效）暴露保留率 = %.3f（观测 %.0f m·yr / 反事实 %.0f m·yr）"
      % (eb_ret, EB.sum(), EBc.sum()))
    # 复发流估计（同质性率，data-only）：被毁暴露 × 观测 B 态率
    hB = FB.sum() / max(EB.sum(), 1e-12)
    destroyed = float(EBc.sum() - EB.sum())
    exp_rep_destroyed = float(hB * destroyed)
    flow_surv = float(FB.sum() / max(FB.sum() + exp_rep_destroyed, 1e-12))
    P("  观测复发事件 = %d 次；被毁暴露 %.0f m·yr × 观测 B 态率 %.2e"
      % (FB.sum(), destroyed, hB))
    P("    ⇒ 被移除毁掉的期望复发 ≈ %.0f 次（同质率下界；老化使真值更高）"
      % exp_rep_destroyed)
    P("  ⇒ 复发信息流存活率 ≈ %.3f；φ 估计精度损失因子 ≈ %.2f 倍"
      % (flow_surv, math.sqrt((FB.sum() + exp_rep_destroyed) /
                              max(FB.sum(), 1.0))))
    res["riskset_info"] = dict(
        EB_retention=eb_ret, FB_obs=float(FB.sum()),
        destroyed_exposure=destroyed, exp_rep_destroyed=exp_rep_destroyed,
        flow_survival=flow_surv,
        se_inflation=float(math.sqrt((FB.sum() + exp_rep_destroyed) /
                                      max(FB.sum(), 1.0))))
    P("")

    # ---------------- B5 · 两个世界的老化斜率 ----------------
    P("-" * 76)
    P("B5 · 老化斜率的两个世界（同一套数据、同一个 Poisson log-rate 模型）")
    fits = {}

    def fit_panel(ENa, FNa, a_lo, a_hi, tag):
        n = ENa.size - 1
        aa = np.arange(1, n + 1)
        msk = (aa >= a_lo) & (aa <= a_hi) & (ENa[1:] > 0)
        a = aa[msk].astype(float)
        y = FNa[1:][msk].astype(float)
        off = np.log(ENa[1:][msk])
        X = np.column_stack([np.ones_like(a), np.log(a)])
        beta, se = irls_poisson(X, y, off)
        fits[tag] = dict(a_lo=int(a_lo), a_hi=int(a_hi), n_ev=float(y.sum()),
                         beta=float(beta[1]), se=float(se[1]),
                         c=float(beta[0]), se_c=float(se[0]))
        P("  %-24s 域 [%3d,%3d] 事件 %6.0f  β = %+.3f ± %.3f"
          % (tag, a_lo, a_hi, y.sum(), beta[1], se[1]))
        return beta

    b_y = fit_panel(EN, FN, 2, amax, "完整史（1997 队列）")
    fl_f = A.kw_flat(d, censor="last", y0=1997, y1=y1, amax=130)
    ENf, FNf, EBf, FBf = B.state_tables(fl_f, 130)
    b_f = fit_panel(ENf, FNf, 2, 130, "全存量（左截断）")
    b_f28 = fit_panel(ENf, FNf, 2, amax, "全存量·同域（含中龄左截断管）")

    P("")
    P("  ⇒ 在更换决策年龄上的外推对比：")
    rows_rate = []
    for a in (30, 60, 90):
        r_y = math.exp(b_y[0] + b_y[1] * math.log(a))
        r_f = math.exp(b_f[0] + b_f[1] * math.log(a))
        rows_rate.append(dict(age=a, rate_y=r_y, rate_f=r_f,
                              ratio=r_f / max(r_y, 1e-300)))
        P("    年龄 %2d 岁：完整史外推 rate=%.2e / 左截断表观 rate=%.2e  ⇒ 相差 %.1fx"
          % (a, r_y, r_f, r_f / max(r_y, 1e-300)))
    P("  ⚠ 表观曲线把老管的复发错记为首次（左截断）且材质/年代混杂——")
    P("    这正是效用公司「眼里」的老化曲线；真实曲线只有亮区可识别。")
    res["beta_worlds"] = fits
    res["decision_age_rates"] = rows_rate
    P("")

    # ---------------- B6 · 退出年龄 ----------------
    P("-" * 76)
    P("B6 · 管理动作的年龄位置（曾爆管且 ASSET_EXISTS=N ⇒ 退出）")
    P("  ⚠ 新数据质量发现：gone 资产的爆管表 ASSET_YEAR_INSTALLED 有 316/2696"
      " 条晚于爆管年且全部集中在 gone——该字段对被换管记录的是**替换管**的"
      "安装年。故退出年龄按下式取下界：install ≤ min(爆管年序列)。")
    ymap = {str(d["wid"][i]): int(d["yv"][i]) for i in range(d["n"])}
    ea, capped, ea_unc = [], 0, []
    for w, bl in d["bk"].items():
        if w in d["gone"] and bl:
            cands = [v for v in (ymap.get(w, 0), d["ayear"].get(w, 0))
                     if v > 1900]
            yi = min(cands) if cands else 0
            if yi <= 1900 or yi > min(bl):
                capped += 1
                yi = min(bl)
            else:
                ea_unc.append(max(bl) - yi)
            ea.append(max(bl) - yi)
    ea = np.asarray(ea, dtype=float)
    if ea.size:
        eq = {str(q): float(np.percentile(ea, q)) for q in (25, 50, 75)}
        qu = {str(q): float(np.percentile(ea_unc, q))
              for q in (25, 50, 75)} if ea_unc else {}
        P("  退出 n=%d，年龄 P25=%.0f P50=%.0f P75=%.0f 岁（退出年=末次爆管年；"
          "%d 个按下界封顶）" % (ea.size, eq["25"], eq["50"], eq["75"], capped))
        if qu:
            P("  未封顶可靠子集 n=%d：P25=%.0f P50=%.0f P75=%.0f 岁"
              % (len(ea_unc), qu["25"], qu["50"], qu["75"]))
        P("  退出年龄 > %d（亮区上限）的比例 = %.1f%%"
          % (H_COMP, 100 * float((ea > H_COMP).mean())))
        res["exit_ages"] = dict(n=int(ea.size), quantiles=eq, capped=capped,
                                unc_quantiles=qu,
                                frac_beyond=float((ea > H_COMP).mean()))
    P("")

    # ---------------- B7 · R23 年份回填的污染计数 ----------------
    P("B7 · R23 安装年回填受新发现的污染范围")
    # load_kitchener 的回填/取小规则下，gone 资产若 ayear 为替换年且 mains 年
    # 缺失，则安装年被高估（年龄被低估）。计数：gone & 有爆管 & ayear > min(bl)
    # 且 mains 年缺失或更晚。
    n_contam = 0
    for w, bl in d["bk"].items():
        if w in d["gone"] and bl and d["ayear"].get(w, 0) > min(bl):
            mv = ymap.get(w, 0)
            if mv <= 1900 or mv >= d["ayear"].get(w, 0):
                n_contam += 1
    P("  gone 且 ayear>min(爆管年) 且 mains 年缺失/更晚 ⇒ 安装年高估的资产数"
      " = %d（占 gone 曾爆管资产的 %.1f%%）"
      % (n_contam, 100 * n_contam / max(sum(1 for w in d["bk"]
                                            if w in d["gone"] and d["bk"][w]), 1)))
    P("  ⇒ 对 R23 各结果的影响量级 = 管段数占比，需在 R24 重算时一并修正。")
    res["backfill_contamination"] = int(n_contam)
    P("")

    P("=" * 76)
    P("探针判据汇总：")
    j1 = dark_km > 0.5
    j2 = eb_ret < 0.5 or flow_surv < 0.5
    r30 = rows_rate[0]["ratio"] if rows_rate else 1.0
    j3 = r30 > 2.0
    P("  B2 暗区占比 %.1f%% > 50%% ⇒ %s" % (100 * dark_km, "成立" if j1 else "不成立"))
    P("  B4 B 态暴露保留 %.3f / 复发流存活 %.3f（任一 < 0.5）⇒ %s"
      % (eb_ret, flow_surv, "成立" if j2 else "不成立"))
    P("  B5 决策年龄两世界相差 %.1fx > 2x ⇒ %s" % (r30, "成立" if j3 else "不成立"))
    res["verdict"] = dict(dark_zone=bool(j1), recurrence_blind=bool(j2),
                          two_worlds=bool(j3))
    P("=" * 76)

    json.dump(dict(system="Kitchener 供水", probe="a89_horizon", **res),
              io.open(os.path.join(RES, "a89_horizon.json"), "w",
                      encoding="utf-8"), ensure_ascii=False, indent=1)
    io.open(os.path.join(RES, "a89_log.txt"), "w", encoding="utf-8").write(
        "\n".join(OUT))
    P("")
    P("写出 results/a89_horizon.json")


if __name__ == "__main__":
    main()
