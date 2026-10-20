# -*- coding: utf-8 -*-
"""生成稿件图件（数据全部来自 results/*.json）。

Water Research 版式：单栏 85 mm，双栏 170 mm。
"""
import json
import math
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
FIG = os.path.join(HERE, "figs")
os.makedirs(FIG, exist_ok=True)

PN = json.load(open(os.path.join(RES, "paper_numbers.json"), encoding="utf-8"))
try:
    BT = json.load(open(os.path.join(RES, "a96_boot.json"), encoding="utf-8"))
except Exception:
    BT = {}

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "font.size": 7.5,
    "axes.labelsize": 8,
    "axes.titlesize": 8.5,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 6.8,
    "axes.linewidth": 0.6,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "xtick.major.size": 2.5,
    "ytick.major.size": 2.5,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

C_N = "#2b6cb0"
C_B = "#c53030"
C_GREY = "#7f8c8d"
C_DARK = "#d9d9d9"


# ----------------------------------------------------------------------
def fig1_model():
    """两状态模型与选择性移除示意。"""
    fig, ax = plt.subplots(figsize=(85 / 25.4, 62 / 25.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.2)
    ax.axis("off")

    def box(x, y, t, c, w=2.6, h=1.1):
        ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                    boxstyle="round,pad=0.08,rounding_size=0.18",
                                    fc="white", ec=c, lw=1.1))
        ax.text(x, y, t, ha="center", va="center", fontsize=7.6, color=c)

    box(2.0, 4.4, "N\nnever failed", C_N)
    box(7.6, 4.4, "B\nfailed $\\geq$ 1", C_B)

    def arrow(x1, y1, x2, y2, lab, c, curve=0.0, ls="-"):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2),
                                     connectionstyle="arc3,rad=%s" % curve,
                                     arrowstyle="-|>", mutation_scale=8,
                                     lw=0.9, color=c, ls=ls))
        ax.text(0.5 * (x1 + x2), 0.5 * (y1 + y2) + (0.30 if curve == 0 else 0.42),
                lab, ha="center", va="bottom", fontsize=6.6, color=c)

    arrow(3.35, 4.72, 6.25, 4.72, "$h(a)$", C_B, curve=-0.28)
    arrow(6.25, 4.08, 3.35, 4.08, "repair (instantaneous)", C_GREY, curve=-0.28,
          ls=(0, (3, 1.6)))
    arrow(2.0, 3.78, 2.0, 2.45, "$r_0$", C_GREY)
    arrow(7.6, 3.78, 7.6, 2.45, "$s\\,r_0$", C_B)
    ax.text(2.0, 2.1, "renewal\n(baseline)", ha="center", va="top",
            fontsize=6.4, color=C_GREY)
    ax.text(7.6, 2.1, "renewal\n(failure-selected)", ha="center", va="top",
            fontsize=6.4, color=C_B)

    ax.text(5.0, 5.95, "selective renewal  $\\gamma = r_0(s-1)$",
            ha="center", va="center", fontsize=7.8, fontweight="bold")
    ax.text(5.0, 0.72,
            "observed hazard  $h_{obs}=h[1+(\\phi-1)p]$      "
            "target  $h_{true}=h[1+(\\phi-1)q]$",
            ha="center", va="center", fontsize=6.8, color="#333333")
    ax.text(5.0, 0.18, "$p$ = share of exposure in B (observed);   "
            "$q=F(a)$ = share that would have failed (no renewal)",
            ha="center", va="center", fontsize=6.2, color=C_GREY)
    fig.tight_layout(pad=0.3)
    fig.savefig(os.path.join(FIG, "fig1_model.pdf"))
    plt.close(fig)


