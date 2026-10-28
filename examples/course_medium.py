"""Monochromatic optical model used in the first three RTE lectures."""
from pathlib import Path
import argparse
import json

import lighthit as lh
import numpy as np


def baikal_450():
    """BaikalWater sample at 450 nm; HG g=0.9 is the LightHit model choice.

    Coefficients were checked against the optical model used by LightHit and
    NTSim on 2026-10-22, on its 350--600 nm grid with 10 nm steps. This single
    band does not represent a wavelength-averaged calibration.
    """
    return lh.Medium(0.076, 0.019, 0.9, 1.3713237239062512, 450.0,
                     "BaikalWater at 450 nm; HG g=0.9")


def arguments(description, default_output):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--output", type=Path, default=Path(default_output))
    parser.add_argument("--refine", action="store_true",
                        help="increase harmonic degree and spatial quadrature")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    return args


def solver_settings(refine=False):
    # Isotropic emission needs only spatial degree zero. Numerical accuracy
    # must be checked by changing harmonic degree, cutoff and panel width.
    return lh.SolverSettings(
        scattering_degree=96 if refine else 64, spatial_degree=0,
        k_max_per_m=12.0 if refine else 8.0,
        k_panel_per_m=0.025 if refine else 0.04,
        k_order=10 if refine else 8)


def write_json(path, data):
    text = json.dumps(data, ensure_ascii=False, indent=2)
    Path(path).write_text(text + "\n", encoding="utf-8")
    print(text)


def plotting():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 15, "figure.facecolor": "black",
                         "axes.facecolor": "black", "text.color": "white",
                         "axes.labelcolor": "white", "axes.edgecolor": "#b8c7d1",
                         "xtick.color": "#b8c7d1", "ytick.color": "#b8c7d1",
                         "svg.fonttype": "path", "svg.hashsalt": "rte-practice"})
    return plt


def save_figure(fig, path):
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", metadata={"Date": None})
