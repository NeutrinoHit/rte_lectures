"""Lecture 3: isotropic flash, collision orders, time bins and a simple receiver."""
import numpy as np
import lighthit as lh

from course_medium import arguments, baikal_450, plotting, save_figure, solver_settings, write_json


def main():
    args = arguments(__doc__, ".work/practice/03_flash")
    medium = baikal_450()
    radius, photons = 30.0, 1e8
    omega = np.linspace(0, 1.2, 321 if not args.refine else 641)
    solver = lh.PointGreenSolver(medium, solver_settings(args.refine),
                                angular_backend="numpy", single_backend="numpy")
    result = solver.solve(omega, [[radius, 0, 0]], direction=None, photons=photons)
    front = float(result.front_time_ns[0])
    edges = front + np.arange(-20., 405., 5.)
    profile = result.readout(edges, sigma_ns=0.0)
    # An idealised isotropic receiver: constant area and efficiency. A real OM
    # additionally requires its measured angular and spectral response.
    area_m2, efficiency = 0.13, 0.20
    charge_orders = result.components[0, 0].real * area_m2 * efficiency
    bins = profile.components[0] * area_m2 * efficiency
    np.savetxt(args.output / "bins.csv", np.column_stack((edges[:-1], edges[1:], bins)),
               delimiter=",", header="left_ns,right_ns,pe_order0,pe_order1,pe_ge2", comments="")
    result.save(args.output / "spectrum.npz")
    write_json(args.output / "summary.json", {
        "photons": photons, "radius_m": radius, "front_time_ns": front,
        "area_m2": area_m2, "efficiency": efficiency,
        "charge_pe_orders_0_1_ge2": charge_orders.tolist(),
        "window_pe_orders_0_1_ge2": bins.sum(axis=0).tolist(),
        "diagnostics": profile.diagnostics, "refined": args.refine,
    })
    plt = plotting(); fig, ax = plt.subplots(figsize=(10, 4.5))
    for index, label, colour in ((0, "0: прямой", "#b8c7d1"),
                                 (1, "1: однократный", "#7cc7ff"),
                                 (2, "≥2: многократный", "#ffcc8a")):
        ax.stairs(bins[:, index], edges-front, color=colour, lw=2, label=label)
    ax.set_xlabel("задержка относительно прямого света, нс")
    ax.set_ylabel("ожидаемое число ф.э. в бине 5 нс")
    ax.set_title("Изотропная вспышка; BaikalWater, 450 нм; приёмник учебный")
    ax.legend(); ax.grid(alpha=.2); save_figure(fig, args.output / "flash.svg")


if __name__ == "__main__":
    main()
