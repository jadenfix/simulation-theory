"""Figures for "Identifiability and randomness as resources".

Every number plotted here is computed by the repository's own certificate
modules (src/simtheory/*.py at the repository root, two levels up):

  two_view_fiber      -> fig_fiber_k2, fig_fiber_k3
  evidence_scaling    -> fig_evidence
  random_bit_price    -> fig_bits

Exact (Fraction / 60-digit Decimal) values are used wherever the module
provides them. The non-exact plotted quantities are closed-form curves (the
k = 2 curve cos^2(psi + theta) with its float arc endpoints, and the ST-T273
envelope of fig_evidence (a)) and the illustrative Haar float scan of O(3) in
fig_fiber_k3, which does not certify the k = 3 fiber.

Outcomes are indexed from 1 in every label (the repository indexes from 0).

Run:  OMP_NUM_THREADS=1 .venv/bin/python figures.py
"""

from __future__ import annotations

import math
import os
import sys
from fractions import Fraction as F
from itertools import permutations, product

os.environ.setdefault("OMP_NUM_THREADS", "1")
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "src"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon, FancyArrowPatch, Wedge

from simtheory import two_view_fiber as tv
from simtheory import evidence_scaling as es
from simtheory import random_bit_price as rb

OUT = os.path.join(HERE, "figures")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------------------
# style
# ---------------------------------------------------------------------------

INK = "#1c2230"
BLUE = "#2c5d8f"
LBLUE = "#c9d8e8"
RUST = "#b0502a"
LRUST = "#efd2c4"
GREEN = "#4b7a3d"
GOLD = "#a67c1a"
GRAY = "#8b909a"
LGRAY = "#e4e6ea"

plt.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": ["cmr10", "Computer Modern Roman", "DejaVu Serif"],
        "mathtext.fontset": "cm",
        "axes.formatter.use_mathtext": True,
        "axes.unicode_minus": False,
        "font.size": 8.5,
        "axes.titlesize": 9,
        "axes.labelsize": 8.5,
        "xtick.labelsize": 7.5,
        "ytick.labelsize": 7.5,
        "legend.fontsize": 7.2,
        "axes.linewidth": 0.6,
        "axes.edgecolor": INK,
        "axes.labelcolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "xtick.major.size": 2.8,
        "ytick.major.size": 2.8,
        "xtick.minor.size": 1.6,
        "ytick.minor.size": 1.6,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "legend.frameon": False,
        "lines.linewidth": 1.2,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.02,
        "pdf.fonttype": 42,
        "svg.fonttype": "path",
    }
)


def save(fig, name):
    for ext in ("pdf", "svg"):
        fig.savefig(os.path.join(OUT, f"{name}.{ext}"))
    plt.close(fig)
    print("wrote", name)


def frac_tex(x: F) -> str:
    return rf"\frac{{{x.numerator}}}{{{x.denominator}}}"


# ---------------------------------------------------------------------------
# Figure 1: the k = 2 orthogonal fiber and the sharp identified interval
# (ST-T297, ST-T301, ST-M87)
# ---------------------------------------------------------------------------


