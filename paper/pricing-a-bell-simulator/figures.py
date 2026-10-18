"""Figures for "Pricing a Bell simulator".

Every number plotted here is computed from the repository root (../../)
(commit aa61193) by calling its own modules and reading its committed data:

  simtheory.real_data            Delft 2015 trials (ST-F50, ST-F51)
  simtheory.bell_disk_zonoid     polar zonotopes and CHSH grid counts (ST-T290 to ST-T296)
  simtheory.finite_precision_renderers   lattice separations and sqrt2 digits (ST-T286 to ST-T289, ST-F57)
  simtheory.bell_escape_routes   strategy enumerations and e-processes (ST-T281 to ST-T285, ST-M85, ST-F56)
  simtheory.le_cam_deficiency    deficiency formulas and deterministic values (ST-T306 to ST-T309, ST-F60)

The only quantity not taken from a repository claim is the 1-sigma ellipse of
the Delft disk point, which uses the same per-setting binomial variance
(1 - E^2)/n as the repository's S error (ST-F50); the paper labels it as such.

Run:  OMP_NUM_THREADS=1 .venv/bin/python figures.py
"""

from __future__ import annotations

import math
import os
import sys
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

from simtheory import bell_disk_zonoid as bz  # noqa: E402
from simtheory import bell_escape_routes as be  # noqa: E402
from simtheory import finite_precision_renderers as fp  # noqa: E402
from simtheory import le_cam_deficiency as lc  # noqa: E402
from simtheory import real_data as rd  # noqa: E402

OUT = HERE / "figures"
OUT.mkdir(exist_ok=True)

# ----------------------------------------------------------------- style
INK = "#1d2733"
MUTE = "#7b8492"
GRID = "#e4e7ec"
BLUE = "#2b5c8a"
TEAL = "#3f8a78"
RUST = "#b3532f"
GOLD = "#c28f1f"
PLUM = "#7a4a86"
SHADE = "#eef2f7"

plt.rcParams.update(
    {
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
        "axes.edgecolor": INK,
        "axes.labelcolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "axes.linewidth": 0.6,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "xtick.major.size": 2.8,
        "ytick.major.size": 2.8,
        "xtick.minor.size": 1.6,
        "ytick.minor.size": 1.6,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "legend.frameon": False,
        "lines.linewidth": 1.2,
        "svg.fonttype": "path",
        "pdf.fonttype": 42,
        "figure.dpi": 150,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.02,
    }
)

TEXTWIDTH = 6.3  # inches, matches the Typst text block


def panel_label(ax, s, x=-0.02, y=1.04):
    ax.text(x, y, s, transform=ax.transAxes, fontsize=9.5, fontweight="bold", color=INK, ha="right", va="bottom")


def save(fig, name):
    fig.savefig(OUT / f"{name}.svg")
    fig.savefig(OUT / f"{name}.pdf")
    plt.close(fig)
    print("wrote", name)


SQ2 = math.sqrt(2.0)


# ----------------------------------------------------------------- data
def delft():
    summary, trials = rd.load_delft_summary()
    counts = {s: 0 for s in rd.DELFT_SETTING_SIGNS}
    sums = {s: 0 for s in rd.DELFT_SETTING_SIGNS}
    for t in trials:
        counts[(t.a, t.b)] += 1
        sums[(t.a, t.b)] += t.x * t.y
    order = [(0, 0), (0, 1), (1, 0), (1, 1)]
    E = [sums[s] / counts[s] for s in order]
    n = [counts[s] for s in order]
    q = rd.canonical_disk_point(E)
    # x = (E00+E01+E10-E11)/(2 sqrt2), y = (-E00+E01+E10+E11)/(2 sqrt2)
    A = np.array([[1, 1, 1, -1], [-1, 1, 1, 1]], dtype=float) / (2 * SQ2)
    var = np.diag([(1 - e * e) / m for e, m in zip(E, n)])
    cov = A @ var @ A.T
    S = sum(rd.DELFT_SETTING_SIGNS[s] * e for s, e in zip(order, E))
    return dict(trials=trials, E=E, n=n, q=q, cov=cov, S=S, summary=summary)


def ellipse_from_cov(center, cov, nsig=1.0, **kw):
    vals, vecs = np.linalg.eigh(cov)
    order = vals.argsort()[::-1]
    vals, vecs = vals[order], vecs[:, order]
    angle = math.degrees(math.atan2(vecs[1, 0], vecs[0, 0]))
    w, h = 2 * nsig * np.sqrt(vals)
    return Ellipse(center, w, h, angle=angle, **kw)