# ----------------------------------------------------------------------
def fig2_defect():
    """(a) 合并替换史：被删记录相对安装年的负年龄分布；(b) φ̂ 修复前后。"""
    fig, axes = plt.subplots(1, 2, figsize=(170 / 25.4, 58 / 25.4))
    ax = axes[0]
    h = PN["datafix"]["neg_years"]["hist"]
    ks = sorted(int(k) for k in h.keys())
    vs = [h[str(k)] for k in ks]
    ax.bar(ks, vs, color=C_B, width=0.85, linewidth=0)
    ax.set_xlabel("years the break record precedes the installed year")
    ax.set_ylabel("records")
    ax.set_title("(a)  merged replacement histories  ($n=%d$ records)"
                 % PN["datafix"]["neg_years"]["n"], loc="left", fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.text(0.98, 0.92, "median %d yr, max %d yr"
            % (PN["datafix"]["neg_years"]["median"],
               PN["datafix"]["neg_years"]["max"]),
            transform=ax.transAxes, ha="right", va="top", fontsize=6.4,
            color="#444444")

    ax = axes[1]
    ph = PN["datafix"]["phi"]
    for i, tag in enumerate(("before", "after")):
        v = ph[tag]
        ax.errorbar([v["phi"]], [1 - i], xerr=[[v["phi"] - v["lo"]],
                                               [v["hi"] - v["phi"]]],
                    fmt="o", ms=4.2, capsize=2.6, lw=1.0,
                    color=(C_GREY if tag == "before" else C_N))
        ax.text(v["hi"] + 0.02, 1 - i, "%.4f [%.4f, %.4f]"
                % (v["phi"], v["lo"], v["hi"]), va="center", fontsize=6.6,
                color=(C_GREY if tag == "before" else C_N))
    ax.axvline(1.0, color="k", ls=(0, (3, 2)), lw=0.8)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["after fix", "before fix"])
    ax.set_ylim(-0.6, 1.6)
    ax.set_xlim(1.15, 1.80)
    ax.set_xlabel("recurrence rate ratio $\\hat\\phi$ (Mantel–Haenszel, "
                  "age-stratified)")
    ax.set_title("(b)  impact on $\\hat\\phi$", loc="left", fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.text(1.0, -0.42, "$H_0:\\phi=1$", fontsize=6.2, ha="center",
            color="#444444")
    fig.tight_layout(pad=0.6)
    fig.savefig(os.path.join(FIG, "fig2_defect.pdf"))
    plt.close(fig)


# ----------------------------------------------------------------------
def fig3_retention():
    """B 态暴露保留曲线（观测 vs 模型）与知识视界。"""
    co = PN["cohort"]
    amax = co["amax"]
    aw = list(range(1, amax + 1))
    obs = co["retention_by_age"]
    eb = co["EBc_by_age"]
    fig, ax = plt.subplots(figsize=(85 / 25.4, 70 / 25.4))
    ax2 = ax.twinx()
    ax2.bar(aw, [e / 1000.0 for e in eb], color=C_DARK, width=0.9, linewidth=0)
    ax2.set_ylabel("B-state exposure, counterfactual ($10^3$ m$\\cdot$yr)",
                   color=C_GREY, fontsize=6.8)
    ax2.tick_params(axis="y", colors=C_GREY, labelsize=6.4)
    ax2.set_ylim(0, max(eb) / 1000.0 * 3.4)
    ax2.spines["top"].set_visible(False)

    ax.plot(aw, obs, "o", ms=3.0, color=C_B, label="observed")
    sc = co["gamma_scenarios"]
    curves = np.array([s["model_by_age"] for s in sc])
    lo_c = curves.min(axis=0)
    hi_c = curves.max(axis=0)
    ax.fill_between(aw, lo_c, hi_c, color=C_N, alpha=0.18, lw=0,
                    label="model envelope ($\\beta$ 1.5-2.9)")
    ax.plot(aw, sc[1]["model_by_age"], "-", lw=1.0, color=C_N,
            label="model ($\\beta$=2.00, $\\hat\\gamma$=%.3f/yr)"
                  % sc[1]["gam"])
    ax.axhline(0.5, color="k", ls=(0, (2, 2)), lw=0.7)
    ax.text(amax, 0.5, " 0.5", va="bottom", ha="right", fontsize=6.2)
    ax.axvline(amax, color=C_GREY, ls=(0, (4, 2)), lw=0.8)
    ax.text(amax - 0.3, 1.02, "window $W$=%d yr" % amax, ha="right",
            va="bottom", fontsize=6.4, color=C_GREY)
    ax.set_xlabel("pipe age (yr)")
    ax.set_ylabel("retention of B-state exposure  $S_I(a;\\gamma)$")
    ax.set_ylim(0, 1.12)
    ax.set_xlim(0, amax + 1)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=3,
              frameon=False, fontsize=5.6, handlelength=1.4,
              columnspacing=0.9, handletextpad=0.4)
    ax.spines["top"].set_visible(False)
    fig.tight_layout(pad=0.5)
    fig.savefig(os.path.join(FIG, "fig3_retention.pdf"))
    plt.close(fig)


