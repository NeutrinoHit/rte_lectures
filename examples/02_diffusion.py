"""Lecture 2: stationary fluence from an isotropic flash, RTE versus diffusion."""
import numpy as np
import lighthit as lh

from course_medium import arguments, baikal_450, plotting, save_figure, solver_settings, write_json


def main():
    args = arguments(__doc__, ".work/practice/02_diffusion")
    medium = baikal_450()
    radii = np.array([10., 20., 30., 40., 50., 60.])
    positions = np.column_stack((radii, np.zeros((len(radii), 2))))
    solver = lh.PointGreenSolver(medium, solver_settings(args.refine),
                                angular_backend="numpy", single_backend="numpy")
    result = solver.solve([0.0], positions, direction=None, photons=1.0)
    exact = result.charge_per_m2  # omega=0 is time-integrated scalar fluence.
    diffusion = medium.speed_m_per_ns / (3 * medium.scattering_per_m * (1 - medium.g))
    alpha = medium.speed_m_per_ns * medium.absorption_per_m
    approx = (medium.speed_m_per_ns / (4 * np.pi * diffusion * radii)
              * np.exp(-radii * np.sqrt(alpha / diffusion)))
    np.savetxt(args.output / "fluence.csv", np.column_stack((radii, exact, approx)),
               delimiter=",", header="radius_m,rte_per_m2,diffusion_per_m2", comments="")
    write_json(args.output / "summary.json", {
        "D_m2_per_ns": diffusion, "alpha_per_ns": alpha,
        "mu_a_over_mu_s_prime": medium.absorption_per_m / (medium.scattering_per_m * (1 - medium.g)),
        "radius_m": radii.tolist(), "rte_per_m2": exact.tolist(),
        "diffusion_per_m2": approx.tolist(), "diffusion_over_rte": (approx / exact).tolist(),
        "refined": args.refine,
    })
    plt = plotting(); fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.semilogy(radii, exact, "o-", color="#7cc7ff", lw=2.5, label="LightHit: RTE")
    ax.semilogy(radii, approx, "s--", color="#ffcc8a", lw=2.5, label="диффузия")
    ax.set_xlabel("расстояние, м"); ax.set_ylabel(r"$F/N$, м$^{-2}$")
    ax.set_title("BaikalWater, 450 нм; HG g=0.9")
    ax.legend(); ax.grid(alpha=.2); save_figure(fig, args.output / "diffusion.svg")


if __name__ == "__main__":
    main()