# ----------------------------------------------------------------- Figure 1: the CHSH disk
def fig_disk(d):
    fig, (ax, az) = plt.subplots(1, 2, figsize=(TEXTWIDTH, 3.3), gridspec_kw=dict(width_ratios=[1.0, 1.0], wspace=0.22))
    c = 1 / SQ2
    for a in (ax, az):
        a.set_aspect("equal")
    # left: whole disk
    strip = Rectangle((-c, -1.05), 2 * c, 2.1, facecolor=SHADE, edgecolor="none", zorder=0)
    ax.add_patch(strip)
    disk = Circle((0, 0), 1.0, transform=ax.transData, facecolor="none", edgecolor="none")
    ax.add_patch(disk)
    strip.set_clip_path(disk)
    th = np.linspace(0, 2 * np.pi, 400)
    ax.plot(np.cos(th), np.sin(th), color=INK, lw=1.0, zorder=3)
    for s in (-1, 1):
        yy = math.sqrt(1 - c * c)
        ax.plot([s * c, s * c], [-yy, yy], color=BLUE, lw=1.0, zorder=3)
    # H_32 meets the Werner (phase 0) axis at q_x = m sqrt2 / 8
    xs = [m * SQ2 / 8 for m in range(-5, 6)]
    ax.plot(xs, [0] * len(xs), ls="none", marker="|", ms=6, mew=0.9, color=GOLD, zorder=4)
    ax.plot([5 * SQ2 / 8], [0], ls="none", marker="o", ms=4.2, mfc=GOLD, mec=INK, mew=0.5, zorder=5)
    # Tsirelson points
    ax.plot([1, -1], [0, 0], ls="none", marker="D", ms=3.6, mfc="white", mec=INK, mew=0.8, zorder=5)
    # Delft
    qx, qy = d["q"]
    ax.add_patch(ellipse_from_cov((qx, qy), d["cov"], facecolor=RUST, alpha=0.18, edgecolor=RUST, lw=0.6, zorder=4))
    ax.plot([qx], [qy], marker="o", ms=3.6, color=RUST, zorder=6)
    ax.annotate("Tsirelson\n$S=2\\sqrt{2}$", xy=(1, 0), xytext=(0.93, 0.86), fontsize=7.2, color=INK, ha="center",
                arrowprops=dict(arrowstyle="-", lw=0.5, color=MUTE))
    ax.text(0, 0.82, "$|S|\\leq 2$", ha="center", fontsize=7.2, color=BLUE)
    ax.text(c + 0.02, -0.82, "$x=1/\\sqrt{2}$", fontsize=7, color=BLUE)
    ax.set_xlim(-1.12, 1.12)
    ax.set_ylim(-1.12, 1.12)
    ax.set_xlabel("$x = v\\cos\\phi$")
    ax.set_ylabel("$y = v\\sin\\phi$")
    ax.set_xticks([-1, -c, 0, c, 1])
    ax.set_xticklabels(["$-1$", "$-\\frac{1}{\\sqrt{2}}$", "$0$", "$\\frac{1}{\\sqrt{2}}$", "$1$"])
    ax.set_yticks([-1, 0, 1])
    # zoom box
    x0, x1, y0, y1 = 0.6, 1.1, -0.3, 0.2
    ax.add_patch(Rectangle((x0, -0.3), 1.03 - x0, 0.5, fill=False, edgecolor=INK, lw=0.5, zorder=7))
    panel_label(ax, "a")

    # right: zoom
    az.add_patch(Rectangle((x0 - 0.1, y0 - 0.1), c - x0 + 0.1, y1 - y0 + 0.2, facecolor=SHADE, edgecolor="none", zorder=0))
    th = np.linspace(-0.6, 0.6, 200)
    az.plot(np.cos(th), np.sin(th), color=INK, lw=1.0, zorder=3)
    az.plot([c, c], [y0 - 0.1, y1 + 0.1], color=BLUE, lw=1.0, zorder=3)
    # l_inf TV ball around the Delft point that just reaches the chord: radius x - 1/sqrt2
    r = qx - c
    az.add_patch(Rectangle((qx - r, qy - r), 2 * r, 2 * r, fill=False, edgecolor=TEAL, lw=0.9, ls="-", zorder=4))
    az.add_patch(ellipse_from_cov((qx, qy), d["cov"], facecolor=RUST, alpha=0.16, edgecolor=RUST, lw=0.7, zorder=4))
    az.plot([qx], [qy], marker="o", ms=4, color=RUST, zorder=6)
    az.plot(xs, [0] * len(xs), ls="none", marker="|", ms=8, mew=1.0, color=GOLD, zorder=5)
    az.plot([5 * SQ2 / 8], [0], ls="none", marker="o", ms=5, mfc=GOLD, mec=INK, mew=0.5, zorder=6)
    az.plot([1], [0], ls="none", marker="D", ms=4, mfc="white", mec=INK, mew=0.8, zorder=6)
    az.text(c + 0.01, qy + r - 0.01, f"Delft 2015\n$S={d['S']:.3f}$", fontsize=7, color=RUST, ha="left", va="top")
    az.annotate("$D=32$ renderer\n$v=5\\sqrt{2}/8,\\ S=5/2$", xy=(5 * SQ2 / 8, 0), xytext=(0.865, 0.15), fontsize=7, color="#8a6512",
                ha="center", arrowprops=dict(arrowstyle="-", lw=0.5, color=GOLD))
    az.text(c + 0.008, qy - r + 0.008, "TV ball,\nradius %.3f" % ((d["S"] - 2) / 8), fontsize=6.8, color=TEAL,
            ha="left", va="bottom")
    az.text(1.018, -0.012, "Tsirelson", fontsize=6.8, color=INK, ha="left", va="top")
    az.text(0.653, -0.285, "$|S|\\leq 2$", fontsize=6.6, color=BLUE, ha="center")
    az.set_xlim(x0, x1)
    az.set_ylim(y0, y1)
    az.set_xlabel("$x$")
    az.set_ylabel("$y$")
    az.set_xticks([0.6, c, 0.8, 0.9, 1.0])
    az.set_xticklabels(["0.6", "$\\frac{1}{\\sqrt{2}}$", "0.8", "0.9", "1"])
    panel_label(az, "b")
    save(fig, "fig1_disk")


