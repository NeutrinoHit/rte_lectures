"""Lecture 1: optical lengths, photon survival and a directed flash's centre."""
import numpy as np

from course_medium import arguments, baikal_450, plotting, save_figure, write_json


def main():
    args = arguments(__doc__, ".work/practice/01_medium")
    medium = baikal_450()
    v = medium.speed_m_per_ns
    mu_tr = medium.scattering_per_m * (1 - medium.g)
    length_tr = 1 / mu_tr
    time_ns = np.linspace(0, 6 * length_tr / v, 301)
    # Exact global moments from lecture 1, normalised to surviving photons.
    survival = np.exp(-medium.absorption_per_m * v * time_ns)
    centre = -np.expm1(-mu_tr * v * time_ns) / mu_tr
    np.savetxt(args.output / "moments.csv", np.column_stack((time_ns, survival, centre)),
               delimiter=",", header="time_ns,survival,centre_m", comments="")
    write_json(args.output / "summary.json", {
        "wavelength_nm": medium.wavelength_nm,
        "mu_a_per_m": medium.absorption_per_m, "mu_s_per_m": medium.scattering_per_m,
        "g": medium.g, "group_index": medium.group_index,
        "speed_m_per_ns": v, "absorption_length_m": 1 / medium.absorption_per_m,
        "scattering_length_m": 1 / medium.scattering_per_m,
        "transport_length_m": length_tr,
        "mu_a_over_mu_s_prime": medium.absorption_per_m / mu_tr,
        "survival_at_100_m": float(np.exp(-medium.absorption_per_m * 100)),
    })
    plt = plotting()
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(time_ns * v / length_tr, centre / length_tr, color="#ffcc8a", lw=3)
    ax.set_xlabel(r"$v_gt/\ell_*$"); ax.set_ylabel(r"$\langle z\rangle/\ell_*$")
    ax.set_title("Центр направленной вспышки: условие выживания")
    ax.grid(alpha=.2); save_figure(fig, args.output / "centre.svg")


if __name__ == "__main__":
    main()
