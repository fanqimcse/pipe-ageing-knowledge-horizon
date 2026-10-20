# -*- coding: utf-8 -*-
"""a93 · 知识视界理论的严格重算（修正 a90 的数值缺陷）

修正要点（相对 a90）：
  1. S_I 直接在 t=Lambda 空间用峰值平移计算，避免 a90 的 inf/NaN；
  2. 视界改用「运行下确界」定义 H(kappa) = sup{a: inf_{u<=a} S_I(u) >= kappa}，
     使 ∂H/∂gamma < 0 不依赖 S_I 对 a 的单调性（a90 的 3/20 违反即源于此）；
  3. 解析导数与有限差逐点互证（a90 的 6.97e+01 是域长/步长错配）；
  4. 一阶公式的适用域按实测相对误差重新界定（a90 声称 ≤10% 实际违反 45/52）。
"""
import os
import json
import math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "results")
os.makedirs(OUT, exist_ok=True)
LOG = []


def P(s=""):
    print(s)
    LOG.append(str(s))


# ----------------------------------------------------------------------
# 基础量：Weibull hazard h(a) = lam * a^(beta-1)，Lambda(a) = lam*a^beta/beta
# ----------------------------------------------------------------------
def Lam(a, lam, beta):
    return lam * np.power(np.maximum(a, 0.0), beta) / beta


def _cumsimp(y, h):
    """Simpson 累积积分，返回长度与 y 相同的数组（首元素 0）。"""
    n = y.size
    out = np.zeros(n)
    if n < 3:
        out[1:] = np.cumsum(0.5 * h * (y[1:] + y[:-1]))
        return out
    # 前两个点用梯形
    out[1] = 0.5 * h * (y[0] + y[1])
    # Simpson 1/3 on [0,2]
    if n >= 3:
        out[2] = h * (y[0] + 4.0 * y[1] + y[2]) / 3.0
    for i in range(3, n):
        if i % 2 == 1:
            out[i] = out[i - 1] + h * (y[i - 2] + 4.0 * y[i - 1] + y[i]) / 3.0
        else:
            out[i] = out[i - 1] + h * (y[i - 2] + 4.0 * y[i - 1] + y[i]) / 3.0
    return out


def _hermite(xq, h, Gt, integ):
    """在等距网格 t=0,h,2h,... 上用三次 Hermite 插值累积积分 G。
    G'(t) = integ(t)，故每段 [t_i, t_i+h] 上用两端值+两端导数做三次插值积分。"""
    Gt = np.asarray(Gt, float)
    it = np.asarray(integ, float)
    n = Gt.size
    x = np.clip(np.asarray(xq, float) / h, 0.0, n - 1.0 - 1e-12)
    i = np.floor(x).astype(int)
    i = np.minimum(i, n - 2)
    s = x - i
    G0 = Gt[i]
    G1 = Gt[i + 1]
    d0 = it[i]
    d1 = it[i + 1]
    s2 = s * s
    s3 = s2 * s
    h00 = 2 * s3 - 3 * s2 + 1
    h10 = s3 - 2 * s2 + s
    h01 = -2 * s3 + 3 * s2
    h11 = s3 - s2
    return G0 * h00 + h * d0 * h10 + G1 * h01 + h * d1 * h11