# ----------------------------------------------------------------- Figure 2: finite precision
def fig_precision():
    fig = plt.figure(figsize=(TEXTWIDTH, 2.55))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.0, 1.0], wspace=0.42)
    ax, ab, ac = fig.add_subplot(gs[0]), fig.add_subplot(gs[1]), fig.add_subplot(gs[2])
    ab.set_box_aspect(1)
    ac.set_box_aspect(1)

    # (a) correlator pairs reachable by H_D, Werner-shaped grid laws, and two Werner segments
    D = 32
    ms = [m for m in range(0, D + 1) if (m - D) % 2 == 0]
    pts = np.array([(a / D, b / D) for a in ms for b in ms])
    ax.plot(pts[:, 0], pts[:, 1], ls="none", marker="o", ms=0.7, color="#c9ced6", zorder=1)
    lat = [x for x in fp.werner_lattice(D) if x >= 0]
    W = np.array([(float(a), float(b)) for a in lat for b in lat])
    ax.plot(W[:, 0], W[:, 1], ls="none", marker="s", ms=2.6, mfc=MUTE, mec="none", zorder=2)
    v = np.linspace(0.5, 1.0, 2)
    ax.plot([0, 1], [0, 1], color=BLUE, lw=0.4, ls=(0, (1, 2)), zorder=1)
    ax.plot([0, 1], [0, 1 / SQ2], color=RUST, lw=0.4, ls=(0, (1, 2)), zorder=1)
    # CHSH pair: both cosines 1/sqrt2 (ST-T287 applies)
    ax.plot(v / SQ2, v / SQ2, color=BLUE, lw=1.8, solid_capstyle="round", zorder=3)
    hits = [float(x) for x in lat if 0.5 / SQ2 <= x <= 1 / SQ2]
    ax.plot(hits, hits, ls="none", marker="o", ms=3.6, mfc=BLUE, mec="white", mew=0.6, zorder=4)
    # {0, pi/4} pair: cosines 1 and 1/sqrt2 (ST-T288 applies)
    ax.plot(v, v / SQ2, color=RUST, lw=1.8, solid_capstyle="round", zorder=3)
    box = dict(boxstyle="square,pad=0.12", fc="white", ec="none")
    ax.text(0.25, 0.66, "CHSH pair", color=BLUE, fontsize=6.8, ha="center", bbox=box, zorder=5)
    ax.text(0.84, 0.40, "$\\{0,\\pi/4\\}$", color=RUST, fontsize=6.8, ha="center", bbox=box, zorder=5)
    ax.set_aspect("equal")
    ax.set_xlim(-0.03, 1.03)
    ax.set_ylim(-0.03, 1.03)
    ax.set_xticks([0, 0.5, 1])
    ax.set_yticks([0, 0.5, 1])
    ax.set_xlabel("$\\tau_1$")
    ax.set_ylabel("$\\tau_2$")
    ax.set_title("$D=32$, $v\\in[1/2,1]$", fontsize=8, color=INK, pad=3)
    panel_label(ax, "a", x=-0.16, y=1.0)

    # (b) D^2 g_D on the repository's declared grid
    vmin, vmax = Fr(1, 2), Fr(1)
    D_list = sorted(set(list(range(4, 401, 4)) + [4 * P for P, _ in fp.pell_pairs(2500)] + [1000, 2048, 4096, 8192, 10000, 1001, 999]))
    pell = {4 * P for P, _ in fp.pell_pairs(2500)}
    vals = []
    for Dv in D_list:
        g, _arg = fp.grid_segment_separation(Dv, vmin, vmax)
        vals.append((Dv, float(g) * Dv * Dv))
    Ds = np.array([a for a, _ in vals])
    rs = np.array([b for _, b in vals])
    isp = np.array([a in pell for a in Ds])
    ab.plot(Ds[~isp], rs[~isp], ls="none", marker="o", ms=2.0, color=MUTE, zorder=3, label="declared grid")
    ab.plot(Ds[isp], rs[isp], ls="none", marker="s", ms=3.0, mfc=RUST, mec="white", mew=0.4, zorder=4, label="$D=4P$ (Pell)")
    lb = 1 / (3 + 2 * SQ2)
    ab.axhline(lb, color=INK, lw=0.8, ls=(0, (4, 2)))
    ab.text(4.0, lb + 0.12, "proved: $1/(3+2\\sqrt{2})$", fontsize=6.6, color=INK, va="bottom")
    ab.set_xscale("log")
    ab.set_ylim(0, 4.4)
    ab.set_yticks([0, 1, 2, 3, 4])
    ab.set_xlim(3, 1.4e4)
    ab.set_xlabel("precision $D$")
    ab.set_ylabel("$D^2\\, g_D$")
    ab.legend(loc="upper left", handletextpad=0.2, borderaxespad=0.2, ncol=1)
    panel_label(ab, "b", x=-0.16, y=1.0)

    # (c) 2^k TV_k at the fixed angle pi/4, known v = 1: the binary digits of sqrt2
    ks = list(range(3, 65))
    tvs = [float(fp.tv_pi4_formula(k)) * 2 ** k for k in ks]
    ac.plot(ks, tvs, color=TEAL, lw=0.5, alpha=0.6)
    ac.plot(ks, tvs, ls="none", marker="o", ms=2.4, color=TEAL)
    kmin = ks[int(np.argmin(tvs))]
    ac.annotate(f"$k={kmin}$: {min(tvs):.4f}", xy=(kmin, min(tvs)), xytext=(42, 0.0055), fontsize=6.8, color=INK,
                arrowprops=dict(arrowstyle="-", lw=0.5, color=MUTE))
    ac.set_yscale("log")
    ac.set_ylim(3e-3, 1.5)
    ac.set_xlim(2, 66)
    ac.set_xlabel("$k$  ($D=2^k$)")
    ac.set_ylabel("$2^k\\,\\mathrm{TV}_k$")
    panel_label(ac, "c", x=-0.16, y=1.0)
    save(fig, "fig2_precision")


