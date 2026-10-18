"""Figures for "How much evidence can a simulator leave?".

Every figure is computed from the simulation-theory repository (this script
lives in paper/<slug>/ and imports ../../src) using its own modules and committed data. Exact repository
routines are used where they are cheap; numpy float re-computations (power
curves, the CHSH covariance ellipse, the Wald-floor curve) are cross-checked
against the repository's exact values or receipt numbers by assertions below,
so a drifting figure fails loudly.

Run:  OMP_NUM_THREADS=1 .venv/bin/python figures.py
"""

from __future__ import annotations

import math
import os
import sys
from decimal import Decimal
from fractions import Fraction as Fr
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "src"))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Circle, Ellipse, Polygon, Rectangle  # noqa: E402

from simtheory import bell_disk_zonoid as zon  # noqa: E402
from simtheory import bell_escape_routes as esc  # noqa: E402
from simtheory import evidence_scaling as es  # noqa: E402
from simtheory import finite_precision_renderers as fpr  # noqa: E402
from simtheory import real_data as rd  # noqa: E402

OUT = HERE / "figures"
OUT.mkdir(exist_ok=True)

# --------------------------------------------------------------------------- style
INK = "#1d232b"
INK2 = "#52514e"
MUTED = "#8b8f96"
GRID = "#e6e4df"
BLUE = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"
VIOLET = "#4a3aa7"
RED = "#e34948"
BAND = "#dbe7f6"
WARM_BAND = "#fbe3d8"

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["cmr10"],
    "mathtext.fontset": "cm",
    "axes.formatter.use_mathtext": True,
    "axes.unicode_minus": False,
    "font.size": 8.5,
    "axes.labelsize": 8.5,
    "axes.titlesize": 9,
    "xtick.labelsize": 7.5,
    "ytick.labelsize": 7.5,
    "legend.fontsize": 7.2,
    "axes.edgecolor": INK2,
    "axes.labelcolor": INK,
    "xtick.color": INK2,
    "ytick.color": INK2,
    "axes.linewidth": 0.6,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "xtick.minor.width": 0.4,
    "ytick.minor.width": 0.4,
    "xtick.major.size": 3,
    "ytick.major.size": 3,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.5,
    "legend.frameon": False,
    "lines.linewidth": 1.4,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.03,
    "pdf.fonttype": 42,
})

W_FULL = 6.6  # inches, text width of the Typst layout


def panel_label(ax, text, x=-0.13, y=1.04):
    ax.text(x, y, text, transform=ax.transAxes, fontsize=9.5, family="cmb10", color=INK, va="bottom")


def save(fig, name):
    fig.savefig(OUT / f"{name}.pdf")
    fig.savefig(OUT / f"{name}.svg")
    plt.close(fig)
    print("wrote", name)


# --------------------------------------------------------------------------- shared math
def lgam(x):
    return np.array([math.lgamma(v) for v in np.atleast_1d(x)], dtype=float)


def log_comb(n, k):
    k = np.asarray(k, dtype=float)
    return math.lgamma(n + 1) - lgam(k + 1) - lgam(n - k + 1)


def log_bf_table(n):
    """ln BF_n(k), k = 0..n, for the KT (Jeffreys) mixture against fair bits (float)."""
    k = np.arange(n + 1, dtype=float)
    # BF_n(k) = C(2k,k) C(2n-2k,n-k) / (2^n C(n,k))  (evidence-scaling-dichotomy, Setting)
    log_c2k = lgam(2 * k + 1) - 2 * lgam(k + 1)
    log_c2nk = lgam(2 * (n - k) + 1) - 2 * lgam(n - k + 1)
    return log_c2k + log_c2nk - n * math.log(2) - log_comb(n, k)


def binom_logpmf(n, q):
    k = np.arange(n + 1, dtype=float)
    return log_comb(n, k) + k * math.log(q) + (n - k) * math.log1p(-q)


