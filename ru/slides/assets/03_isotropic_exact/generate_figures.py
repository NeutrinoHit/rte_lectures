#!/usr/bin/env python3
"""Figures for lecture 3: which light reaches 50-300 m from an isotropic flash.

Data (laser_data.npz): exact orders from the continued fraction of the lecture
(stationary, HG g=0.9) and a photon Monte Carlo (HG scattering, absorption as a
weight, first crossing of a sphere of radius R). Medium: mu_a=0.020, mu_s=0.022 1/m.
Run from any directory with Python + NumPy + Matplotlib.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.patches import Arc, FancyArrowPatch
import numpy as np

OUT = Path(__file__).resolve().parent
D = np.load(OUT / "laser_data.npz")
BLUE, GOLD, GREEN, RED = "#7cc7ff", "#ffcc8a", "#75ddb8", "#ff9ab0"
INK, MUTED = "#f2f2f2", "#b8c7d1"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 17,
    "text.color": INK, "axes.labelcolor": INK, "xtick.color": MUTED,
    "ytick.color": MUTED, "axes.edgecolor": MUTED,
    "axes.facecolor": "#000000", "figure.facecolor": "#000000",
    "savefig.facecolor": "#000000", "svg.fonttype": "path",
    "axes.spines.top": False, "axes.spines.right": False,
    "svg.hashsalt": "isotropic-source-lecture-03",
})
MUS = 0.022


def save(fig, name):
    fig.savefig(OUT / name, metadata={"Date": None}, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)


def orders():
    r, q, mean = D["ord_r"], D["ord_q"], D["ord_mean"]
    share = q / q.sum(axis=0)
    groups = [("0", share[0], MUTED), ("1", share[1], BLUE), ("2", share[2], GREEN),
              ("3", share[3], GOLD), ("4–5", share[4:6].sum(0), RED),
              ("≥6", share[6:].sum(0), "#c9a7ff")]
    fig, (a, b) = plt.subplots(1, 2, figsize=(14, 5.4), gridspec_kw={"width_ratios": [1.35, 1]})
    bottom = np.zeros_like(r)
    for lab, y, c in groups:
        a.fill_between(r, bottom, bottom + y, color=c, alpha=0.9, lw=0, label=lab)
        bottom = bottom + y
    a.set_xlim(r[0], r[-1]); a.set_ylim(0, 1)
    a.set_xlabel("расстояние $r$, м"); a.set_ylabel("доля флюенса")
    a.legend(title="число рассеяний", ncol=3, frameon=False, fontsize=14, title_fontsize=14,
             loc="upper center", bbox_to_anchor=(0.5, 1.28))
    x = MUS * r
    b.plot([0, 10], [0, 10], color=MUTED, lw=1.5, ls="--", label="$\\mu_s r$")
    b.plot(x, mean, color=GOLD, lw=3, marker="o", ms=7, label="по порядкам флюенса")
    b.set_xlim(0, 9); b.set_ylim(0, 9)
    b.set_xlabel("$\\mu_s r$"); b.set_ylabel("среднее число рассеяний")
    b.legend(frameon=False, fontsize=14, loc="upper left")
    fig.tight_layout(); save(fig, "orders.svg")


def quantiles(h, rb, qs):
    c = np.cumsum(h, axis=1); c = c / c[:, -1:]
    return np.array([[np.interp(q, c[k], rb[1:]) for q in qs] for k in range(len(h))])


def tube():
    zb, rb = D["tube_zb"], D["tube_rb"]
    z = 0.5 * (zb[1:] + zb[:-1]) * 250.0
    q = {t: quantiles(D[f"{t}_tube"], rb, (0.5, 0.9)) for t in ("g09", "g00")}
    fig, axs = plt.subplots(1, 2, figsize=(14, 5.4), sharey=True)
    for ax, tag, title in ((axs[0], "g09", "HG, $g=0.9$"), (axs[1], "g00", "изотропное, $g=0$")):
        # Convert path length in cylindrical rings to path length per volume.
        # Equal longitudinal bin widths cancel in the per-section normalisation.
        ring_area = np.pi * np.diff(rb**2)
        h = D[f"{tag}_tube"] / ring_area[None, :]
        h = h / h.max(axis=1, keepdims=True)
        full = np.concatenate([h[:, ::-1], h], axis=1).T
        ax.imshow(full, origin="lower", extent=[0, 250, -rb[-1], rb[-1]], aspect="equal",
                  cmap="magma", vmin=0, vmax=1)
        for s in (1, -1):
            ax.plot(z, s * q[tag][:, 1], color=BLUE, lw=2.2, label="90% длины" if s == 1 else None)
            ax.plot(z, s * q[tag][:, 0], color=GREEN, lw=2.2, label="50% длины" if s == 1 else None)
        ax.scatter([0], [0], s=70, color=GOLD, zorder=5); ax.scatter([250], [0], s=70, color=BLUE, zorder=5)
        ax.set_title(title, fontsize=17, color=INK); ax.set_xlabel("вдоль хорды, м"); ax.set_xlim(0, 250)
    axs[0].set_ylabel("поперёк хорды, м"); axs[0].legend(frameon=False, fontsize=14, loc="upper right")
    fig.tight_layout(); save(fig, "tube.svg")


def spread():
    gr, gl = D["grid_rho"], D["grid_dl"]
    cols = {50: GREEN, 100: BLUE, 200: GOLD, 300: RED}
    fig, (a, b) = plt.subplots(1, 2, figsize=(14, 5.2))
    for R, c in cols.items():
        a.plot(gr * R, D[f"g09_cdf_rho_{R}"], color=c, lw=3, label=f"{R} м")
        a.plot(gr * R, D[f"g00_cdf_rho_{R}"], color=c, lw=2, ls="--")
        b.plot(gl, D[f"g09_cdf_dl_{R}"], color=c, lw=3)
        b.plot(gl, D[f"g00_cdf_dl_{R}"], color=c, lw=2, ls="--")
    a.set_xlim(0, 120); a.set_ylim(0, 1)
    a.set_xlabel("наибольшее боковое отклонение пути, м"); a.set_ylabel("доля света (накопленная)")
    a.legend(title="$R$", frameon=False, fontsize=14, title_fontsize=14, loc="lower right")
    b.set_xlim(0, 150); b.set_ylim(0, 1)
    b.set_xlabel("избыток длины пути $L-R$, м")
    b.plot([], [], color=INK, lw=3, label="$g=0.9$"); b.plot([], [], color=INK, lw=2, ls="--", label="$g=0$")
    b.legend(frameon=False, fontsize=14, loc="lower right")
    fig.tight_layout(); save(fig, "spread.svg")


def ellipsoid():
    """Meridional section of rho_1 + rho_2 = s, with the scattering angle."""
    r, s = 1.0, 1.2
    a, c = s / 2, r / 2
    b = np.sqrt(a*a - c*c)
    u = np.linspace(0, 2*np.pi, 600)
    source, receiver = np.array([0., 0.]), np.array([r, 0.])
    q = np.deg2rad(65)
    y = np.array([c + a*np.cos(q), b*np.sin(q)])
    incoming = y / np.linalg.norm(y)
    outgoing = (receiver - y) / np.linalg.norm(receiver - y)
    ai = np.rad2deg(np.arctan2(incoming[1], incoming[0]))
    ao = np.rad2deg(np.arctan2(outgoing[1], outgoing[0]))
    fig, ax = plt.subplots(figsize=(13, 5.0))
    ax.plot(c + a*np.cos(u), b*np.sin(u), color=BLUE, lw=2.5)
    ax.plot([-.16, 1.28], [0, 0], color=MUTED, lw=1, ls="--", alpha=.7)
    for start, end, color in ((source, y, GOLD), (y, receiver, GREEN)):
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=20,
                                    lw=3, color=color, shrinkA=6, shrinkB=6))
    extension = y + .28*incoming
    ax.plot([y[0], extension[0]], [y[1], extension[1]], color=GOLD, lw=1.8, ls="--")
    ax.add_patch(Arc(y, .24, .24, theta1=ao, theta2=ai, color=RED, lw=2.5))
    am = np.deg2rad((ai + ao)/2)
    ax.text(*(y + .175*np.array([np.cos(am), np.sin(am)])), r"$\theta$",
            color=RED, ha="center", va="center", fontsize=23)
    ax.add_patch(Arc(y, .16, .16, theta1=ai+180, theta2=ao+360, color=MUTED, lw=1.5))
    am_inner = np.deg2rad((ai+180+ao+360)/2)
    ax.text(*(y + .155*np.array([np.cos(am_inner), np.sin(am_inner)])), r"$\pi-\theta$",
            color=MUTED, ha="center", va="center", fontsize=18)
    ax.scatter([0, r, y[0]], [0, 0, y[1]], s=[75, 75, 65], color=[GOLD, BLUE, INK], zorder=5)
    ax.text(-.01, -.075, "источник\n$0$", ha="center", va="top", color=GOLD, fontsize=18)
    ax.text(1.04, -.075, "приёмник\n$\\mathbf{r}$", ha="center", va="top", color=BLUE, fontsize=18)
    ax.text(y[0]-.03, y[1]+.065, r"$\mathbf{y}$", fontsize=23)
    ax.text(.32, .195, r"$\rho_1$", color=GOLD, fontsize=23)
    ax.text(1.02, .18, r"$\rho_2$", color=GREEN, fontsize=23)
    ax.annotate("", xy=(r, -.24), xytext=(0, -.24),
                arrowprops={"arrowstyle": "<->", "color": MUTED, "lw": 1.5})
    ax.text(.5, -.275, "$r$", ha="center", va="top", color=MUTED, fontsize=20)
    ax.text(.5, .52, r"$\rho_1+\rho_2=s=v_gt>r$", ha="center", fontsize=25)
    ax.set_aspect("equal"); ax.set_xlim(-.2, 1.3); ax.set_ylim(-.39, .62); ax.axis("off")
    fig.tight_layout(); save(fig, "ellipsoid.svg")


if __name__ == "__main__":
    orders(); tube(); spread(); ellipsoid()