def fig_fiber_k2():
    S, K, PI = tv.S2, tv.K2, tv.PI2
    q, T = tv.one_view(PI, K), tv.two_view(PI, K)
    x_star = min(range(3), key=lambda x: K[1][x] / K[0][x])
    L, U, y_star = tv.identified_interval_k2(q, T, x_star)
    assert (L, U) == (F(144, 1825), F(1849, 2425))
    W = tv.mm(tv.diag(S), K)
    cols = [np.array([float(W[0][x]), float(W[1][x])]) for x in range(3)]
    s = np.array([float(S[0]), float(S[1])])
    th_lo, th_hi = tv.float_arc_k2(S, K)
    psi = math.atan2(s[1], s[0])

    # exact rational grid tan(theta/2) = j/200, as in the ST-F59 certificate
    grid = []
    for j in range(-100, 101):
        t = F(j, 200)
        r = tv.fiber_point(S, K, tv.rot2(t))
        if r is not None:
            pip, Kp, _ = r
            assert tv.two_view(pip, Kp) == T
            grid.append((2 * math.atan(float(t)), float(pip[0])))
    witness = tv.fiber_point(S, K, tv.O2)
    assert witness[0] == tv.PI2_PRIME_EXPECTED
    th_w = math.atan2(7, 24)

    fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(6.6, 2.75), gridspec_kw={"width_ratios": [1.0, 1.35], "wspace": 0.32})

    # (a) geometry in the (latent 1, latent 2) plane
    ax = ax0
    ax.set_aspect("equal")
    R = 1.0
    tt = np.linspace(0, math.pi / 2, 200)
    ax.plot(R * np.cos(tt), R * np.sin(tt), color=LGRAY, lw=0.8, zorder=0)
    ang = [math.atan2(c[1], c[0]) for c in cols]

    def cone(theta, fc, ec, alpha, lw, ls="-", z=1):
        a0, a1 = min(ang) + theta, max(ang) + theta
        pts = [(0, 0)] + [(R * math.cos(a), R * math.sin(a)) for a in np.linspace(a0, a1, 60)]
        ax.add_patch(Polygon(pts, closed=True, fc=fc, ec="none", alpha=alpha, lw=0, zorder=z))
        for a in (a0, a1):
            ax.plot([0, R * math.cos(a)], [0, R * math.sin(a)], color=ec, lw=lw, ls=ls, zorder=z + 0.5)

    cone(th_lo, GREEN, GREEN, 0.10, 0.7, (0, (3, 2)), 1)
    cone(th_hi, RUST, RUST, 0.10, 0.7, (0, (3, 2)), 1)
    cone(0.0, BLUE, BLUE, 0.22, 0.8, "-", 2)
    for x, c in enumerate(cols):
        ax.annotate("", xy=c, xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", lw=0.9, color=INK, mutation_scale=7), zorder=4)
        off = {0: (0.0, -0.085), 1: (-0.12, -0.03), 2: (-0.045, 0.035)}[x]
        ax.text(c[0] + off[0], c[1] + off[1], rf"$w_{x + 1}$", fontsize=8, color=INK, zorder=7,
                bbox=dict(boxstyle="square,pad=0.05", fc="white", ec="none", alpha=0.85))
    ax.annotate("", xy=s, xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", lw=1.3, color=BLUE, mutation_scale=8), zorder=5)
    ax.text(s[0] + 0.03, s[1] + 0.01, r"$s=\sqrt{\pi}$", color=BLUE, fontsize=8)
    for th, col in ((th_lo, GREEN), (th_hi, RUST)):
        u = np.array([math.cos(psi + th), math.sin(psi + th)])
        ax.plot(*u, "o", ms=3.4, color=col, zorder=6)
    ax.text(1.06, 0.13, "rotate by $\\theta_{-}$:\n$w_1$ reaches\nthe axis", color=GREEN, fontsize=6.4, ha="left", va="bottom")
    ax.text(0.17, 1.05, "rotate by $\\theta_{+}$: $w_3$ reaches the axis", color=RUST, fontsize=6.4, ha="left", va="bottom")
    ax.text(1.06, 0.62, "dots: $u=Os$,\n$\\pi'=u\\circ u$", color=INK, fontsize=6.4, ha="left", va="bottom")
    ax.set_xlim(-0.02, 1.42)
    ax.set_ylim(-0.02, 1.14)
    ax.set_xticks([0, 0.5, 1])
    ax.set_yticks([0, 0.5, 1])
    ax.spines["bottom"].set_bounds(0, 1)
    ax.spines["left"].set_bounds(0, 1)
    ax.set_xlabel("coordinate 1 (latent 1) of $W=D_{\\sqrt{\\pi}}K$")
    ax.set_ylabel("coordinate 2 (latent 2)")

    # (b) prior weight along the admissible arc
    ax = ax1
    th = np.linspace(th_lo, th_hi, 400)
    w1 = np.cos(psi + th) ** 2
    ax.axhspan(float(L), float(U), color=LBLUE, alpha=0.55, lw=0, zorder=0)
    ax.plot(np.degrees(th), w1, color=BLUE, lw=1.4, zorder=2, label=r"$\pi_1'(\theta)=\cos^2(\psi+\theta)$")
    gx = np.degrees([g[0] for g in grid])
    gy = [g[1] for g in grid]
    ax.plot(gx, gy, "o", ms=1.9, color=INK, alpha=0.75, zorder=3, label=r"exact fiber models ($\tan\frac{\theta}{2}\in\frac{1}{200}\mathbb{Z}$)")
    ax.plot([0], [float(PI[0])], marker="*", ms=9, color=GOLD, mec=INK, mew=0.4, zorder=5, ls="none", label=r"true model, $\pi_1=9/25$")
    ax.plot([math.degrees(th_w)], [float(witness[0][0])], marker="D", ms=4.2, color="white", mec=INK, mew=0.8, zorder=5, ls="none", label=r"ST-M87 witness, $K'>0$")
    ax.plot([math.degrees(th_lo)], [float(U)], "o", ms=4.5, color=GREEN, zorder=6)
    ax.plot([math.degrees(th_hi)], [float(L)], "o", ms=4.5, color=RUST, zorder=6)
    # annotations sit inside the shaded band, so the leader lines never cross it
    ax.annotate(r"$U=q_{x^*}^2/T_{x^*x^*}=1849/2425$" + "\noutcome 1 anchors latent 1",
                xy=(math.degrees(th_lo), float(U)), xytext=(math.degrees(th_lo) - 1.2, 0.40),
                fontsize=6.6, color=GREEN, ha="left", va="top",
                arrowprops=dict(arrowstyle="-", lw=0.5, color=GREEN, shrinkA=0, shrinkB=3))
    ax.annotate(r"$L=1-q_{y^*}^2/T_{y^*y^*}=144/1825$" + "\noutcome 3 anchors latent 2",
                xy=(math.degrees(th_hi), float(L)), xytext=(math.degrees(th_hi) + 1.5, 0.47),
                fontsize=6.6, color=RUST, ha="right", va="bottom",
                arrowprops=dict(arrowstyle="-", lw=0.5, color=RUST, shrinkA=0, shrinkB=3))
    ax.set_xlim(math.degrees(th_lo) - 3, math.degrees(th_hi) + 3)
    ax.set_ylim(0, 1.0)
    ax.set_xlabel(r"rotation angle $\theta$ (degrees)")
    ax.set_ylabel(r"weight $\pi_1'$ of the fiber model")
    ax.legend(loc="upper right", fontsize=6.3, handlelength=1.4, borderaxespad=0.1)
    fig.canvas.draw()
    ytit = max(ax0.get_position().y1, ax1.get_position().y1) + 0.035
    for a_, tit in ((ax0, r"$\mathbf{(a)}$  columns of $W$ and the rotated cones"),
                    (ax1, r"$\mathbf{(b)}$  prior weight along the admissible arc")):
        p_ = a_.get_position()
        fig.text(0.5 * (p_.x0 + p_.x1), ytit, tit, fontsize=8, color=INK, ha="center", va="bottom")
    save(fig, "fig_fiber_k2")


# ---------------------------------------------------------------------------
# Figure 2: k = 3, consistent priors in the simplex for three channels
# (ST-T298, ST-T302, ST-M88, ST-T303, ST-M89)
# ---------------------------------------------------------------------------


def tern(p):
    p = np.asarray(p, dtype=float)
    x = p[..., 1] + 0.5 * p[..., 2]
    y = (math.sqrt(3) / 2) * p[..., 2]
    return x, y


def simplex_axes(ax, title):
    tri = np.array([[0, 0], [1, 0], [0.5, math.sqrt(3) / 2], [0, 0]])
    ax.plot(tri[:, 0], tri[:, 1], color=INK, lw=0.6)
    for k in range(1, 10):
        f = k / 10
        for (a, b) in (((f, 1 - f, 0), (f, 0, 1 - f)), ((1 - f, f, 0), (0, f, 1 - f)), ((1 - f, 0, f), (0, 1 - f, f))):
            xa, ya = tern(a)
            xb, yb = tern(b)
            ax.plot([xa, xb], [ya, yb], color=LGRAY, lw=0.35, zorder=0)
    ax.text(-0.02, -0.02, r"$e_1$", ha="right", va="top", fontsize=8)
    ax.text(1.02, -0.02, r"$e_2$", ha="left", va="top", fontsize=8)
    ax.text(0.5, math.sqrt(3) / 2 + 0.02, r"$e_3$", ha="center", va="bottom", fontsize=8)
    ax.set_aspect("equal")
    ax.set_xlim(-0.08, 1.08)
    ax.set_ylim(-0.15, 0.95)
    ax.axis("off")
    ax.set_title(title, fontsize=8, color=INK, pad=11)


def haar_scan(S, K, n, seed):
    rng = np.random.default_rng(seed)
    W = np.diag([float(x) for x in S]) @ np.array([[float(x) for x in r] for r in K])
    s = np.array([float(x) for x in S])
    out = []
    chunk = 20000
    for _ in range(n // chunk):
        G = rng.standard_normal((chunk, 3, 3))
        Q, Rm = np.linalg.qr(G)
        Q = Q * np.sign(np.diagonal(Rm, axis1=1, axis2=2))[:, None, :]
        M = Q @ W
        ok = (M >= -1e-12).all(axis=(1, 2))
        u = Q[ok] @ s
        out.append(u ** 2)
    return np.concatenate(out)


def fig_fiber_k3():
    fig, axes = plt.subplots(1, 3, figsize=(6.6, 2.75), gridspec_kw={"wspace": 0.16})

    # (a) strictly positive channel K3 with prior (1/9, 4/9, 4/9)
    ax = axes[0]
    simplex_axes(ax, r"$\mathbf{(a)}$  $K>0$ entrywise (ST-M88)")
    ell = tv.weight_floor(tv.S3, tv.K3)
    assert ell == F(4, 153)
    e = float(ell)
    inner = [(1 - 2 * e, e, e), (e, 1 - 2 * e, e), (e, e, 1 - 2 * e), (1 - 2 * e, e, e)]
    xi, yi = tern(inner)
    ax.fill(xi, yi, color=LRUST, alpha=0.35, lw=0, zorder=1)
    ax.plot(xi, yi, color=RUST, lw=0.7, ls="--", zorder=2)
    scan = haar_scan(tv.S3, tv.K3, 3000000, seed=20261018)
    assert (scan.min(axis=1) >= e - 1e-9).all()
    xs, ys = tern(scan)
    ax.scatter(xs, ys, s=0.9, color=BLUE, alpha=0.18, lw=0, zorder=2, rasterized=True)
    # exact Cayley grid of the ST-F59 certificate (SO(3) chart, 9261 points)
    grid = [F(j, 10) for j in range(-10, 11)]
    exact = []
    T3 = tv.two_view(tv.PI3, tv.K3)
    for a, b, c in product(grid, repeat=3):
        r = tv.fiber_point(tv.S3, tv.K3, tv.cayley(tv.skew3(a, b, c)))
        if r is not None:
            pip, Kp, _ = r
            assert tv.two_view(pip, Kp) == T3 and tv.is_row_stochastic(Kp)
            exact.append([float(x) for x in pip])
    assert len(exact) == 197
    xe, ye = tern(np.array(exact))
    ax.scatter(xe, ye, s=2.6, color=INK, lw=0, zorder=4)
    xt, yt = tern(np.array([float(x) for x in tv.PI3]))
    ax.plot(xt, yt, marker="*", ms=8, color=GOLD, mec=INK, mew=0.4, zorder=5)
    ax.text(0.5, -0.1, r"dashed: floor $\ell(T)=4/153$", ha="center", fontsize=7.5, color=RUST)

    # (b) anchored channel, same prior: only relabelings survive (ST-T303)
    ax = axes[1]
    simplex_axes(ax, r"$\mathbf{(b)}$  anchored $K$ (ST-T303)")
    q, T = tv.one_view(tv.PI3, tv.K3_ANCHORED), tv.two_view(tv.PI3, tv.K3_ANCHORED)
    assert [q[x] * q[x] / T[x][x] for x in range(3)] == tv.PI3
    pts = set()
    for perm in permutations(range(3)):
        P = [[F(int(perm[i] == j)) for j in range(3)] for i in range(3)]
        r = tv.fiber_point(tv.S3, tv.K3_ANCHORED, P)
        assert r is not None
        pts.add(tuple(r[0]))
    for p in pts:
        x, y = tern(np.array([float(v) for v in p]))
        ax.plot(x, y, "o", ms=4, color=INK, zorder=4)
    ax.plot(xt, yt, marker="*", ms=8, color=GOLD, mec=INK, mew=0.4, zorder=5)
    scan_b = haar_scan(tv.S3, tv.K3_ANCHORED, 200000, seed=7)
    assert len(scan_b) == 0
    ax.text(0.5, -0.1, "relabelings only", ha="center", fontsize=7.5, color=INK)

    # (c) no anchors but sufficiently scattered: point identified (ST-M89)
    ax = axes[2]
    simplex_axes(ax, r"$\mathbf{(c)}$  scattered, no anchors (ST-M89)")
    s_unif = [F(1), F(1), F(1)]  # s proportional to 1; G(W) = {O : O K >= 0}
    assert all(sum(row) == 1 for row in tv.K_SCATTERED)
    scan_c = haar_scan(s_unif, tv.K_SCATTERED, 200000, seed=11)
    assert len(scan_c) == 0
    xu, yu = tern(np.array([1 / 3, 1 / 3, 1 / 3]))
    ax.plot(xu, yu, marker="*", ms=8, color=GOLD, mec=INK, mew=0.4, zorder=5)
    ax.text(0.5, -0.1, "point identified", ha="center", fontsize=7.5, color=INK)
    save(fig, "fig_fiber_k3")
    return len(scan)


# ---------------------------------------------------------------------------
# Figure 3: evidence growth versus the persistent-latent cap
# (ST-T273, ST-T277, ST-T278, ST-T279, ST-T280)
# ---------------------------------------------------------------------------


def fig_evidence():
    fig, axes = plt.subplots(1, 3, figsize=(6.6, 2.75), gridspec_kw={"wspace": 0.55})
    with es.precise():
        # (a) hypotheses differ in the per-world law (coin bias beta against fair bits)
        ax = axes[0]
        ns = [1, 2, 4, 8, 16, 24, 32, 48, 64, 96, 128, 160, 192, 256, 320, 384, 448, 512]
        for bv, col in ((F(3, 5), BLUE), (F(11, 20), GREEN), (F(1, 2), GRAY)):
            ev = [float(es.expected_log_bf(n, bv)) for n in ns]
            kl = float(es.kl_to_fair(bv))
            lo = [n * kl - 0.5 * math.log(n) - math.log(2) for n in ns]
            hi = [n * kl - 0.5 * math.log(n) + 1 - 0.5 * math.log(math.pi / 2) for n in ns]
            assert all(l_ - 1e-9 <= e <= h_ + 1e-9 for l_, e, h_ in zip(lo, ev, hi))
            ax.fill_between(ns, lo, hi, color=col, alpha=0.16, lw=0)
            ax.plot(ns, ev, "-", color=col, lw=1.2 if bv != F(1, 2) else 1.0)
            lab = rf"$\beta={bv.numerator}/{bv.denominator}$"
            if bv == F(1, 2):
                ax.text(ns[-1] - 4, lo[-1] - 0.25, lab, color=GRAY, fontsize=6.6, ha="right", va="top")
            else:
                ax.text(ns[-1] - 4, hi[-1] + 0.25, lab, color=col, fontsize=6.6, ha="right", va="bottom")
        ax.axhline(0, color=LGRAY, lw=0.6, zorder=0)
        ax.set_xlim(0, 540)
        ax.set_ylim(-5.2, 9.6)
        ax.set_xticks([0, 128, 256, 384, 512])
        ax.set_xlabel(r"trials $n$")
        ax.set_ylabel(r"$E_\beta[\ln \mathrm{BF}_n]$ (nats)")
        ax.set_title("$\\mathbf{(a)}$  per-world law differs:\nlinear growth (ST-T273)", fontsize=7.8, pad=3)

        # (b) weight-only hypotheses saturate at KL(a||b)
        ax = axes[1]
        third = F(1, 3)
        rows_bin = [[1 - third, third], [third, 1 - third]]
        a, b = [F(3, 4), F(1, 4)], [F(1, 4), F(3, 4)]
        Ts = [1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256]
        cap = float(es.kl_vector(a, b))
        kl_bin = [float(es.persistent_audit(a, b, rows_bin, rows_bin, t)["kl_t"]) for t in Ts]
        assert all(k <= cap + 1e-12 for k in kl_bin)
        # non-identifying components: saturates strictly below the cap
        rows_ni = [[F(3, 4), F(1, 4)], [F(3, 4), F(1, 4)], [F(1, 4), F(3, 4)]]
        a2, b2 = [F(1, 2), F(1, 3), F(1, 6)], [F(1, 6), F(1, 3), F(1, 2)]
        merged = float(es.kl_vector([a2[0] + a2[1], a2[2]], [b2[0] + b2[1], b2[2]]))
        Ts2 = [t for t in Ts if t <= 128]
        kl_ni = [float(es.persistent_audit(a2, b2, rows_ni, rows_ni, t)["kl_t"]) for t in Ts2]
        # different kernels (ST-T280): exceeds the world-level cap
        rows_b3 = [[F(3, 5), F(2, 5)], [F(2, 5), F(3, 5)]]
        kl_dk = [float(es.persistent_audit(a, b, rows_bin, rows_b3, t)["kl_t"]) for t in Ts]
        within = sum(float(am) * float(es.kl_vector(ra, rb_)) for am, ra, rb_ in zip(a, rows_bin, rows_b3))
        assert abs(within - 0.009466) < 1e-6
        bound_dk = [cap + t * within for t in Ts]
        assert all(k <= bd + 1e-9 for k, bd in zip(kl_dk, bound_dk))
        ax.axhline(cap, color=BLUE, lw=0.7, ls="--")
        ax.text(1.0, cap + 0.09, r"cap $\mathrm{KL}(a\|b)$", color=BLUE, fontsize=6.4)
        ax.plot(Ts, kl_bin, "o-", ms=2.2, color=BLUE, lw=1.1)
        ax.axhline(merged, color=GOLD, lw=0.6, ls=":")
        ax.plot(Ts2, kl_ni, "s-", ms=2.0, color=GOLD, lw=1.0)
        ax.text(20, 0.06, "non-identifying", color=GOLD, fontsize=6.2, va="bottom", ha="left")
        ax.plot(Ts, bound_dk, color=RUST, lw=0.7, ls="--")
        ax.plot(Ts, kl_dk, "^-", ms=2.2, color=RUST, lw=1.0)
        ax.text(70, 2.15, "different kernels\n(bound dashed)", color=RUST, fontsize=6.4, ha="right")
        ax.set_xscale("log", base=2)
        ax.set_ylim(0, 3.2)
        ax.set_xlabel(r"transcript length $n$")
        ax.set_ylabel(r"$\mathrm{KL}(aK\,\|\,bK)$ (nats)")
        ax.set_title("$\\mathbf{(b)}$  only world weights differ:\nsaturation (ST-T277)", fontsize=7.8, pad=3)

        # (c) the saturation gap and its bound
        ax = axes[2]
        examples = [
            ("binary", a, b, rows_bin, BLUE, "o"),
            ("ternary", [F(1, 2), F(1, 3), F(1, 6)], [F(1, 6), F(1, 3), F(1, 2)],
             [[F(3, 4), F(1, 4)], [F(1, 2), F(1, 2)], [F(1, 4), F(3, 4)]], GREEN, "s"),
            ("support mismatch", [F(1, 2), F(1, 2), F(0)], [third, third, third],
             [[F(3, 4), F(1, 4)], [F(1, 2), F(1, 2)], [F(1, 4), F(3, 4)]], RUST, "^"),
        ]
        Tg = [1, 2, 4, 8, 12, 16, 24, 32, 48, 64, 96, 128]
        for name, aa, bb, rows, col, mk in examples:
            c0 = es.kl_vector(aa, bb)
            gaps, bounds = [], []
            for t in Tg:
                au = es.persistent_audit(aa, bb, rows, rows, t)
                g = c0 - au["kl_t"]
                bd, _ = es.gap_bound(aa, bb, rows, t, au["map_error"])
                assert bd - g > -es.TOL
                assert abs(g - au["gap_direct"]) < es.TOL
                gaps.append(float(g))
                bounds.append(float(bd))
            ax.plot(Tg, gaps, mk + "-", ms=2.2, color=col, lw=1.0, label=name)
            ax.plot(Tg, bounds, "--", color=col, lw=0.7)
        from matplotlib.lines import Line2D
        h, l = ax.get_legend_handles_labels()
        h.append(Line2D([], [], color=GRAY, lw=0.7, ls="--"))
        l.append("ST-T279 bound\n(same color)")
        ax.set_yscale("log")
        ax.set_ylim(1e-7, 2e1)
        ax.set_xlabel(r"transcript length $n$")
        ax.set_ylabel("saturation gap (nats)")
        ax.set_title("$\\mathbf{(c)}$  gap (solid) and\nST-T279 bound (dashed)", fontsize=7.8, pad=3)
        ax.legend(h, l, loc="lower left", fontsize=6.0, handlelength=1.6, borderaxespad=0.2, labelspacing=0.3)
    save(fig, "fig_evidence")


# ---------------------------------------------------------------------------
# Figure 4: the random-bit price of shared randomness
# (ST-T310, ST-T311, ST-T312, ST-T313, ST-M90..ST-M93)
# ---------------------------------------------------------------------------


def _receipt_curve(label: str):
    """Parse a committed gap curve from the random-bit-price receipt."""
    path = os.path.join(REPO, "receipts", "random-bit-price-shared-randomness.txt")
    for line in open(path):
        if line.strip().startswith(f"gap curve {label}:"):
            return [F(x.strip()) for x in line.split(":", 1)[1].split(",")]
    raise KeyError(label)


def fig_bits():
    fig = plt.figure(figsize=(6.6, 4.6))
    gs = fig.add_gridspec(2, 2, wspace=0.34, hspace=0.62)

    # (a) gap curves with the two-sided Theta(2^-b) envelope
    ax = fig.add_subplot(gs[0, 0])
    bs = list(range(0, 11))
    m27_receipt = _receipt_curve("ST-M27 radius 1/2")
    for name, col, mk in (("ST-M26 full-TV K3", BLUE, "o"), ("ST-M27 radius 1/2", RUST, "s")):
        A = rb.INSTANCES[name]
        V, _ = rb.solve_game(A)
        assert V == rb.EXPECTED_VALUES[name]
        D = rb.common_denominator(A)
        gaps = []
        for bb in bs:
            if name.startswith("ST-M26"):
                Vb = rb.k3_grid_value_fast(2 ** bb)
                assert Vb == F(5, 3) + F(2 ** bb % 3, 3 * 2 ** bb)  # ST-M90 closed form
            else:
                Vb, _ = rb.grid_value(A, 2 ** bb)  # exhaustive over the 2^b-grid
                assert Vb == F(5, 3) + F(2 ** bb % 3, 30 * 2 ** bb)  # ST-M91 closed form
                assert Vb - V == m27_receipt[bb]  # committed receipt curve
            gaps.append(Vb - V)
        lower = [F(1, D * V.denominator * 2 ** bb) for bb in bs]
        w = (F(1, 3), F(1, 3), F(1, 3))
        upper = [rb.rounding_gap_bound(A, w, 2 ** bb) for bb in bs]
        assert all(lo <= g <= up for lo, g, up in zip(lower, gaps, upper))
        ax.fill_between(bs, [float(x) for x in lower], [float(x) for x in upper], color=col, alpha=0.10, lw=0)
        ax.plot(bs, [float(x) for x in lower], color=col, lw=0.5, ls=":")
        ax.plot(bs, [float(x) for x in upper], color=col, lw=0.5, ls=":")
        ax.step(bs, [float(g) for g in gaps], where="post", color=col, lw=0.6, alpha=0.6)
        ax.plot(bs, [float(g) for g in gaps], mk, ms=3, color=col,
                label={"ST-M26 full-TV K3": "$K_3$ game (ST-M90)", "ST-M27 radius 1/2": "skew TV, $r=1/2$ (ST-M91)"}[name])
    ax.set_yscale("log", base=2)
    ax.set_xlabel(r"public fair bits $b$")
    ax.set_ylabel(r"$V_b-V^*$")
    ax.set_xticks(bs[::2])
    from matplotlib.patches import Patch
    h, l = ax.get_legend_handles_labels()
    h.append(Patch(fc=GRAY, alpha=0.25, lw=0))
    l.append("ST-T311 envelope")
    ax.legend(h, l, loc="lower left", fontsize=6.0, borderaxespad=0.1, handlelength=1.2)
    ax.set_ylim(2.0 ** -18.5, 2.0 ** 1)
    ax.set_title(r"$\mathbf{(a)}$  odd-numbered bits are worthless", fontsize=8, pad=3)

    # (b) Knuth-Yao tail for the uniform ternary law
    ax = fig.add_subplot(gs[0, 1])
    w = [F(1, 3)] * 3
    ts = list(range(0, 21))
    U = rb.ddg_undecided(w, ts[-1])
    tail = [F(u, 2 ** t) for t, u in enumerate(U)]
    assert all(tail[t] == rb.sampler_lower_bound_tail(w, t) for t in ts)
    assert rb.ky_expected_bits(w) == F(8, 3)
    ax.step(ts, [float(x) for x in tail], where="post", color=BLUE, lw=1.1)
    ax.plot(ts, [float(x) for x in tail], "o", ms=2.5, color=BLUE)
    ax.set_yscale("log", base=2)
    ax.set_xlabel(r"fair bits consumed $t$")
    ax.set_ylabel(r"$P(\tau>t)$")
    ax.set_xticks(range(0, 21, 4))
    H = math.log2(3)
    ax.text(20, 0.5, r"$E[\tau]=3\,\kappa(1/3)=8/3$" + "\n" + rf"$H(w)=\log_2 3\approx{H:.3f}$", ha="right", va="top", fontsize=6.8, color=INK)
    ax.text(0.3, 2.0 ** -17.5, r"$P(\tau>t)=(2^t\ \mathrm{mod}\ 3)/2^t$" + "\n= universal lower bound", fontsize=6.4, color=BLUE, va="bottom")
    ax.set_title(r"$\mathbf{(b)}$  exact ternary choice: never bounded", fontsize=8, pad=3)

    # (c) the DDG tree (Knuth-Yao) for (1/3, 1/3, 1/3)
    ax = fig.add_subplot(gs[1, 0])
    ax.axis("off")
    depth = 6
    U = rb.ddg_undecided(w, depth)
    assert U == [1, 2, 1, 2, 1, 2, 1]  # undecided nodes per depth
    y = lambda d: 1 - d / (depth + 0.6)
    h1, h2, x0 = 0.13, 0.065, 0.33
    for period in range(depth // 2):
        xr = x0 + period * (h1 + h2)
        d = 2 * period
        for sg1 in (-1, 1):
            xc = xr + sg1 * h1
            ax.plot([xr, xc], [y(d), y(d + 1)], color=GRAY, lw=0.6, zorder=1)
            ax.plot(xc, y(d + 1), "o", ms=2.6, color=INK, zorder=3)
            for sg2 in (-1, 1):
                xg = xc + sg2 * h2
                ax.plot([xc, xg], [y(d + 1), y(d + 2)], color=GRAY, lw=0.6, zorder=1)
        leaves = [xr - h1 - h2, xr - h1 + h2, xr + h1 - h2]
        for i, xl in enumerate(leaves):
            ax.text(xl, y(d + 2), "ABC"[i], ha="center", va="center", fontsize=6.2, color="white",
                    bbox=dict(boxstyle="circle,pad=0.16", fc=[BLUE, GREEN, RUST][i], ec="none"), zorder=4)
        ax.plot(xr, y(d), "o", ms=2.6, color=INK, zorder=3)
    xe = x0 + (depth // 2) * (h1 + h2)
    ax.plot(xe, y(depth), "o", ms=2.6, color=INK, zorder=3)
    ax.plot([xe, xe + 0.05], [y(depth), y(depth) - 0.05], color=GRAY, lw=0.6, ls=":")
    ax.text(0.98, y(2), r"$3/4$ decided", fontsize=6.4, ha="right", va="center", color=INK)
    ax.text(0.0, y(4), r"$15/16$ decided", fontsize=6.4, ha="left", va="center", color=INK)
    ax.text(0.0, y(6), r"$63/64$ decided", fontsize=6.4, ha="left", va="center", color=INK)
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(y(depth) - 0.1, 1.04)
    ax.set_title(r"$\mathbf{(c)}$  Knuth-Yao DDG tree for $(\frac{1}{3},\frac{1}{3},\frac{1}{3})$", fontsize=8, pad=3)

    # (d) one L-ary toss: V_{L,1} for the K3 game and the skew TV game
    ax = fig.add_subplot(gs[1, 1])
    Ls = list(range(1, 13))
    vk3 = [rb.k3_grid_value_fast(L) for L in Ls]
    assert all(v == 2 - F(L // 3, L) for v, L in zip(vk3, Ls))
    vm27 = [rb.grid_value(rb.INSTANCES["ST-M27 radius 1/2"], L)[0] for L in Ls]
    ax.axhline(5 / 3, color=INK, lw=0.6, ls="--", label=r"$V^*=5/3$")
    ax.plot(Ls, [float(v) for v in vm27], "s", ms=2.4, color=RUST, label="skew TV, $r=1/2$ (ST-M91)")
    ax.vlines(Ls, 5 / 3, [float(v) for v in vk3], color=BLUE, lw=1.0, alpha=0.6)
    hit = [L % 3 == 0 for L in Ls]
    ax.plot([L for L, h in zip(Ls, hit) if not h], [float(v) for v, h in zip(vk3, hit) if not h], "o", ms=3.4, color=BLUE, label="$K_3$ game (ST-M90)")
    ax.plot([L for L, h in zip(Ls, hit) if h], [float(v) for v, h in zip(vk3, hit) if h], "o", ms=4.2, mfc="white", mec=BLUE, mew=1.0, zorder=5)
    ax.set_xticks(Ls)
    ax.set_xlabel(r"sides $L$ of one public toss")
    ax.set_ylabel(r"$V_{L,1}$")
    ax.set_ylim(1.635, 2.03)
    ax.legend(loc="upper right", fontsize=6.3)
    ax.set_title(r"$\mathbf{(d)}$  one toss reaches $V^*$ iff $3\mid L$ (open circles)", fontsize=8, pad=3)
    save(fig, "fig_bits")


if __name__ == "__main__":
    which = sys.argv[1:] or ["k2", "k3", "evidence", "bits"]
    if "k2" in which:
        fig_fiber_k2()
    if "k3" in which:
        n = fig_fiber_k3()
        print("k3 float-scan admissible samples:", n)
    if "evidence" in which:
        fig_evidence()
    if "bits" in which:
        fig_bits()