def kl_half(p):
    p = np.asarray(p, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        t = np.where(p > 0, p * np.log(2 * p), 0.0) + np.where(p < 1, (1 - p) * np.log(2 * (1 - p)), 0.0)
    return t


def d_bern(p, q):
    return p * math.log(p / q) + (1 - p) * math.log((1 - p) / (1 - q))


def expected_log_bf(n, q):
    if q == 0:
        return float(log_bf_table(n)[0])
    return float(np.sum(np.exp(binom_logpmf(n, q)) * log_bf_table(n)))


C_INT = 0.5 * math.log(2 * math.e / math.pi)  # 0.274209..., ST-T274
C_UP = 1 - 0.5 * math.log(math.pi / 2)  # 0.7742, ST-T273


# =========================================================================== Fig 1
def fig_evidence():
    # Cross-check the float routine against the repository's exact 60-digit value.
    with es.precise():
        exact = float(es.expected_log_bf(128, Fr(1, 4)))
    assert abs(exact - expected_log_bf(128, 0.25)) < 1e-9, (exact, expected_log_bf(128, 0.25))

    ns = np.unique(np.round(np.logspace(0, 4, 70)).astype(int))
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(W_FULL, 2.75), gridspec_kw={"wspace": 0.3})

    # (a) the additive constant E_q[ln BF_n] - n KL(q || 1/2) + (1/2) ln n.
    ax1.axhspan(-math.log(2), C_UP, color=BAND, lw=0)
    ax1.axhline(C_INT, color=INK2, lw=0.8, ls=(0, (4, 2)))
    ax1.axhline(-0.5 * math.log(math.pi), color=MUTED, lw=0.8, ls=(0, (1, 1.5)))
    ax1.text(1.25, C_UP - 0.075, "ST-T273 sandwich, valid for every $n$", color=BLUE, fontsize=6.8, va="top")
    ax1.text(1.25, C_UP + 0.015, r"$1-\frac{1}{2}\ln\frac{\pi}{2}\approx 0.774$ (ST-T273 upper edge)", color=BLUE,
             fontsize=6.8, va="bottom")
    ax1.text(1.25, -math.log(2) - 0.015, r"$-\ln 2$ (ST-T271 lower edge)", color=BLUE, fontsize=6.8, va="top")
    ax1.text(9.5e3, C_INT + 0.035, r"$\frac{1}{2}\ln\frac{2e}{\pi}=0.274$ (ST-T274)", color=INK2, fontsize=6.8,
             ha="right", va="bottom")
    ax1.text(9.5e3, -0.5 * math.log(math.pi) + 0.025, r"$-\frac{1}{2}\ln\pi$ (boundary $q\in\{0,1\}$)", color=INK2,
             fontsize=6.8, ha="right", va="bottom")
    series = [(0.10, BLUE, r"$q=1/10$", (2.3, -0.37)), (0.25, AQUA, r"$q=1/4$", (1.7, 0.4)),
              (0.5, VIOLET, r"$q=1/2$", (1.07, 0.27)), (0.0, ORANGE, r"$q=0$", (40, -0.49))]
    for q, col, lab, (tx, ty) in series:
        ys = np.array([expected_log_bf(int(n), q) - int(n) * float(kl_half(q)) + 0.5 * math.log(n) for n in ns])
        ax1.plot(ns, ys, color=col, lw=1.3)
        ax1.plot([], [], color=col, lw=1.3, label=lab)
    ax1.set_xscale("log")
    ax1.set_xlim(1, 1e4)
    ax1.set_ylim(-0.8, 0.98)
    ax1.legend(loc="center right", bbox_to_anchor=(1.0, 0.36), handlelength=1.6, borderaxespad=0.4)
    ax1.set_xlabel("trials $n$")
    ax1.set_ylabel(r"$\mathbb{E}_q[\ln \mathrm{BF}_n]-n\,\mathrm{KL}(q\|\frac{1}{2})+\frac{1}{2}\ln n$")
    ax1.set_title("Per-world law differs", loc="left", color=INK)
    panel_label(ax1, "a", x=-0.16)

    # (b) one persistent latent draw: transcript KL saturates at KL(a || b).
    third = Fr(1, 3)
    rows_bin = [[1 - third, third], [third, 1 - third]]
    a_bin, b_bin = [Fr(3, 4), Fr(1, 4)], [Fr(1, 4), Fr(3, 4)]
    a3, b3 = [Fr(1, 2), Fr(1, 3), Fr(1, 6)], [Fr(1, 6), Fr(1, 3), Fr(1, 2)]
    rows_nid = [[Fr(3, 4), Fr(1, 4)], [Fr(3, 4), Fr(1, 4)], [Fr(1, 4), Fr(3, 4)]]
    rows_kb = [[Fr(3, 5), Fr(2, 5)], [Fr(2, 5), Fr(3, 5)]]  # theta^b = (2/5, 3/5)
    Ts = [1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256]
    curves = {"bin": [], "nid": [], "ker": []}
    with es.precise():
        cap_bin = float(es.kl_vector(a_bin, b_bin))
        cap_nid = float(es.kl_vector(a3, b3))
        merged = float(es.kl_vector([a3[0] + a3[1], a3[2]], [b3[0] + b3[1], b3[2]]))
        within = float(es.bernoulli_kl(Fr(1, 3), Fr(2, 5)))
        for T in Ts:
            curves["bin"].append(float(es.persistent_audit(a_bin, b_bin, rows_bin, rows_bin, T)["kl_t"]))
            curves["nid"].append(float(es.persistent_audit(a3, b3, rows_nid, rows_nid, T)["kl_t"]))
            curves["ker"].append(float(es.persistent_audit(a_bin, b_bin, rows_bin, rows_kb, T)["kl_t"]))
    # receipt anchors (ST-F55 / ST-T280)
    assert abs(curves["bin"][Ts.index(64)] - 0.544045) < 5e-6
    assert abs(curves["nid"][Ts.index(64)] - 0.242579) < 5e-6
    assert abs(curves["ker"][Ts.index(256)] - 2.972728) < 5e-6
    Ts_a = np.array(Ts)
    ax2.axhline(cap_bin, color=BLUE, lw=0.8, ls=(0, (4, 2)))
    ax2.axhline(cap_nid, color=ORANGE, lw=0.8, ls=(0, (4, 2)))
    ax2.axhline(merged, color=ORANGE, lw=0.6, ls=(0, (1, 1.5)))
    ax2.plot(Ts_a, cap_bin + Ts_a * within, color=AQUA, lw=0.8, ls=(0, (1, 1.5)), label="ST-T280 bound")
    ax2.plot(Ts_a, curves["ker"], color=AQUA, marker="o", ms=2.6, lw=1.3, label="different kernels")
    ax2.plot(Ts_a, curves["bin"], color=BLUE, marker="o", ms=2.6, lw=1.3, label="binary latent")
    ax2.plot(Ts_a, curves["nid"], color=ORANGE, marker="o", ms=2.6, lw=1.3, label="two identical components")
    hs, ls_ = ax2.get_legend_handles_labels()
    order = [2, 3, 1, 0]
    ax2.legend([hs[i] for i in order], [ls_[i] for i in order], loc="upper left", handlelength=1.8,
               borderaxespad=0.3, labelspacing=0.3)
    # values of the dashed and dotted reference lines, in the right margin
    from matplotlib.transforms import blended_transform_factory
    tr = blended_transform_factory(ax2.transAxes, ax2.transData)
    ax2.text(1.02, cap_bin, r"cap $\mathrm{KL}(a\|b)$" + "\n" + r"$=0.549$", transform=tr, color=BLUE, fontsize=6.6,
             va="center", ha="left", clip_on=False)
    ax2.text(1.02, cap_nid, "cap\n$0.366$", transform=tr, color=ORANGE, fontsize=6.6, va="center", ha="left",
             clip_on=False)
    ax2.text(1.02, merged, "merged\n$0.243$", transform=tr, color=ORANGE, fontsize=6.6, va="center",
             ha="left", clip_on=False)
    ax2.annotate(r"$\to 2.97$ at $T=256$", xy=(84, 1.24), xytext=(150, 1.06), fontsize=6.6, color=AQUA,
                 ha="center", arrowprops=dict(arrowstyle="->", color=AQUA, lw=0.5))
    ax2.set_xscale("log")
    ax2.set_xlim(1, 256)
    ax2.set_ylim(0, 1.25)
    ax2.set_xlabel("transcript length $T$ (one world draw)")
    ax2.set_ylabel(r"$\mathrm{KL}(P_a^{Y}\,\|\,P_b^{Y})$  (nats)")
    ax2.set_title("Only world weights differ", loc="left", color=INK)
    panel_label(ax2, "b", x=-0.16)
    save(fig, "fig_evidence")