# ----------------------------------------------------------------- Figure 3: zonoid memory constants
def float_schedule(angles, weights=None):
    m = len(angles)
    weights = weights or [1.0 / m] * m
    return [(w, (math.cos(t), math.sin(t))) for w, t in zip(weights, angles)]


def fig_zonoid():
    fig = plt.figure(figsize=(TEXTWIDTH, 2.55))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.15, 1.0], wspace=0.32)
    ax, ab, ac = fig.add_subplot(gs[0]), fig.add_subplot(gs[1]), fig.add_subplot(gs[2])

    shapes = [
        ("CHSH  $32$", float_schedule([math.pi / 4, -math.pi / 4]), BLUE, "-"),
        ("reg. 3  $18\\sqrt{3}$", float_schedule([0, math.pi / 3, 2 * math.pi / 3]), TEAL, "-"),
        ("reg. 4  $384\\sqrt{2}-512$", float_schedule([0, math.pi / 4, math.pi / 2, 3 * math.pi / 4]), RUST, "-"),
    ]
    for label, sched, col, ls in shapes:
        V = bz.polar_vertices(sched)
        area = bz.shoelace(V)
        ax.add_patch(Polygon(np.array(V, dtype=float), closed=True, fill=False, edgecolor=col, lw=1.0, ls=ls, label=label, zorder=3))
        print(f"  polar area {label}: {area:.6f}")
    th = np.linspace(0, 2 * np.pi, 400)
    ax.plot(np.pi * np.cos(th), np.pi * np.sin(th), color=INK, lw=0.8, ls=(0, (2, 1.5)), label="disk  $\\pi^3$")
    ax.set_aspect("equal")
    lim = 3.62
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_xticks([-3, 0, 3])
    ax.set_yticks([-3, 0, 3])
    ax.set_xlabel("$x_1$")
    ax.set_ylabel("$x_2$")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.3), ncol=2, handlelength=1.3, fontsize=6.0, handletextpad=0.4, labelspacing=0.3, columnspacing=0.8, title="area of $Z^\\circ$", title_fontsize=6.3)
    panel_label(ax, "a", x=-0.14)

    # (b) ladder of asymptotic constants lim N eps^2
    consts = [
        ("ST-T13 packing $1/16$ (lower)", 1 / 16, MUTE),
        ("CHSH exact $\\pi/32$", math.pi / 32, BLUE),
        ("regular 3 exact $\\pi/(18\\sqrt{3})$", math.pi / (18 * math.sqrt(3)), TEAL),
        ("regular 4, lower $\\pi/A_4$", math.pi / (384 * SQ2 - 512), RUST),
        ("area-converse ceiling $1/\\pi^2$", 1 / math.pi ** 2, INK),
        ("Fejes T$\\acute{\\rm o}$th upper $2/(\\sqrt{27}\\pi)$", 2 / (math.sqrt(27) * math.pi), INK),
    ]
    for i, (lab, val, col) in enumerate(consts):
        y = len(consts) - 1 - i
        ab.plot([0.058, val], [y, y], color=GRID, lw=2.4, solid_capstyle="butt", zorder=1)
        ab.plot([val], [y], marker="o", ms=4, color=col, zorder=3)
        ab.text(0.0585, y + 0.2, lab, fontsize=6.6, color=col, va="bottom", ha="left")
        ab.text(val + 0.0028, y, f"{val:.5f}", fontsize=6.4, color=col, va="center")
    ab.set_yticks([])
    ab.axvspan(1 / math.pi ** 2, 2 / (math.sqrt(27) * math.pi), color=SHADE, zorder=0)
    ab.set_xlim(0.058, 0.137)
    ab.set_ylim(-0.5, 5.75)
    ab.set_xticks([0.06, 0.08, 0.10, 0.12])
    ab.set_xlabel("constant for $N_w(\\varepsilon)\\,\\varepsilon^2$\n(limit or bound)")
    ab.spines["left"].set_visible(False)
    panel_label(ab, "b", x=-0.02)

    # (c) exact CHSH grid counts versus pi/(32 eps^2)
    ns = list(range(40, 401, 40))
    ratios_meet, ratios_fam = [], []
    for n in ns:
        meet, inside, bd = bz.chsh_grid_counts(n)
        base = math.pi * n * n / 32
        ratios_meet.append(meet / base)
        ratios_fam.append((meet + 3 * bd) / base)
    ac.plot(ns, ratios_fam, marker="s", ms=2.6, color=TEAL, label="in-family $G+3G_{\\mathrm{bd}}$")
    ac.plot(ns, ratios_meet, marker="o", ms=2.6, color=BLUE, label="clipped centers $G$")
    nn = np.linspace(40, 400, 200)
    ac.plot(nn, (1 + 8 / nn) ** 2, color=INK, lw=0.7, ls=(0, (3, 2)), label="$(1+8\\varepsilon)^2$")
    ac.axhline(1.0, color=INK, lw=0.6)
    ac.set_xlabel("$1/\\varepsilon$")
    ac.set_ylabel("count $\\times\\ 32\\varepsilon^2/\\pi$")
    ac.set_ylim(0.95, 2.45)
    ac.legend(loc="upper right", handlelength=1.4)
    panel_label(ac, "c", x=-0.12)
    save(fig, "fig3_zonoid")