class SI:
    """给定 (beta, lam, gamma)，在固定年龄网格上给出 S_I 与其解析导数。

    S_I(a) = e^{-gamma a} * M(a) / F(a)
      M(a) = int_0^a f(u) e^{gamma u} du
      F(a) = 1 - e^{-Lambda(a)}
    在 t = Lambda(u) 空间：dt = h(u) du, f(u) du = e^{-t} dt,
      u = (beta t / lam)^{1/beta}
      M(a) = int_0^{Lam(a)} exp(-t + gamma*(beta t/lam)^{1/beta}) dt
      M1(a)= int_0^{Lam(a)} u(t) * exp(-t + gamma*u(t)) dt
    """

    def __init__(self, beta, lam, gamma, ages, nx=20001):
        self.beta = float(beta)
        self.lam = float(lam)
        self.gam = float(gamma)
        self.ages = np.asarray(ages, float)
        Lmax = float(np.max(Lam(self.ages, self.lam, self.beta)))
        self.Lmax = Lmax
        if Lmax <= 0.0:
            self.SI = np.ones_like(self.ages)
            self.dSI = np.zeros_like(self.ages)
            return
        t = np.linspace(0.0, Lmax, nx)
        h = t[1] - t[0]
        u = np.power(np.maximum(self.beta * t / self.lam, 0.0), 1.0 / self.beta)
        psi = -t + self.gam * u
        pm = float(np.max(psi))
        w = np.exp(psi - pm)
        wu = w * u
        Mt = _cumsimp(w, h)
        M1t = _cumsimp(wu, h)
        La = Lam(self.ages, self.lam, self.beta)
        M = _hermite(La, h, Mt, w) * math.exp(pm)
        M1 = _hermite(La, h, M1t, wu) * math.exp(pm)
        F = 1.0 - np.exp(-La)
        eg = np.exp(-self.gam * self.ages)
        small = F < 1e-300
        Fs = np.where(small, 1.0, F)
        SIv = eg * M / Fs
        SIv = np.where(small, 1.0, SIv)
        # 解析导数 dS_I/dgamma = e^{-g a}(M1 - a M)/F
        d = eg * (M1 - self.ages * M) / Fs
        d = np.where(small, 0.0, d)
        self.SI = SIv
        self.dSI = d

    def horizon(self, kappa, ages=None):
        """H(kappa) = sup{ a : inf_{u<=a} S_I(u) >= kappa }（运行下确界版）。"""
        a = self.ages if ages is None else np.asarray(ages, float)
        s = self.SI
        run = np.minimum.accumulate(s)
        ok = run >= kappa
        if not np.any(ok):
            return 0.0
        idx = int(np.max(np.nonzero(ok)[0]))
        if idx >= a.size - 1:
            return float("inf")
        # 线性插值到 run = kappa
        r0, r1 = run[idx], run[idx + 1]
        if r1 < r0 - 1e-15:
            t = (r0 - kappa) / max(r0 - r1, 1e-300)
            return float(a[idx] + t * (a[idx + 1] - a[idx]))
        return float(a[idx])


# ----------------------------------------------------------------------
def t1_props():
    P("=" * 74)
    P("T1 · 命题 A/B/C 的严格数值核验（重算版 a93）")
    P("=" * 74)
    ages = np.arange(0.5, 200.001, 0.25)
    maxSI = -np.inf
    minSI = np.inf
    dpos = 0
    dneg = 0
    dzero = 0
    fd_err = 0.0
    da_pos = 0
    da_tot = 0
    cases = []
    for beta in (1.2, 1.5, 2.0, 2.5, 3.0):
        for gam in (0.0, 0.002, 0.01, 0.05, 0.2, 0.5):
            for eta in (20.0, 40.0):
                lam = eta * beta / (100.0 ** beta)
                cases.append((beta, lam, gam))
    for beta, lam, gam in cases:
        o = SI(beta, lam, gam, ages)
        s = o.SI
        if not np.all(np.isfinite(s)):
            P("  !! 非有限值 beta=%.1f gam=%.3f" % (beta, gam))
            continue
        maxSI = max(maxSI, float(np.max(s)))
        minSI = min(minSI, float(np.min(s)))
        d = o.dSI
        dpos += int(np.sum(d > 1e-14))
        dneg += int(np.sum(d < -1e-14))
        dzero += int(np.sum(np.abs(d) <= 1e-14))
        # 有限差互证（仅对 gamma>0 且导数尺度合理的点）
        if gam > 0:
            eps = gam * 1e-4
            o2 = SI(beta, lam, gam + eps, ages)
            fd = (o2.SI - s) / eps
            m = np.abs(d) > 1e-6
            if np.any(m):
                rel = np.max(np.abs(fd[m] - d[m]) / np.abs(d[m]))
                fd_err = max(fd_err, float(rel))
        dd = np.diff(s)
        da_pos += int(np.sum(dd > 1e-12))
        da_tot += dd.size
    P("  命题 A（S_I ≤ 1）：max S_I = %.12f（应 ≤ 1）" % maxSI)
    P("  命题 A 下侧：min S_I = %.6f" % minSI)
    P("  命题 B（∂S_I/∂γ ≤ 0）：d>0 的点 %d；d<0 的点 %d；|d|≤1e-14 的点 %d"
      % (dpos, dneg, dzero))
    P("  命题 B 解析↔有限差：最大相对误差 = %.3e" % fd_err)
    P("  （非命题）dS_I/da > 0 的点 = %d / %d —— S_I 对 a 非单调，故视界用"
      "运行下确界定义" % (da_pos, da_tot))
    okA = maxSI <= 1.0 + 1e-9
    okB = (dpos == 0) and (fd_err < 1e-3)
    P("  ⇒ 命题 A %s；命题 B %s" % ("通过" if okA else "未通过",
                                    "通过" if okB else "未通过"))
    return dict(maxSI=float(maxSI), minSI=float(minSI), d_pos=dpos, d_neg=dneg,
                fd_err=float(fd_err), da_pos=da_pos, da_tot=da_tot,
                okA=bool(okA), okB=bool(okB))