# =========================================================================== Fig 2
def fig_beacon():
    _, pulses = rd.load_beacon_summary()
    bits = rd.beacon_bits(pulses[:256])
    n_all = len(bits)
    assert n_all == 131072 and sum(bits) == 65461
    path = np.array(rd.kt_log_bayes_factor_path(bits))
    ks = np.cumsum(bits)
    ns = np.arange(1, n_all + 1)
    qhat = ks / ns
    nkl = ns * kl_half(qhat)
    lower = nkl - 0.5 * np.log(ns) - math.log(2)
    upper = nkl - 0.5 * np.log(ns) - 0.5 * math.log(math.pi / 2)
    assert np.all(path >= lower - 1e-7) and np.all(path <= upper + 1e-7)  # ST-T272 on real data
    assert abs(path[-1] - (-6.031714)) < 1e-5

    idx = np.unique(np.round(np.logspace(0, math.log10(n_all), 2500)).astype(int)) - 1
    fig, (ax1, axr, ax2) = plt.subplots(1, 3, figsize=(W_FULL, 2.7),
                                        gridspec_kw={"wspace": 0.48, "width_ratios": [1.0, 0.85, 1.4]})
    ax1.plot(ns[idx], path[idx], color=BLUE, lw=0.9, label=r"$\ln\mathrm{BF}_n$, beacon bits")
    ax1.plot(ns[idx], -0.5 * np.log(ns[idx]) + C_INT, color=INK2, lw=0.9, ls=(0, (4, 2)),
             label=r"fair-bit asymptote")
    ax1.axhline(math.log(100), color=RED, lw=0.9)
    ax1.text(1.3, math.log(100) + 0.25, r"Ville threshold $\ln 100$", color=INK2, fontsize=6.8)
    ax1.annotate(r"$-6.03$", xy=(n_all, path[-1]), xytext=(4e3, -8.6), fontsize=6.8, color=INK2,
                 arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    ax1.set_xscale("log")
    ax1.set_xlim(1, n_all * 1.3)
    ax1.set_xticks([1, 1e2, 1e4])
    ax1.set_ylim(-9.5, 6.5)
    ax1.set_xlabel("bits $n$")
    ax1.set_ylabel(r"$\ln \mathrm{BF}_n$ (nats)")
    ax1.legend(loc="upper right", bbox_to_anchor=(1.0, 0.86), handlelength=1.6, borderaxespad=0.2, fontsize=6.6)
    ax1.set_title("No rejection (ST-F52)", loc="left", color=INK, pad=30)
    panel_label(ax1, "a", x=-0.3, y=1.19)

    # (b) the regret residual, which ST-T272 confines to a fixed band for every sequence
    resid = path - nkl + 0.5 * np.log(ns)
    assert np.all(resid >= -math.log(2) - 1e-7) and np.all(resid <= -0.5 * math.log(math.pi / 2) + 1e-7)
    assert 0 < -0.5 * math.log(math.pi / 2) - resid[-1] < 3e-6  # within 2e-6 of the upper end (ST-F53 box)
    axr.axhspan(-math.log(2), -0.5 * math.log(math.pi / 2), color=BAND, lw=0)
    axr.plot(ns[idx], resid[idx], color=BLUE, lw=0.8)
    axr.text(1.4, -0.5 * math.log(math.pi / 2) + 0.012, r"$-\frac{1}{2}\ln\frac{\pi}{2}$", color=BLUE, fontsize=6.8,
             va="bottom")
    axr.text(1.4, -math.log(2) - 0.012, r"$-\ln 2$", color=BLUE, fontsize=6.8, va="top")
    axr.text(0.97, 0.5, "holds for\nevery sequence", transform=axr.transAxes, color=INK2, fontsize=6.6,
             ha="right", va="center")
    axr.set_xscale("log")
    axr.set_xlim(1, n_all * 1.3)
    axr.set_xticks([1, 1e2, 1e4])
    axr.set_ylim(-0.78, -0.14)
    axr.set_xlabel("bits $n$")
    axr.set_ylabel("regret residual (nats)")
    axr.set_title("Check (ST-T272)", loc="left", color=INK, pad=30)
    panel_label(axr, "b", x=-0.36, y=1.19)

    # (b) exact fixed-n power curves at n = 131072, alpha = 1/100.
    n = n_all
    lbf = log_bf_table(n)
    k = np.arange(n + 1)
    reject = lbf >= math.log(100)
    j = int(np.min(np.abs(k[reject] - n / 2)))
    assert j == 839, j  # receipt: reject iff |k - n/2| >= 839
    lp0 = binom_logpmf(n, 0.5)
    p0 = np.exp(lp0 - lp0.max()) / np.exp(lp0 - lp0.max()).sum()
    tail = np.cumsum(p0[::-1])[::-1]  # P0(K >= c)
    c = int(np.argmax(tail <= 0.01))
    gamma = (0.01 - tail[c]) / p0[c - 1]

    def powers(q):
        lp = binom_logpmf(n, q)
        p = np.exp(lp - lp.max())
        p /= p.sum()
        kt = p[np.abs(k - n / 2) >= j].sum()
        np_ = p[c:].sum() + gamma * p[c - 1]
        return kt, np_

    deltas = np.linspace(0, 0.0145, 160)
    pk, pn = np.array([powers(0.5 + d) for d in deltas]).T
    kappa = 0.1  # BSC(1/10) seen through, ST-M84
    pkf = np.array([powers(0.5 + (1 - 2 * kappa) * d)[0] for d in deltas])
    # receipt brackets
    assert powers(0.5 + 1136 / n)[0] < 0.95 < powers(0.5 + 1137 / n)[0]
    assert powers(0.5 + 718 / n)[1] < 0.95 < powers(0.5 + 719 / n)[1]
    ax2.axhspan(0, 0.95, xmin=0, xmax=0.002011 / 0.0145, color=WARM_BAND, lw=0)
    ax2.plot(deltas, pn, color=AQUA, lw=1.4, label="NP (optimal)")
    ax2.plot(deltas, pk, color=BLUE, lw=1.4, label=r"KT, $\mathrm{BF}_n\geq 100$")
    ax2.plot(deltas, pkf, color=BLUE, lw=1.1, ls=(0, (4, 2)), label=r"KT via BSC($\kappa=1/10$)")
    ax2.axhline(0.95, color=MUTED, lw=0.6)
    marks = [(0.002011, "converse\n0.0020"), (0.005482, "NP\n0.0055"), (0.008671, "KT\n0.0087"),
             (0.009914, "closed form\n0.0099")]
    for (x, lab), ha in zip(marks, ["right", "right", "right", "left"]):
        ax2.axvline(x, color=INK2, lw=0.5, ls=(0, (1, 1.5)))
        ax2.text(x + {"center": 0, "right": -0.0001, "left": 0.0001}[ha], 1.035, lab, fontsize=6.4, color=INK2,
                 va="bottom", ha=ha, clip_on=False, linespacing=1.0)
    ax2.set_xlim(0, 0.0145)
    ax2.set_ylim(0, 1.02)
    ax2.set_xticks([0, 0.005, 0.01])
    ax2.set_xticklabels(["0", "0.005", "0.010"])
    ax2.set_xlabel(r"simulator bias $|q-1/2|$")
    ax2.set_ylabel(r"power, $n=131072$, $\alpha=0.01$")
    ax2.legend(loc="lower right", handlelength=1.4, borderaxespad=0.3, frameon=True, facecolor="white",
               edgecolor="none", framealpha=1.0, fontsize=6.4)
    ax2.set_title("Power (ST-F54)", loc="left", color=INK, pad=30)
    panel_label(ax2, "c", x=-0.3, y=1.19)
    save(fig, "fig_beacon")


# =========================================================================== Fig 3
def fig_chsh_disk():
    _, trials = rd.load_delft_summary()
    s = rd.chsh_summary(trials)
    x0, y0 = rd.canonical_disk_point(s.correlations)
    assert abs(s.s_value - 2.422) < 5e-4 and abs(s.s_error - 0.204) < 5e-4
    assert abs(x0 - 0.856) < 5e-4 and abs(y0 + 0.094) < 5e-4
    # covariance of (x, y) under the same per-setting binomial error model as S +- 0.204
    var = np.array(s.correlation_errors) ** 2
    sx = np.array([1, 1, 1, -1])
    sy = np.array([-1, 1, 1, 1])
    cov = np.array([[np.sum(var), np.sum(sx * sy * var)], [np.sum(sx * sy * var), np.sum(var)]]) / 8
    assert abs(math.sqrt(cov[0, 0]) - s.s_error / (2 * math.sqrt(2))) < 1e-12
    evals, evecs = np.linalg.eigh(cov)
    ang = math.degrees(math.atan2(evecs[1, 1], evecs[0, 1]))

    r = 1 / math.sqrt(2)
    xw = 5 * math.sqrt(2) / 8
    th = np.linspace(-math.acos(r), math.acos(r), 300)
    cap = np.column_stack([np.concatenate([[r], np.cos(th), [r]]),
                           np.concatenate([[-math.sqrt(1 - r * r)], np.sin(th), [math.sqrt(1 - r * r)]])])
    fig, (ax, az) = plt.subplots(1, 2, figsize=(W_FULL, 3.2), gridspec_kw={"wspace": 0.3, "width_ratios": [1, 1]})
    zx, zy = (0.47, 1.03), (-0.33, 0.21)
    for a in (ax, az):
        a.set_aspect("equal")
        a.grid(False)
        a.add_patch(Polygon(cap, closed=True, color=WARM_BAND, lw=0, zorder=0))
        a.add_patch(Circle((0, 0), 1, fill=False, ec=INK, lw=1.0, zorder=2))
        a.plot([r, r], [-r, r], color=ORANGE, lw=1.3, zorder=3)
        for k_sig, alpha_ in ((2, 0.16), (1, 0.30)):
            a.add_patch(Ellipse((x0, y0), 2 * k_sig * math.sqrt(evals[1]), 2 * k_sig * math.sqrt(evals[0]),
                                angle=ang, color=BLUE, alpha=alpha_, lw=0, zorder=4))
        a.plot([x0], [y0], "o", color=BLUE, ms=4.5, mec="white", mew=0.8, zorder=6)
        a.plot([1], [0], marker="*", color=VIOLET, ms=9, mec="white", mew=0.6, zorder=6, clip_on=False)
        a.plot([xw], [0], marker="D", color=AQUA, ms=4.2, mec="white", mew=0.6, zorder=6)
    # full disk
    ax.add_patch(Rectangle((-r, -r), 2 * r, 2 * r, fill=False, ec=MUTED, lw=0.6, ls=(0, (3, 2)), zorder=1))
    ax.add_patch(Rectangle((zx[0], zy[0]), zx[1] - zx[0], zy[1] - zy[0], fill=False, ec=INK2, lw=0.6, zorder=7))
    ax.plot([0], [0], "+", color=MUTED, ms=5, mew=0.7)
    ax.text(0.0, 0.1, "visibility-phase\nquantum family\n$\\|z\\|_2\\leq 1$", ha="center", fontsize=7, color=INK2)
    ax.text(-0.69, -0.68, r"inscribed square (ST-T13)", fontsize=6.4, color=MUTED, va="bottom")
    ax.text(r - 0.04, 0.45, "$S=2$", color=ORANGE, fontsize=7.2, ha="right", va="center")
    ax.set_xlim(-1.08, 1.08)
    ax.set_ylim(-1.08, 1.08)
    ax.set_xlabel(r"$x=v\cos\phi$")
    ax.set_ylabel(r"$y=v\sin\phi$")
    ax.set_xticks([-1, 0, r, 1])
    ax.set_xticklabels(["$-1$", "$0$", r"$\frac{1}{\sqrt{2}}$", "$1$"])
    ax.set_yticks([-1, 0, 1])
    ax.set_anchor("S")
    az.set_anchor("S")
    panel_label(ax, "a", x=-0.2, y=1.13)
    # zoom
    yb = -0.27
    az.annotate("", xy=(r, yb), xytext=(x0, yb), arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.6, shrinkA=0, shrinkB=0))
    az.plot([x0, x0], [y0, yb], color=INK2, lw=0.4, ls=(0, (1, 1.5)))
    az.text(r + 0.006, yb - 0.012, r"$\mathrm{TV}=\frac{S-2}{8}=0.053$", ha="left", va="top",
            fontsize=7, color=INK2)
    az.text(r - 0.01, 0.13, "local bound\n$S=2$ (chord)", color=ORANGE, fontsize=7, ha="right", va="center")
    az.annotate("Tsirelson\n$S=2\\sqrt{2}$", xy=(1, 0), xytext=(1.045, 0.075), fontsize=7, color=VIOLET,
                ha="left", va="center", annotation_clip=False,
                arrowprops=dict(arrowstyle="-", color=VIOLET, lw=0.5, shrinkB=5))
    az.annotate("Delft 2015\n$z=(0.856,-0.094)$", xy=(x0, y0), xytext=(0.595, -0.035), fontsize=7,
                color=BLUE, ha="center", arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.5, shrinkB=4))
    az.annotate("$D=32$ grid law,\nexactly Werner\n(ST-T287)", xy=(xw, 0), xytext=(0.80, 0.12), va="center",
                fontsize=7, color=AQUA, ha="center", arrowprops=dict(arrowstyle="-", color=AQUA, lw=0.5, shrinkB=4))
    az.text(0.49, -0.20, "$1\\sigma$, $2\\sigma$ regions\n(per-setting\nbinomial errors)", color=BLUE,
            fontsize=6.6, va="center")
    az.set_xlim(*zx)
    az.set_ylim(*zy)
    az.set_xlabel(r"$x=v\cos\phi$")
    az.set_xticks([0.5, 0.6, r, 0.8, 0.9, 1.0])
    az.set_xticklabels(["$0.5$", "$0.6$", r"$\frac{1}{\sqrt{2}}$", "$0.8$", "$0.9$", "$1$"])
    az.set_yticks([-0.3, -0.2, -0.1, 0, 0.1, 0.2])
    sec = az.secondary_xaxis("top", functions=(lambda u: 2 * math.sqrt(2) * u, lambda t: t / (2 * math.sqrt(2))))
    sec.set_xticks([1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8])
    sec.set_xlabel(r"$S=2\sqrt{2}\,x$", fontsize=7.5)
    sec.tick_params(labelsize=7)
    for sp in ("top", "right"):
        az.spines[sp].set_visible(True)
    panel_label(az, "b", x=-0.13, y=1.13)
    save(fig, "fig_chsh_disk")
    return x0, y0


