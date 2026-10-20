# -*- coding: utf-8 -*-
"""a95 · 信息存活曲线 S_I(a;gamma) 的数值稳定实现

定义（两状态选择性更换模型）
----------------------------
资产在年龄 u 首次失效后进入「已失效 B」态；B 态以率 s*r0 被移除，
无失效史资产以率 r0 被移除。记 gamma = r0*(s-1) >= 0 为**超额移除强度**。
在年龄 a，B 态暴露相对「无选择性移除」反事实的保留率为

    S_I(a;gamma) = E[ exp(-gamma*(a-U)) | U <= a ],  U~首次失效年龄，密度 f/F

写成 Weibull(lam, beta)（h(a)=lam*a^(beta-1), Lam(a)=lam*a^beta/beta, F=1-exp(-Lam)）：

    M(a) = int_0^a f(u) exp(gamma*u) du ,   S_I = exp(-gamma*a) * M(a)/F(a)

数值关键
--------
直接在 Lambda 空间积分会在 t->0 处遇到 w^(1/beta) 的代数奇点，Simpson 阶数
退化，导致 S_I>1、dS_I/dgamma>0 等解析上不可能的伪违反（a90/a93 即败于此）。

本实现把积分缩放到 [0,1] 并用 Gauss-Jacobi 求积吸收 z^(beta-1) 权重：
    w = z^beta  =>  w^(1/beta) = z,  dw = beta*z^(beta-1)*dz
    M(a) = L*beta * int_0^1 exp(-L*z^beta + gamma*a*z) * z^(beta-1) dz ,  L = Lam(a)
         ~ L*beta * sum_i w_i * exp(-L*z_i^beta + gamma*a*z_i)
    F(a) = 1 - exp(-L)   （解析）

于是
    S_I(a)   = exp(-gamma*a) * L*beta * sum_i w_i exp(E_i) / F
    dS_I/dgamma = exp(-gamma*a) * a * L*beta * sum_i w_i (z_i-1) exp(E_i) / F  <= 0
    E_i = -L*z_i^beta + gamma*a*z_i

由于 z_i in (0,1)、w_i>0，dS_I/dgamma < 0 在**离散层面也严格成立**，
故数值核验检验的是代数推导而非求积误差。溢出用 logsumexp 处理。
"""
import numpy as np
from scipy.special import roots_jacobi, logsumexp

NODES = 160


class SI:
    """S_I(a;gamma) 及其对 gamma 的解析导数。"""

    def __init__(self, beta, lam, gamma, ages, n=NODES):
        self.beta = float(beta)
        self.lam = float(lam)
        self.gam = float(gamma)
        self.ages = np.asarray(ages, dtype=float)
        # Gauss-Jacobi 节点原生在 [-1,1]，权 (1-x)^0 (1+x)^(beta-1)。
        # 变换 z=(x+1)/2 到 [0,1]：
        #   int_0^1 g(z) z^(beta-1) dz = 2^(-beta) * int_{-1}^1 g((x+1)/2)(1+x)^(beta-1) dx
        x, wj = roots_jacobi(n, 0.0, self.beta - 1.0)
        z = 0.5 * (np.asarray(x, dtype=float) + 1.0)
        w = np.asarray(wj, dtype=float) * (2.0 ** (-self.beta))
        keep = w > 0
        self.z = z[keep]
        self.lw = np.log(w[keep])
        self.lz1 = np.log(np.maximum(1.0 - self.z, 1e-300))
        self._build()

    def _build(self):
        a = self.ages
        L = self.lam * np.power(np.maximum(a, 0.0), self.beta) / self.beta
        self.L = L
        # E[i,j] = -L_i * z_j^beta + gamma * a_i * z_j
        zb = np.power(self.z, self.beta)
        E = (-L[:, None] * zb[None, :]
             + (self.gam * a)[:, None] * self.z[None, :])
        self.E = E
        # log M
        lm = np.log(np.maximum(L * self.beta, 1e-300))
        self.logM = lm + logsumexp(self.lw[None, :] + E, axis=1)
        # log |a*(dM/dgamma - a*M)| 的项：log(a*L*beta) + logsumexp(log w + log(1-z) + E)
        self.logMdiff = (np.log(np.maximum(np.abs(a), 1e-300)) + lm) \
            + logsumexp(self.lw[None, :] + self.lz1[None, :] + E, axis=1)
        F = -np.expm1(-L)
        self.F = F
        logF = np.log(np.maximum(F, 1e-300))
        la = -self.gam * a
        self.SI = np.exp(la + self.logM - logF)
        # dS_I/dgamma = -exp(la + logMdiff - logF)  (严格负)
        self.dSI = -np.exp(la + self.logMdiff - logF)
        tiny = ~(F > 0)
        if np.any(tiny):
            self.SI[tiny] = 1.0
            self.dSI[tiny] = 0.0

    def horizon(self, kappa, amax):
        """H(kappa) = sup{ a : inf_{u<=a} S_I(u) >= kappa }（运行下确界定义）。

        S_I 对 a 不必单调（数值上确有少量上升点），故用运行下确界；
        这样由 S_I 对 gamma 逐点递减可直接推出 H 对 gamma 非增。
        未在网格内达到 kappa 时返回 amax（右删）。
        """
        run = np.minimum.accumulate(self.SI)
        ok = run >= kappa
        if not np.any(ok):
            return 0.0
        idx = int(np.max(np.nonzero(ok)[0]))
        a = self.ages
        if idx >= a.size - 1:
            return float(amax)
        r0, r1 = run[idx], run[idx + 1]
        if r1 < r0 - 1e-15:
            t = (r0 - kappa) / max(r0 - r1, 1e-300)
            return float(min(a[idx] + t * (a[idx + 1] - a[idx]), amax))
        return float(min(a[idx], amax))
