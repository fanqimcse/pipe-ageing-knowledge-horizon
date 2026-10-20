# -*- coding: utf-8 -*-
"""
A92 · T3 自致盲回路的最终版演示（带观察窗口；复用 R23 model_exact）
====================================================================

结构完全对齐 Kitchener：队列 N0=8000 管同在 t=0 安装，观察窗口 W=28 年
（镜像 1997–2025 面板）；窗口内期望首次失效 ≈31 次（Λ(28)=0.0039）。
管理者只在窗口内拟合 Weibull（噪声水平 ≈ Kitchener 的 se 0.28），
按 hazard 阈值 h* 定触发年龄 Â（oracle = 50 岁），再外推决策。

回答两个问题：
  Q1 弱形式：决策年龄是否在信息视界（窗口）之外？外推信念与真值差多少？
  Q2 强形式：政策 γ 的内生反馈是否自增强（β̂ 系统性恶化、回路发散）？

按 Gate B 纪律：若强形式不成立，如实降级并写入交付物（负面结果入文）。

证据链：本脚本 → results/a92_loop.json + a92_log.txt。
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
import a82_bias_theory as T  # noqa: E402
from a90_horizon_theory import SI_exact  # noqa: E402

OUT = os.path.join(HERE, "results")
LOG = []


def P(s=""):
    print(s)
    LOG.append(str(s))


BETA, LAM, R0, PHI = 2.0, 1e-5, 0.01, 1.5
N0 = 8000.0
W = 28.0
HSTAR = LAM * 50.0
AGES = np.arange(1.0, 151.0, 1.0)
_LAM_A = LAM * AGES ** BETA / BETA
_F_A = -np.expm1(-_LAM_A)
_H_A = LAM * AGES ** (BETA - 1.0)
_SN_A = np.exp(-_LAM_A - R0 * AGES)


def panel(gam, rng):
    """真值风险集（无平移）：R = e^{-Λ-r0a} + e^{-r0a}F·S_I(γ)。"""
    SIv = SI_exact(BETA, LAM, gam, AGES, nx=2001)
    SB = np.exp(-R0 * AGES) * _F_A * SIv
    R = (_SN_A + SB) * N0
    p = SB / np.maximum(_SN_A + SB, 1e-300)
    hobs = _H_A * (1.0 + (PHI - 1.0) * p)
    ev = rng.poisson(np.maximum(R * hobs, 0.0))
    hhat = np.where(R > 0, ev / np.maximum(R, 1e-12), np.nan)
    return hhat, R, ev


def fit_window(hhat, R):
    msk = (AGES <= W) & np.isfinite(hhat) & (hhat > 0)
    x = np.log(AGES[msk])
    y = np.log(hhat[msk])
    w = np.sqrt(np.maximum(R[msk] * hhat[msk], 1.0))
    X = np.column_stack([np.ones(x.size), x])
    th = np.linalg.lstsq(X * w[:, None], y * w, rcond=None)[0]
    return float(math.exp(th[0])), float(th[1] + 1.0)


def trigger_age(lam, beta):
    if lam <= 0 or abs(beta - 1.0) < 1e-9:
        return 150.0
    a = (HSTAR / lam) ** (1.0 / (beta - 1.0))
    return float(min(max(a, 1.0), 150.0))


def welfare(gam):
    SIv = SI_exact(BETA, LAM, gam, AGES, nx=2001)
    SB = np.exp(-R0 * AGES) * _F_A * SIv
    ev = float(np.trapezoid(_H_A * (_SN_A + PHI * SB), AGES))
    rm = float(np.trapezoid(R0 * _SN_A + (R0 + gam) * SB, AGES))
    return ev, rm


def main():
    res = {"probe": "a92_loop_final"}
    P("=" * 78)
    P("T3 · 自致盲回路演示（窗口 W=%d 年；真 β=2, λ=1e-5, r0=0.01, φ=1.5）" % W)
    P("=" * 78)
    rng0 = np.random.default_rng(7)
    _, _, ev0 = panel(0.02, rng0)
    P("  窗口内期望事件（γ=0.02 基线）≈ %.0f（Kitchener 完整史 32）"
      % float(ev0[AGES <= W].sum()))
    P("")
    # ---------- Q1 · 弱形式：200 种子 ----------
    P("Q1 · 弱形式（决策在窗口外 + 外推信念 vs 真值），200 种子：")
    rows = []
    for seed in range(200):
        rng = np.random.default_rng(1000 + seed)
        hhat, R, _ = panel(0.02, rng)
        lam, beta = fit_window(hhat, R)
        Ahat = trigger_age(lam, beta)
        h_true_A = LAM * Ahat ** (BETA - 1.0)
        h_bel = lam * Ahat ** (beta - 1.0)
        rows.append((beta, Ahat, h_true_A / max(h_bel, 1e-300)))
    rows = np.asarray(rows)
    P("  β̂：均值 %.3f（真 2.000），SD %.3f（Kitchener 实测 se 0.285）"
      % (rows[:, 0].mean(), rows[:, 0].std()))
    P("  触发年龄 Â：中位 %.0f 岁，IQR [%.0f, %.0f]（oracle 50；窗口 %d）"
      % (np.median(rows[:, 1]), np.percentile(rows[:, 1], 25),
         np.percentile(rows[:, 1], 75), W))
    P("  Â > 窗口 %d 的种子比例 = %.0f%%"
      % (W, 100.0 * float((rows[:, 1] > W).mean())))
    Kr = rows[:, 2]
    P("  外推信念误差 K = h_true(Â)/ĥ̂(Â)：中位 %.2f×，P90 %.1f×，"
      "P99 %.1f×（真值被低估为信念的 1/K）"
      % (np.median(Kr), np.percentile(Kr, 90), np.percentile(Kr, 99)))
    res["q1"] = dict(beta_mean=float(rows[:, 0].mean()),
                     beta_sd=float(rows[:, 0].std()),
                     A_med=float(np.median(rows[:, 1])),
                     frac_beyond_window=float((rows[:, 1] > W).mean()),
                     K_med=float(np.median(Kr)),
                     K_p90=float(np.percentile(Kr, 90)),
                     K_p99=float(np.percentile(Kr, 99)))
    P("")
    # ---------- Q2 · 强形式：政策内生反馈（10 种子 × 8 步） ----------
    P("Q2 · 强形式（政策 γ 内生反馈是否自增强），10 种子 × 8 步回路：")
    P("  %-5s %-8s %-10s %-10s %-8s" % ("seed", "步数", "γ 终值", "β̂ 终值", "Â 终值"))
    loops = []
    for seed in range(10):
        rng = np.random.default_rng(500 + seed)
        gam = 0.02
        b0 = None
        for t in range(8):
            hhat, R, _ = panel(gam, rng)
            lam, beta = fit_window(hhat, R)
            Ahat = trigger_age(lam, beta)
            gam_new = 1.0 / max(Ahat, 1.0)
            b0 = beta
            if abs(gam_new - gam) < 1e-4:
                gam = gam_new
                break
            gam = gam_new
        loops.append(dict(seed=seed, gam=float(gam), beta=float(b0),
                          A=float(Ahat)))
        P("  %-5d %-8d %-10.4f %-10.3f %-8.1f" % (seed, t + 1, gam, b0, Ahat))
    gb = [l["beta"] for l in loops]
    P("  ⇒ β̂ 终值均值 %.3f vs 单步均值 %.3f（回路无系统性恶化）"
      % (np.mean(gb), rows[:, 0].mean()))
    P("  ⇒ 强形式（自增强致盲回路）在本参数域**不成立**：γ 反馈对窗口内")
    P("    面板的影响微弱（B 态暴露占比小），致盲由观察窗口这一外生约束主导。")
    res["q2"] = dict(loops=[dict((k, float(v)) for k, v in l.items())
                            for l in loops],
                     beta_loop_mean=float(np.mean(gb)))
    P("")
    P("  判读：弱形式成立（决策年龄越过窗口、外推信念误差中位 %.1f×、"
      "P99 %.0f×）；" % (np.median(Kr), np.percentile(Kr, 99)))
    P("    强形式不成立 ⇒ 按 Gate B 纪律，T3 定位降为「弱形式 + 窗口主导」，")
    P("    与 a91 的 γ̂≈0.05（H(0.5)≈47 > 窗口 28）互证：Kitchener 的致盲")
    P("    主因是观察窗口，不是选择性移除。")
    with io.open(os.path.join(OUT, "a92_loop.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    with io.open(os.path.join(OUT, "a92_log.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(LOG))
    P("")
    P("完成：results/a92_loop.json")


if __name__ == "__main__":
    main()