# =========================================================================== Fig 4
def fig_delft_eprocess():
    wins = esc.load_delft()
    assert len(wins) == 245 and sum(wins) == 196
    f34, xi = Fr(3, 4), esc.XI
    pc = esc.prefix_counts(wins)
    mix = np.array([float(esc.uniform_mixture_e_value(k, m, xi)) for k, m in pc])
    fixed = np.array([float(esc.fixed_bet_e_value(k, m, Fr(17, 20), xi)) for k, m in pc])
    ceil = np.array([float(esc.constant_bet_ceiling(k, m, f34)) for k, m in pc])
    # KT plug-in bet path (same rule as esc.plugin_bet_running_sup), cross-checked on its supremum
    kt_path, value, kk, nn = [], Fr(1), 0, 0
    for w in wins:
        q = max(xi, min(Fr(1), Fr(2 * kk + 1, 2 * nn + 2)))
        value *= esc.bet_factor(q, xi, w)
        kt_path.append(float(value))
        kk += w
        nn += 1
    assert abs(max(max(kt_path), 1.0) - float(esc.plugin_bet_running_sup(wins, xi, "kt"))) < 1e-12
    assert abs(mix.max() - 2.781599) < 1e-5 and int(np.argmax(mix)) + 1 == 6
    assert abs(ceil.max() - 7.779688) < 1e-5 and int(np.argmax(ceil)) + 1 == 241
    p_fixed = rd.binomial_upper_tail(196, 245, float(xi))
    assert abs(p_fixed - 0.039175) < 1e-5

    n = np.arange(1, 246)
    fig, ax = plt.subplots(figsize=(W_FULL, 2.85))
    ax.fill_between(n, 1, ceil, color=BAND, lw=0, step="post", label=r"realized ceiling $C_n(3/4)$ (every constant-bet mixture)")
    ax.step(n, ceil, where="post", color=BLUE, lw=0.6, alpha=0.7)
    ax.plot(n, mix, color=BLUE, lw=1.4, label=r"uniform mixture on $[\xi,1]$ (anytime $p=0.36$)")
    ax.plot(n, kt_path, color=AQUA, lw=1.1, label="predictable KT plug-in bet (exploration only)")
    ax.plot(n, fixed, color=VIOLET, lw=1.0, ls=(0, (4, 2)), label=r"fixed bet $u=17/20$")
    ax.axhline(20, color=RED, lw=1.0)
    ax.text(3, 21.8, r"Ville threshold $1/\alpha=20$", color=INK2, fontsize=7)
    ax.plot([245], [1 / p_fixed], marker="s", color=ORANGE, ms=4.5, mec="white", mew=0.6, clip_on=False, zorder=5)
    ax.annotate(r"fixed-$n$ $1/p=25.5$ (not an anytime e-value)", xy=(245, 1 / p_fixed),
                xytext=(236, 36), fontsize=7, color=ORANGE, ha="right",
                arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.5, shrinkB=3))
    ax.annotate(r"max $7.78$ at $n=241$", xy=(241, ceil[240]), xytext=(196, 11.5), fontsize=7, color=BLUE,
                ha="center", arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.5, shrinkB=2))
    ax.set_yscale("log")
    ax.set_ylim(0.08, 60)
    ax.set_xlim(1, 249)
    ax.set_yticks([0.1, 0.3, 1, 3, 10, 20, 50])
    ax.set_yticklabels(["0.1", "0.3", "1", "3", "10", "20", "50"])
    ax.set_xlabel("Delft 2015 valid trial $n$ (timestamp order)")
    ax.set_ylabel(r"e-value $E_n$ (win indicator)")
    ax.legend(loc="lower left", bbox_to_anchor=(0.0, 1.01), ncol=2, handlelength=1.8, borderaxespad=0.0, columnspacing=1.5)
    save(fig, "fig_delft_eprocess")