# ----------------------------------------------------------------- Figure 4: escape routes
def fig_frontiers():
    fig, (aa, ab, ac) = plt.subplots(1, 3, figsize=(TEXTWIDTH, 2.3), gridspec_kw=dict(wspace=0.42))
    ts = math.cos(math.pi / 8) ** 2
    delft_rate = 196 / 245

    pts = sorted(set(be.signalling_strategies()))
    flag = sorted(set(be.flag_strategies()))
    aa.plot([float(c) for c, _ in pts], [float(w) for _, w in pts], ls="none", marker="o", ms=3.0, mfc="white", mec=MUTE, mew=0.6,
            zorder=3, label="deterministic strategies")
    c = np.linspace(0, 1, 200)
    aa.plot(c, np.minimum(0.75 + c / 2, 1), color=BLUE, lw=1.3, zorder=4, label="silence free, $3/4+c/2$")
    aa.plot(c, 0.75 + c / 4, color=RUST, lw=1.3, zorder=4, label="$s$-blind flag, $3/4+c/4$")
    aa.legend(loc="lower right", bbox_to_anchor=(1.0, 0.14), fontsize=6.2, handlelength=1.4, borderaxespad=0.0)
    aa.axhline(ts, color=INK, lw=0.6, ls=(0, (3, 2)))
    aa.text(0.995, ts + 0.008, "Tsirelson", fontsize=6.4, ha="right", va="bottom")
    aa.plot([2 * (ts - 0.75)], [ts], marker="o", ms=3, color=BLUE, zorder=5)
    aa.plot([4 * (ts - 0.75)], [ts], marker="o", ms=3, color=RUST, zorder=5)
    aa.annotate("$c=\\sqrt{2}-1$ (Pironio)", xy=(4 * (ts - 0.75), ts), xytext=(0.74, 0.785), fontsize=6.4, color=RUST, ha="center",
                arrowprops=dict(arrowstyle="-", lw=0.5, color=RUST))
    aa.set_xlabel("communication cost $c$")
    aa.set_ylabel("max win probability")
    aa.set_ylim(0.45, 1.03)
    aa.set_xlim(-0.03, 1.03)
    panel_label(aa, "a", x=-0.13)

    l = np.linspace(0, 0.25, 100)
    ab.plot(l, 1 - l, color=TEAL, lw=1.3)
    ab.axhline(ts, color=INK, lw=0.6, ls=(0, (3, 2)))
    ab.axhline(delft_rate, color=RUST, lw=0.6, ls=(0, (1, 1.5)))
    ab.plot([1 - ts], [ts], marker="o", ms=3, color=TEAL)
    ab.plot([1 - delft_rate], [delft_rate], marker="o", ms=3, color=RUST)
    ab.text(0.002, ts + 0.006, "Tsirelson", fontsize=6.4, va="bottom")
    ab.text(0.002, delft_rate + 0.006, "Delft rate $196/245$", fontsize=6.4, va="bottom", color=RUST)
    ab.text(0.155, 0.93, "$1-\\ell$", fontsize=7.5, color=TEAL)
    ab.set_xlabel("setting-probability floor $\\ell$")
    ab.set_ylabel("max win probability")
    ab.set_xlim(0, 0.255)
    ab.set_ylim(0.45, 1.03)
    ab.set_xticks([0, 0.1, 0.2, 0.25])
    ab.set_xticklabels(["0", "0.1", "0.2", "1/4"])
    panel_label(ab, "b", x=-0.13)

    eta = np.linspace(0.6, 1.0, 200)
    ch = eta ** 2 * (1 + SQ2) / 2 - eta
    estar = 2 / (1 + SQ2)
    ac.axhline(0, color=INK, lw=0.6)
    ac.fill_between(eta, ch, 0, where=ch > 0, color=PLUM, alpha=0.15, lw=0)
    ac.plot(eta, ch, color=PLUM, lw=1.3)
    ac.plot([estar], [0], marker="o", ms=3.4, color=PLUM)
    ac.annotate("$\\eta^*=2/(1+\\sqrt{2})$\n$\\approx 0.8284$", xy=(estar, 0), xytext=(0.915, -0.09), fontsize=6.6, color=PLUM,
                ha="center", arrowprops=dict(arrowstyle="-", lw=0.5, color=PLUM))
    ac.text(0.62, 0.03, "local model\nexists", fontsize=6.4, color=MUTE)
    ac.text(0.99, 0.012, "no local\nmodel", fontsize=6.4, color=PLUM, ha="right", va="bottom")
    ac.set_xlabel("detection efficiency $\\eta$")
    ac.set_ylabel("CH functional")
    ac.set_xlim(0.6, 1.0)
    panel_label(ac, "c", x=-0.13)
    save(fig, "fig4_frontiers")