def t1_horizon_mono():
    P("")
    P("-" * 74)
    P("T1 · 命题 B′：视界 H(κ;γ) 对 γ 严格递减（运行下确界定义）")
    P("-" * 74)
    ages = np.arange(0.5, 400.001, 0.25)
    gams = [0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
    viol = 0
    tot = 0
    table = []
    for beta in (1.5, 2.0, 2.5, 2.907):
        row = []
        for gam in gams:
            lam = 40.0 * beta / (100.0 ** beta)
            o = SI(beta, lam, gam, ages)
            row.append(o.horizon(0.5))
        for i in range(len(row) - 1):
            tot += 1
            if not (row[i + 1] < row[i]):
                viol += 1
        table.append((beta, row))
    P("  β      " + "".join("%8.3f" % g for g in gams))
    for beta, row in table:
        P("  %-6.3f " % beta + "".join("%8.1f" % v for v in row))
    P("  单调违反 = %d / %d" % (viol, tot))
    okC = (viol == 0)
    P("  ⇒ 命题 B′ %s" % ("通过" if okC else "未通过"))
    return dict(gammas=gams, rows=[dict(beta=b, H=r) for b, r in table],
                viol=viol, tot=tot, ok=bool(okC))


def t1_first_order():
    P("")
    P("-" * 74)
    P("T1 · 一阶视界 H₁ = (β+1)(1−κ)/γ 的适用域（重估）")
    P("-" * 74)
    ages = np.arange(0.05, 600.001, 0.05)
    rows = []
    for beta in (1.5, 2.0, 2.5):
        for gam in (0.002, 0.005, 0.01, 0.02, 0.05, 0.1):
            for kappa in (0.5, 0.8, 0.9):
                lam = 40.0 * beta / (100.0 ** beta)
                o = SI(beta, lam, gam, ages)
                H = o.horizon(kappa)
                H1 = (beta + 1.0) * (1.0 - kappa) / gam
                if not math.isfinite(H) or H <= 0:
                    continue
                rel = abs(H1 - H) / H
                rows.append(dict(beta=beta, gam=gam, kappa=kappa, H=H,
                                 H1=H1, rel=rel, x=gam * H1))
    P("  %-6s %-8s %-6s %9s %9s %9s %9s" % ("β", "γ", "κ", "H", "H₁", "γH₁", "rel.err"))
    for r in rows[:18]:
        P("  %-6.2f %-8.3f %-6.1f %9.2f %9.2f %9.3f %9.3f"
          % (r["beta"], r["gam"], r["kappa"], r["H"], r["H1"], r["x"], r["rel"]))
    # 找满足 rel <= 0.10 的 γH₁ 最大范围
    ok = [r for r in rows if r["rel"] <= 0.10]
    if ok:
        xmax = max(r["x"] for r in ok)
        nok = len(ok)
    else:
        xmax, nok = 0.0, 0
    P("  ⇒ rel.err ≤ 10%% 的 %d / %d 行；这些行的最大 γH₁ = %.3f"
      % (nok, len(rows), xmax))
    thr = None
    for cand in (0.05, 0.1, 0.2, 0.5, 1.0, 2.0):
        sub = [r for r in rows if r["x"] <= cand]
        if sub and all(r["rel"] <= 0.10 for r in sub):
            thr = cand
    P("  ⇒ 使「γH₁ ≤ T ⇒ rel.err ≤ 10%%」成立的最大 T = %s"
      % (("%.2f" % thr) if thr else "不存在（一阶式无可靠适用域）"))
    return dict(rows=rows[:40], n_ok=nok, n=len(rows), xmax=float(xmax), thr=thr)


def t2_uniform():
    P("")
    P("=" * 74)
    P("T2 · 视界外的均匀界：|D| ≤ |φ−1|·max(1, 1/φ)")
    P("=" * 74)
    P("  （对 R23 命题 3 的界 |D| ≤ |φ−1|·max{(1−p)/φ, p} 取 sup_{p∈[0,1]}）")
    P("  sup_p max{(1−p)/φ, p} = max(1/φ, 1)  （两线性函数在 p*=1/(1+φ) 处相交）")
    ages = np.arange(0.5, 120.001, 0.5)
    worst = -np.inf
    best = 0.0
    n = 0
    for beta in (1.5, 2.0, 2.5):
        for lam in (1e-5, 1e-4, 1e-3):
            for r0 in (0.005, 0.02, 0.05):
                for s in (1.0, 2.0, 5.0, 20.0):
                    for phi in (0.5, 0.8, 1.5, 3.0, 8.0):
                        n += 1
                        # 直接构造 p 的界与模型可达 |D| 的比较
                        # 用 R23 的 D 需完整两状态模型；此处核验界本身对 p 的 sup
                        bnd = abs(phi - 1.0) * max(1.0 / phi, 1.0)
                        # 模型流形上 p 的实际范围由 SN,SB 决定 → 用 SI 版替代
                        gam = r0 * (s - 1.0)
                        o = SI(beta, lam, gam, ages)
                        # p = SB/(SN+SB)；SB/SN = (F/(1-F)) * S_I * e^{-(s-1) r0 a}
                        F = 1.0 - np.exp(-Lam(ages, lam, beta))
                        SN = np.exp(-Lam(ages, lam, beta)) * np.exp(-r0 * ages)
                        SB = (F * o.SI) * SN * 1.0  # S_B = F*S_I 相对 SN 的不移除部分
                        SB = SB * np.exp(-r0 * (s - 1.0) * ages)
                        p = SB / np.maximum(SN + SB, 1e-300)
                        q = F
                        D = (phi - 1.0) * (p - q) / (1.0 + (phi - 1.0) * q)
                        m = np.isfinite(D) & np.isfinite(p)
                        if np.any(m):
                            worst = max(worst, float(np.max(np.abs(D[m]) - bnd)))
                            best = max(best, float(np.max(np.abs(D[m])) / bnd))
    P("  %d 组合：max(|D| − 界) = %.4e（应 ≤ 0）" % (n, worst))
    P("  max |D|/界 = %.4f（模型流形上的经验上确界比）" % best)
    ok = (worst <= 0.0)
    P("  ⇒ 均匀界 %s" % ("通过" if ok else "未通过"))
    return dict(n=n, worst=float(worst), best_ratio=float(best), ok=bool(ok))


def calib_kitchener():
    P("")
    P("=" * 74)
    P("T1K · Kitchener 标定（用 a91 修复后的逐龄保留率）")
    P("=" * 74)
    # a91 S3 修复后：B 态暴露保留率 0.7848；逐龄保留序列
    ret_obs = np.array([1.00, 0.61, 0.62, 0.62, 0.64, 0.67, 0.58, 0.58,
                        0.59, 0.73, 0.74, 0.67, 0.67, 0.75])
    ages_obs = np.arange(1, 15)
    agg = 0.7848
    rows = []
    for beta in (1.5, 2.0, 2.5, 2.907):
        # λ 使 Λ(28) = 32/8272（观测首次失效累积）
        lam = (32.0 / 8272.0) * beta / (28.0 ** beta)
        best = None
        for gam in np.linspace(0.001, 0.30, 600):
            o = SI(beta, lam, gam, ages_obs.astype(float))
            mae = float(np.mean(np.abs(o.SI - ret_obs)))
            if best is None or mae < best[1]:
                best = (gam, mae)
        gam, mae = best
        ages_f = np.arange(0.5, 250.001, 0.25)
        o2 = SI(beta, lam, gam, ages_f)
        rows.append(dict(beta=beta, gam=float(gam), mae=float(mae),
                         H05=float(o2.horizon(0.5)), H02=float(o2.horizon(0.2)),
                         H08=float(o2.horizon(0.8))))
        P("  β=%.3f ⇒ γ̂=%.4f /yr  MAE=%.3f  H(0.5)=%.1f  H(0.2)=%.1f  H(0.8)=%.1f"
          % (beta, gam, mae, rows[-1]["H05"], rows[-1]["H02"], rows[-1]["H08"]))
    P("")
    P("  对照：观察窗口 W = 28 yr（1997–2025）")
    for r in rows:
        P("    β=%.3f：H(0.5)=%.1f %s W ⇒ %s 主导"
          % (r["beta"], r["H05"], ">" if r["H05"] > 28 else "<",
             "选择性移除" if r["H05"] < 28 else "观察窗口"))
    return dict(rows=rows, agg=agg, W=28.0)


def main():
    res = dict(probe="a93_verify")
    res["t1_props"] = t1_props()
    res["t1_horizon_mono"] = t1_horizon_mono()
    res["t1_first_order"] = t1_first_order()
    res["t2_uniform"] = t2_uniform()
    res["calib"] = calib_kitchener()
    with open(os.path.join(OUT, "a93_verify.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    with open(os.path.join(OUT, "a93_log.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(LOG))
    P("")
    P("[written] a93_verify.json / a93_log.txt")


if __name__ == "__main__":
    main()