# =========================================================================== Fig 5
def fig_frontiers():
    xi = float(esc.XI)
    w_ts = math.cos(math.pi / 8) ** 2
    se = math.sqrt(0.8 * 0.2 / 245)
    fig, (ax1, axd, ax2) = plt.subplots(1, 3, figsize=(W_FULL, 2.55),
                                        gridspec_kw={"wspace": 0.5, "width_ratios": [1.1, 0.8, 1.15]})

    def refs(ax, xr, labels):
        ax.axhline(0.75, color=MUTED, lw=0.7)
        ax.axhline(w_ts, color=INK2, lw=0.7, ls=(0, (1, 1.5)))
        ax.axhspan(0.8 - se, 0.8 + se, color=WARM_BAND, lw=0)
        ax.axhline(0.8, color=ORANGE, lw=0.9)
        if labels:
            ax.text(xr, 0.8 + 0.004, r"Delft $\hat w=0.80\pm$s.e.", color=ORANGE, fontsize=6.6, ha="right", va="bottom")
            ax.text(xr, w_ts + 0.003, r"Tsirelson $0.854$", color=INK2, fontsize=6.6, ha="right", va="bottom")
            ax.text(xr, 0.75 + 0.003, r"local $3/4$", color=MUTED, fontsize=6.6, ha="right", va="bottom")

    c = np.linspace(0, 1, 300)
    refs(ax1, 0.99, True)
    ax1.plot(c, np.minimum(1, 0.75 + c / 2), color=BLUE, lw=1.4, label="silence free, $3/4+c/2$")
    ax1.plot(c, 0.75 + c / 4, color=AQUA, lw=1.4, label="send flag, $3/4+c/4$")
    ax1.legend(loc="upper left", handlelength=1.4, borderaxespad=0.05, fontsize=6.6, ncol=1, labelspacing=0.25)
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0.73, 1.09)
    ax1.set_yticks([0.75, 0.8, 0.85, 0.9, 0.95, 1.0])
    ax1.set_xlabel(r"signaling cost $c$")
    ax1.set_ylabel(r"max CHSH win probability $f$")
    ax1.set_title(r"$\mathbf{a}$  Signaling", loc="left", color=INK)

    lv = np.linspace(0, 0.25, 100)
    refs(axd, 0.245, False)
    axd.plot(lv, 1 - lv, color=VIOLET, lw=1.4)
    axd.text(0.14, 0.95, "$1-\\ell$", color=VIOLET, fontsize=6.8)
    axd.set_xlim(0, 0.25)
    axd.set_ylim(0.73, 1.09)
    axd.set_yticks([0.75, 0.8, 0.85, 0.9, 0.95, 1.0])
    axd.set_xticks([0, 0.125, 0.25])
    axd.set_xticklabels(["0", "1/8", "1/4"])
    axd.set_xlabel(r"min setting prob. $\ell$")
    axd.set_title(r"$\mathbf{b}$  Setting dependence", loc="left", color=INK)

    v0 = math.sqrt(2) * (2 * xi - 1)
    v = np.linspace(v0 + 1e-4, 1, 400)
    wv = (1 + v / math.sqrt(2)) / 2
    floor = np.array([math.log(20) / d_bern(w, xi) for w in wv])
    v_delft = (2 * 0.8 - 1) * math.sqrt(2)
    fl_ts = math.log(20) / d_bern(w_ts, xi)
    fl_d = math.log(20) / d_bern(0.8, xi)
    assert abs(fl_ts - 93.5) < 0.05 and abs(fl_d - 428.4) < 0.05
    ax2.fill_between(v, 245, floor, where=floor > 245, color=WARM_BAND, lw=0)
    ax2.plot(v, floor, color=BLUE, lw=1.4)
    ax2.axhline(245, color=ORANGE, lw=0.9)
    ax2.text(0.712, 225, "Delft sample $n=245$", color=ORANGE, fontsize=6.6, ha="left", va="top")
    ax2.plot([1], [fl_ts], "o", color=VIOLET, ms=4, mec="white", mew=0.6, clip_on=False, zorder=5)
    ax2.annotate("93.5 at $v=1$", xy=(1, fl_ts), xytext=(0.93, 35), fontsize=6.6, color=VIOLET, ha="center",
                 arrowprops=dict(arrowstyle="-", color=VIOLET, lw=0.5, shrinkB=3))
    ax2.plot([v_delft], [fl_d], "o", color=ORANGE, ms=4, mec="white", mew=0.6, zorder=5)
    ax2.annotate(r"428.4 at $\hat w=0.8$", xy=(v_delft, fl_d), xytext=(0.90, 2500), fontsize=6.6, color=ORANGE,
                 ha="center", arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.5, shrinkB=3))
    ax2.axvline(1 / math.sqrt(2), color=MUTED, lw=0.6, ls=(0, (1, 1.5)))
    ax2.text(0.7125, 13, r"$v=1/\sqrt{2}$", color=INK2, fontsize=7.2, rotation=90, va="bottom")
    ax2.set_yscale("log")
    ax2.set_ylim(10, 1e5)
    ax2.set_xlim(0.70, 1.0)
    ax2.set_xlabel(r"visibility $v$")
    ax2.set_ylabel(r"floor $\ln 20\,/\,\mathrm{KL}(w_v\,\|\,\xi)$ on $\mathbb{E}[T_\alpha]$")
    ax2.set_title(r"$\mathbf{c}$  Wald floor", loc="left", color=INK)
    save(fig, "fig_frontiers")