# ----------------------------------------------------------------- Figure 5: Le Cam deficiency
def fig_lecam():
    fig, (aa, ab) = plt.subplots(1, 2, figsize=(TEXTWIDTH, 2.55), gridspec_kw=dict(wspace=0.3, width_ratios=[1.2, 1.0]))
    C = 1 / SQ2
    lam = np.linspace(0, 1, 300)
    delta = C * (1 - lam) / (2 * (2 - C * lam))
    ident = C * (1 - lam) / 2
    naive = C * (1 - lam) / 4
    detmax = np.minimum(C * (1 - lam) / 2, 0.25)
    aa.fill_between(lam, naive, delta, color=SHADE, lw=0)
    aa.plot(lam, ident, color=MUTE, lw=0.9, ls=(0, (3, 2)), label="identity kernel $C(1-\\lambda)/2$")
    aa.plot(lam, detmax, color=RUST, lw=1.1, label="deterministic, worst setting")
    cs, pis, Cq = lc.canonical_schedule()
    grid = [Fr(k, 16) for k in range(17)]
    davg = []
    for g in grid:
        _w, b = lc.det_values(cs, pis, Cq, g)
        davg.append(float(b))
    aa.plot([float(g) for g in grid], davg, ls="none", marker="o", ms=2.6, mfc="white", mec=RUST, mew=0.7,
            label="deterministic, averaged (exact)")
    aa.plot(lam, delta, color=BLUE, lw=1.6, label="Le Cam deficiency $\\delta$")
    aa.plot(lam, naive, color=INK, lw=0.7, ls=(0, (1, 1.5)), label="two-point bound $C(1-\\lambda)/4$")
    lo, hi = 2.218 / (2 * SQ2), 2.626 / (2 * SQ2)
    aa.axvspan(lo, hi, color=GOLD, alpha=0.12, lw=0)
    aa.text((lo + hi) / 2, 0.2, "Delft $\\pm1\\sigma$", fontsize=6.0, color="#8a6512", ha="center", va="center", rotation=90)
    aa.set_xlabel("simulator visibility $\\lambda$")
    aa.set_ylabel("deficiency (TV)")
    aa.set_xlim(0, 1)
    aa.set_ylim(0, 0.6)
    aa.set_yticks([0, 0.1, 0.2, 0.3, 0.4, 0.5])
    aa.legend(loc="upper left", bbox_to_anchor=(0.0, 1.02), fontsize=6.0, handlelength=1.5, borderaxespad=0.0, labelspacing=0.25)
    panel_label(aa, "a", x=-0.1)

    lamv = 0.5
    A = (0.0, C * (1 - lamv) / 2)
    B = (0.25, (1 - lamv * C) / 4)
    Dp = (0.5, (1 - C) / 2)
    s = C * (1 - lamv) / (2 - C * lamv)
    R = (s / 2, s / 2)
    ab.plot([A[0], Dp[0]], [A[1], Dp[1]], color=RUST, lw=1.0, zorder=2)
    for P, name, off, ha in ((A, "$R_1$", (0.012, 0.01), "left"), (B, "$R_2$", (0.0, -0.03), "center"), (Dp, "$R_3$", (0.0, 0.014), "center")):
        ab.plot([P[0]], [P[1]], marker="o", ms=4, color=RUST, zorder=4)
        ab.text(P[0] + off[0], P[1] + off[1], name, fontsize=7.2, color=RUST, ha=ha, va="bottom")
    t = np.linspace(0, 0.5, 10)
    ab.plot(t, t, color=MUTE, lw=0.5, ls=(0, (2, 2)))
    # randomized optimal kernel: mixing laws inside one setting
    mix = [(u * 0.5, abs(C * (1 - lamv) - u * (1 - lamv * C)) / 2) for u in np.linspace(0, 1, 50)]
    ab.plot([m[0] for m in mix], [m[1] for m in mix], color=BLUE, lw=1.2, zorder=3)
    ab.plot([R[0]], [R[1]], marker="*", ms=8, color=BLUE, zorder=5)
    hull = (1 - lamv) / (2 * (2 - lamv))
    ab.plot([hull], [hull], marker="o", ms=3.5, mfc="white", mec=RUST, mew=0.8, zorder=5)
    ab.annotate(f"$\\delta={s / 2:.4f}$", xy=R, xytext=(0.03, 0.03), fontsize=6.8, color=BLUE,
                arrowprops=dict(arrowstyle="-", lw=0.5, color=BLUE))
    ab.annotate(f"setting-preserving\ndeterministic, avg. $\\geq 1/6$", xy=(hull, hull), xytext=(0.29, 0.225), fontsize=6.4, color=RUST, ha="left",
                arrowprops=dict(arrowstyle="-", lw=0.5, color=RUST))
    ab.text(0.525, 0.002, "mixing kernels\n(identity / overwrite)", fontsize=6.0, color=BLUE, ha="right", va="bottom")
    ab.set_xlabel("error at $v=0$")
    ab.set_ylabel("error at $v=1$")
    ab.set_xlim(-0.01, 0.53)
    ab.set_ylim(-0.005, 0.27)
    ab.set_title("canonical CHSH, $\\lambda=1/2$", fontsize=8, pad=3)
    panel_label(ab, "b", x=-0.12)
    save(fig, "fig5_lecam")