# ----------------------------------------------------------------------
def fig4_worlds():
    """两世界的危险率外推 + 观察窗口/暗区。"""
    import math
    w = PN["worlds"]
    st = PN["stock"]
    co = PN["cohort"]
    fig, ax = plt.subplots(figsize=(170 / 25.4, 62 / 25.4))
    a = [x / 10.0 for x in range(20, 1301)]
    hF = [math.exp(w["bF"]["c"]) * x ** w["bF"]["beta"] for x in a]
    hY = [math.exp(w["bY"]["c"]) * x ** w["bY"]["beta"] for x in a]
    ax.fill_between([0, co["amax"]], 1e-9, 1, color=C_DARK, alpha=0.55, lw=0)
    ax.fill_between([co["amax"], 130], 1e-9, 1, color="#f2f2f2", lw=0)
    ax.plot(a, hF, "-", lw=1.2, color=C_B,
            label="world F: full stock, left-truncated "
                  "($\\beta$=%.2f$\\pm$%.2f)" % (w["bF"]["beta"], w["bF"]["se"]))
    ax.plot(a, hY, "-", lw=1.2, color=C_N,
            label="world Y: complete-history cohort "
                  "($\\beta$=%.2f$\\pm$%.2f)" % (w["bY"]["beta"], w["bY"]["se"]))
    ax.set_yscale("log")
    ax.set_ylim(1e-7, 1e-1)
    ax.set_xlim(2, 130)
    ax.set_xlabel("pipe age (yr)")
    ax.set_ylabel("failure intensity  $h(a)$  (per m$\\cdot$yr)")
    ax.legend(loc="upper left", frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.text(co["amax"] / 2.0, 1.6e-7, "observed window", ha="center",
            va="bottom", fontsize=6.6, color="#555555")
    ax.text((co["amax"] + 130) / 2.0, 3e-2, "dark zone (extrapolation beyond $W$)",
            ha="center", va="center", fontsize=6.6, color="#777777")
    for r in w["ratios"]:
        if r["age"] in (30, 57, 90):
            ax.annotate("", xy=(r["age"], r["hF"]), xytext=(r["age"], r["hY"]),
                        arrowprops=dict(arrowstyle="<->", lw=0.7,
                                        color="#444444"))
            ax.text(r["age"] + 1.5, math.sqrt(r["hF"] * r["hY"]),
                    "%.0f$\\times$" % r["ratio"], fontsize=6.2, color="#444444")
    ax.text(0.99, 0.03, "%.0f%% of network length is older than %d yr"
            % (100 * st["dark_fraction"], co["amax"]),
            transform=ax.transAxes, ha="right", va="bottom", fontsize=6.4,
            color="#444444")
    fig.tight_layout(pad=0.5)
    fig.savefig(os.path.join(FIG, "fig4_worlds.pdf"))
    plt.close(fig)


# ----------------------------------------------------------------------
def fig5_sentinel():
    """哨兵随机延迟设计的两世界功效带。"""
    t4 = PN["t4"]
    fig, ax = plt.subplots(figsize=(85 / 25.4, 62 / 25.4))
    for Delta in (5.0, 10.0, 15.0):
        rs = [r for r in t4["rows"] if abs(r["Delta"] - Delta) < 1e-9]
        rs.sort(key=lambda r: r["rho"])
        ax.plot([r["rho"] for r in rs], [r["mF"] for r in rs], "-o", ms=3.2,
                lw=1.0, color=C_B, label="$\\Delta$=%d yr, world F" % Delta)
        ax.plot([r["rho"] for r in rs], [r["mY"] for r in rs], "--s", ms=3.0,
                lw=0.9, color=C_N, label="$\\Delta$=%d yr, world Y" % Delta)
    ax.set_yscale("log")
    ax.set_xlabel("randomisation fraction $\\rho$ (defer renewal)")
    ax.set_ylabel("expected recovered break events  $m$")
    ax.legend(frameon=False, fontsize=5.8, ncol=2, loc="upper left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.text(0.98, 0.04, "$n=%d$ failure-triggered removals"
            % t4["n_exit"], transform=ax.transAxes, ha="right", va="bottom",
            fontsize=6.2, color="#444444")
    fig.tight_layout(pad=0.5)
    fig.savefig(os.path.join(FIG, "fig5_sentinel.pdf"))
    plt.close(fig)


if __name__ == "__main__":
    fig1_model()
    fig2_defect()
    fig3_retention()
    fig4_worlds()
    fig5_sentinel()
    print("figures:", sorted(os.listdir(FIG)))