# =========================================================================== Fig 6
def fig_renderers():
    fig, axes = plt.subplots(1, 3, figsize=(W_FULL, 2.5), gridspec_kw={"wspace": 0.5})
    ax1, ax2, ax3 = axes
    # (a) D-grid correlator lattice vs the Werner segment v (1, 1/sqrt 2)
    D = 16
    ms = np.arange(0, D + 1, 2)
    M1, M2 = np.meshgrid(ms / D, ms / D)
    g, (m1, m2) = fpr.grid_segment_separation(D, Fr(1, 2), Fr(1))
    gf = float(g)
    ax1.set_aspect("equal")
    ax1.grid(False)
    ax1.scatter(M1, M2, s=7, color=INK2, lw=0, zorder=3)
    v = np.linspace(0.5, 1, 50)
    ax1.plot(v, v / math.sqrt(2), color=ORANGE, lw=1.6, zorder=2, solid_capstyle="round")
    ax1.plot([0, 1.0], [0, 1 / math.sqrt(2)], color=ORANGE, lw=0.5, ls=(0, (1, 1.5)), zorder=1)
    ax1.add_patch(Rectangle((m1 / D - gf, m2 / D - gf), 2 * gf, 2 * gf, fill=False, ec=BLUE, lw=0.9, zorder=4))
    ax1.plot([m1 / D], [m2 / D], "o", color=BLUE, ms=3.6, zorder=5)
    wbox = dict(fc="white", ec="none", pad=0.5, alpha=1.0)
    ax1.text(0.21, 0.4375, "Werner segment", color=ORANGE, fontsize=6.4, ha="center", va="center", bbox=wbox, zorder=6)
    # zoom on the closest grid law: the separation box is invisible at full scale
    axin = ax1.inset_axes([0.55, 0.04, 0.42, 0.42])
    cx, cy = m1 / D, m2 / D
    hw = 4 * gf
    vv = np.linspace(cx - hw, cx + hw, 10)
    axin.plot(vv, vv / math.sqrt(2), color=ORANGE, lw=1.4)
    axin.add_patch(Rectangle((cx - gf, cy - gf), 2 * gf, 2 * gf, fill=False, ec=BLUE, lw=0.9))
    axin.plot([cx], [cy], "o", color=BLUE, ms=3.2)
    vg = np.linspace(0.5, 1.0, 200001)
    dist = np.maximum(np.abs(cx - vg), np.abs(cy - vg / math.sqrt(2)))
    vs = vg[int(np.argmin(dist))]
    assert abs(dist.min() - gf) < 1e-5
    axin.plot([vs], [vs / math.sqrt(2)], "o", color=ORANGE, ms=2.6, mec="white", mew=0.4, zorder=5)
    axin.set_xlim(cx - hw, cx + hw)
    axin.set_ylim(cy - hw, cy + hw)
    axin.set_aspect("equal")
    axin.set_xticks([])
    axin.set_yticks([])
    axin.grid(False)
    for sp in axin.spines.values():
        sp.set_visible(True)
        sp.set_color(INK2)
        sp.set_linewidth(0.6)
    axin.text(0.06, 0.94, f"$g_{{{D}}}={gf:.4f}$", transform=axin.transAxes, fontsize=6, ha="left", va="top", color=BLUE)
    ax1.indicate_inset_zoom(axin, edgecolor=INK2, lw=0.5, alpha=0.8)
    ax1.set_xlim(-0.03, 1.05)
    ax1.set_ylim(-0.03, 1.05)
    ax1.set_xticks([0, 0.5, 1])
    ax1.set_yticks([0, 0.5, 1])
    ax1.set_xlabel(r"$\zeta_1$ (setting angle $0$)")
    ax1.set_ylabel(r"$\zeta_2$ (setting angle $\pi/4$)")
    ax1.set_title(f"Grid laws, $D={D}$", loc="left", color=INK)
    panel_label(ax1, "a", x=-0.3)

    # (b) D^2 g_D vs D with the ST-T288 lower bound 1/(3 + 2 sqrt 2)
    Ds = sorted(set(int(4 * round(x / 4)) for x in np.logspace(math.log10(8), math.log10(2048), 34)))
    vals = []
    for d in Ds:
        gd, _ = fpr.grid_segment_separation(d, Fr(1, 2), Fr(1))
        vals.append(float(gd) * d * d)
        assert gd >= fpr.g_lower_bound(d, Fr(1, 2)) - Decimal("1e-60")
    ax2.plot(Ds, vals, "o", color=BLUE, ms=2.8, lw=0)
    ax2.axhline(1 / (3 + 2 * math.sqrt(2)), color=ORANGE, lw=1.0, ls=(0, (4, 2)))
    ax2.text(9, 1 / (3 + 2 * math.sqrt(2)) + 0.07, r"lower bound $1/(3+2\sqrt{2})$", color=ORANGE, fontsize=6.6)
    ax2.set_xscale("log")
    ax2.set_xlim(7, 2400)
    ax2.set_ylim(0, 3.2)
    ax2.set_box_aspect(1)
    ax2.set_xlabel(r"precision $D$ ($4\mid D$)")
    ax2.set_ylabel(r"$D^2\,g_D$")
    ax2.set_title(r"Separation $\Theta(1/D^2)$", loc="left", color=INK)
    panel_label(ax2, "b", x=-0.3)

    # (c) excess polar area A_w - pi^3 of the regular 2-, 3- and 4-direction schedules (ST-T292 to ST-T295)
    styles = [(2, ORANGE, "CHSH\n(2 dir.)"), (3, BLUE, "3 dir."), (4, AQUA, "4 dir.")]
    areas = []
    for m, col, lab in styles:
        sched = zon.regular_schedule_qs(m)
        areas.append(float(zon.polar_area(sched)))
    assert abs(areas[0] - 32) < 1e-9 and abs(areas[1] - 18 * math.sqrt(3)) < 1e-9
    assert abs(areas[2] - (384 * math.sqrt(2) - 512)) < 1e-9
    excess = [a - math.pi ** 3 for a in areas]
    assert all(e > 0 for e in excess)  # ST-T292
    xs = np.arange(len(styles))
    ax3.bar(xs, excess, width=0.6, color=[c for _, c, _ in styles], lw=0)
    for x, a, e in zip(xs, areas, excess):
        ax3.text(x, e + 0.025, f"{a:.3f}", ha="center", va="bottom", fontsize=6.6, color=INK2)
    ax3.set_xticks(xs)
    ax3.set_xticklabels([lab for _, _, lab in styles], fontsize=7)
    ax3.set_xlim(-0.6, len(styles) - 0.4)
    ax3.set_ylim(0, 1.15)
    ax3.grid(axis="x", visible=False)
    ax3.set_ylabel(r"$A_w-\pi^3$")
    ax3.text(0.97, 0.80, r"area $A_w$ above bar;" + "\n" + r"$\pi^3\approx 31.006$", transform=ax3.transAxes,
             ha="right", va="top", fontsize=6.6, color=INK2)
    ax3.set_box_aspect(1)
    ax3.set_title(r"Polar areas above $\pi^3$", loc="left", color=INK)
    panel_label(ax3, "c", x=-0.3)
    save(fig, "fig_renderers")


if __name__ == "__main__":
    which = sys.argv[1:] or ["evidence", "beacon", "disk", "delft", "frontiers", "renderers"]
    table = {"evidence": fig_evidence, "beacon": fig_beacon, "disk": fig_chsh_disk, "delft": fig_delft_eprocess,
             "frontiers": fig_frontiers, "renderers": fig_renderers}
    for w in which:
        table[w]()