# ----------------------------------------------------------------- Figure 6: Delft evidence
def fig_delft(d):
    fig, (aa, ab) = plt.subplots(1, 2, figsize=(TEXTWIDTH, 2.45), gridspec_kw=dict(wspace=0.3))
    path = rd.running_chsh(d["trials"])
    n = np.array([p[0] for p in path])
    S = np.array([p[1] for p in path])
    err = np.array([p[2] for p in path])
    aa.fill_between(n, S - err, S + err, color=RUST, alpha=0.15, lw=0)
    aa.plot(n, S, color=RUST, lw=1.0)
    aa.axhline(2, color=BLUE, lw=0.8)
    aa.axhline(2 * SQ2, color=INK, lw=0.6, ls=(0, (3, 2)))
    aa.axhline(2.5, color=GOLD, lw=0.8, ls=(0, (1, 1.5)))
    aa.text(250, 2 * SQ2 + 0.03, "$2\\sqrt{2}$", fontsize=6.8, ha="right")
    aa.text(250, 2.0 - 0.13, "local $S=2$", fontsize=6.8, ha="right", color=BLUE)
    aa.text(250, 2.5 + 0.03, "$D=32$ renderer, $5/2$", fontsize=6.8, ha="right", color="#8a6512")
    aa.set_xlabel("valid trials $n$")
    aa.set_ylabel("running $S_n \\pm 1\\sigma$")
    aa.set_ylim(1.0, 3.6)
    aa.set_xlim(0, 252)
    panel_label(aa, "a", x=-0.1)

    wins = be.load_delft()
    pref = be.prefix_counts(wins)
    f = Fr(3, 4)
    mix = [float(be.uniform_mixture_e_value(k, m, f)) for k, m in pref]
    mixxi = [float(be.uniform_mixture_e_value(k, m, be.XI)) for k, m in pref]
    ceil = [float(be.constant_bet_ceiling(k, m, f)) for k, m in pref]
    nn = np.arange(1, len(wins) + 1)
    ab.plot(nn, ceil, color=TEAL, lw=1.0, label="constant-bet ceiling $U_n(3/4)$")
    ab.plot(nn, mix, color=BLUE, lw=1.2, label="uniform mixture, $f=3/4$")
    ab.plot(nn, mixxi, color=BLUE, lw=0.6, ls=(0, (2, 1.5)), label="uniform mixture, $f=\\xi$")
    ab.axhline(20, color=INK, lw=0.8)
    ab.text(4, 21.5, "$1/\\alpha=20$", fontsize=6.8)
    imax = int(np.argmax(ceil))
    ab.plot([nn[imax]], [ceil[imax]], marker="o", ms=3.2, color=TEAL)
    ab.annotate(f"max {ceil[imax]:.2f} at $n={nn[imax]}$", xy=(nn[imax], ceil[imax]), xytext=(150, 11.5), fontsize=6.6, color=TEAL,
                arrowprops=dict(arrowstyle="-", lw=0.5, color=TEAL))
    ab.plot([245], [25.53], marker="x", ms=4.5, mew=1.0, color=RUST)
    ab.text(242, 30, "$1/p=25.5$ (fixed $n$; not an e-value)", fontsize=6.4, color=RUST, ha="right")
    ab.set_yscale("log")
    ab.set_ylim(0.02, 80)
    ab.set_xlim(0, 252)
    ab.set_xlabel("valid trials $n$ (timestamp order)")
    ab.set_ylabel("e-value")
    ab.legend(loc="lower right", fontsize=6.2, handlelength=1.6, borderaxespad=0.2)
    panel_label(ab, "b", x=-0.1)
    save(fig, "fig6_delft")


def main():
    d = delft()
    print("Delft q =", d["q"], "S =", d["S"], "cov =", d["cov"].tolist(), "n =", d["n"])
    fig_disk(d)
    fig_precision()
    fig_zonoid()
    fig_frontiers()
    fig_lecam()
    fig_delft(d)


if __name__ == "__main__":
    main()
