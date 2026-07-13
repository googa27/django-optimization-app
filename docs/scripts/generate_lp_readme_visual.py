"""Generate README visuals for the sample two-product LP.

The script is deliberately small and reproducible: it reads the checked-in sample
CSV, derives the feasible vertices from the same two machine constraints used by
``optimizador.optimizer.OptimizationModel``, and renders a dark GitHub-safe plot.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CSV = ROOT / "revenew_proj" / "optimization_problem_data.csv"
DEFAULT_PNG = ROOT / "docs" / "assets" / "lp_feasible_region_sample_dark.png"
DEFAULT_SVG = ROOT / "docs" / "assets" / "lp_formulation_card_dark.svg"
DEFAULT_JSON = ROOT / "docs" / "assets" / "lp_feasible_region_sample_provenance.json"

COLORS = {
    "bg": "#0d1117",
    "panel": "#161b22",
    "grid": "#30363d",
    "text": "#c9d1d9",
    "muted": "#8b949e",
    "cyan": "#65d6ff",
    "purple": "#b46cff",
    "magenta": "#ff4fd8",
    "green": "#3fb950",
    "orange": "#f97316",
    "red": "#f85149",
}


@dataclass(frozen=True)
class Problem:
    a1: float
    b1: float
    cap1: float
    a2: float
    b2: float
    cap2: float
    price_a: float
    price_b: float

    @property
    def objective_label(self) -> str:
        return f"max {self.price_a:g} A + {self.price_b:g} B"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def load_problem(path: Path) -> Problem:
    with path.open(newline="") as fh:
        row = next(csv.DictReader(fh))
    return Problem(
        a1=float(row["Product_A_Production_Time_Machine_1"]),
        b1=float(row["Product_B_Production_Time_Machine_1"]),
        cap1=float(row["Machine_1_Available_Hours"]),
        a2=float(row["Product_A_Production_Time_Machine_2"]),
        b2=float(row["Product_B_Production_Time_Machine_2"]),
        cap2=float(row["Machine_2_Available_Hours"]),
        price_a=float(row["Price_Product_A"]),
        price_b=float(row["Price_Product_B"]),
    )


def feasible(problem: Problem, point: tuple[float, float], tol: float = 1e-9) -> bool:
    a, b = point
    return (
        a >= -tol
        and b >= -tol
        and problem.a1 * a + problem.b1 * b <= problem.cap1 + tol
        and problem.a2 * a + problem.b2 * b <= problem.cap2 + tol
    )


def candidate_vertices(problem: Problem) -> list[tuple[float, float]]:
    candidates: list[tuple[float, float]] = [(0.0, 0.0)]
    if problem.a1 > 0:
        candidates.append((problem.cap1 / problem.a1, 0.0))
    if problem.a2 > 0:
        candidates.append((problem.cap2 / problem.a2, 0.0))
    if problem.b1 > 0:
        candidates.append((0.0, problem.cap1 / problem.b1))
    if problem.b2 > 0:
        candidates.append((0.0, problem.cap2 / problem.b2))

    det = problem.a1 * problem.b2 - problem.a2 * problem.b1
    if abs(det) > 1e-12:
        a = (problem.cap1 * problem.b2 - problem.cap2 * problem.b1) / det
        b = (problem.a1 * problem.cap2 - problem.a2 * problem.cap1) / det
        candidates.append((a, b))

    unique: list[tuple[float, float]] = []
    for point in candidates:
        if feasible(problem, point) and not any(
            abs(point[0] - seen[0]) < 1e-8 and abs(point[1] - seen[1]) < 1e-8
            for seen in unique
        ):
            unique.append((max(point[0], 0.0), max(point[1], 0.0)))
    return sorted(unique)


def solve(problem: Problem) -> tuple[tuple[float, float], float, list[tuple[float, float]]]:
    vertices = candidate_vertices(problem)
    scored = [(point, problem.price_a * point[0] + problem.price_b * point[1]) for point in vertices]
    optimum, value = max(scored, key=lambda item: item[1])
    return optimum, value, vertices


def _style_axis(ax: plt.Axes) -> None:
    ax.set_facecolor(COLORS["panel"])
    ax.grid(color=COLORS["grid"], alpha=0.55, linewidth=0.7)
    for spine in ax.spines.values():
        spine.set_color(COLORS["grid"])
    ax.tick_params(colors=COLORS["text"])
    ax.xaxis.label.set_color(COLORS["text"])
    ax.yaxis.label.set_color(COLORS["text"])


def render_png(problem: Problem, output: Path) -> dict[str, object]:
    output.parent.mkdir(parents=True, exist_ok=True)
    optimum, value, vertices = solve(problem)
    max_a = max(v[0] for v in vertices + [optimum, (problem.cap1 / problem.a1, 0), (problem.cap2 / problem.a2, 0)])
    max_b = max(v[1] for v in vertices + [optimum, (0, problem.cap1 / problem.b1), (0, problem.cap2 / problem.b2)])
    x_max = max_a * 1.18 + 0.2
    y_max = max_b * 1.18 + 0.2
    x = np.linspace(0.0, x_max, 600)
    y1 = (problem.cap1 - problem.a1 * x) / problem.b1
    y2 = (problem.cap2 - problem.a2 * x) / problem.b2
    y_feasible = np.maximum(0.0, np.minimum(y1, y2))

    fig, ax = plt.subplots(figsize=(12.8, 7.6), dpi=300)
    fig.patch.set_facecolor(COLORS["bg"])
    _style_axis(ax)
    ax.fill_between(
        x,
        0.0,
        y_feasible,
        where=(y1 >= 0) & (y2 >= 0),
        color=COLORS["green"],
        alpha=0.18,
        label="feasible region",
    )
    ax.plot(x, y1, color=COLORS["cyan"], lw=2.5, label=f"M1: {problem.a1:g}A + {problem.b1:g}B <= {problem.cap1:g}")
    ax.plot(x, y2, color=COLORS["purple"], lw=2.5, label=f"M2: {problem.a2:g}A + {problem.b2:g}B <= {problem.cap2:g}")
    ax.plot([v[0] for v in vertices], [v[1] for v in vertices], "o", color=COLORS["green"], ms=6)

    opt_a, opt_b = optimum
    ax.scatter([opt_a], [opt_b], s=145, color=COLORS["green"], edgecolor=COLORS["text"], zorder=5)
    ax.annotate(
        f"verified optimum\nA={opt_a:.2f}, B={opt_b:.2f}\nrevenue=${value:.2f}",
        xy=optimum,
        xytext=(34, -12),
        textcoords="offset points",
        color=COLORS["green"],
        fontsize=11,
        weight="bold",
        arrowprops={"arrowstyle": "->", "color": COLORS["green"], "lw": 1.4},
    )

    old = (4.0, 2.0)
    ax.scatter([old[0]], [old[1]], s=100, marker="x", color=COLORS["red"], lw=3, zorder=6)
    ax.annotate(
        "old README point\ninfeasible: M2 uses 11 > 10",
        xy=old,
        xytext=(-130, 40),
        textcoords="offset points",
        color=COLORS["red"],
        fontsize=10,
        arrowprops={"arrowstyle": "->", "color": COLORS["red"], "lw": 1.2},
    )

    # Objective iso-revenue line through optimum.
    b_line = (value - problem.price_a * x) / problem.price_b
    ax.plot(x, b_line, color=COLORS["orange"], lw=2.0, ls="--", label=f"objective at optimum: {problem.objective_label}")
    ax.annotate(
        "objective line",
        xy=(min(x_max * 0.55, x[-1]), np.interp(min(x_max * 0.55, x[-1]), x, b_line)),
        xytext=(10, 18),
        textcoords="offset points",
        color=COLORS["orange"],
        fontsize=10,
    )

    ax.set_xlim(-0.12, x_max)
    ax.set_ylim(0.0, y_max)
    ax.set_xlabel("Product A units")
    ax.set_ylabel("Product B units")
    ax.set_title("Sample LP feasible region and objective", color=COLORS["text"], fontsize=16, weight="bold")
    ax.legend(loc="upper right", facecolor=COLORS["panel"], edgecolor=COLORS["grid"], labelcolor=COLORS["text"], fontsize=9)
    caption = (
        "Source: revenew_proj/optimization_problem_data.csv and optimizador.optimizer constraints. "
        "Continuous LP demo, not integer production planning. The prior A=4, B=2 example violates Machine 2."
    )
    fig.text(
        0.01,
        0.015,
        caption,
        color=COLORS["muted"],
        fontsize=9,
        bbox={"facecolor": COLORS["panel"], "edgecolor": COLORS["grid"], "boxstyle": "round,pad=0.4"},
    )
    fig.savefig(output, bbox_inches="tight", pad_inches=0.24, facecolor=fig.get_facecolor())
    plt.close(fig)
    return {"optimum": {"Product_A": opt_a, "Product_B": opt_b, "Total_Revenue": value}, "vertices": vertices}


def render_svg(problem: Problem, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="980" height="300" viewBox="0 0 980 300" role="img" aria-labelledby="title desc">
  <title id="title">LP formulation card</title>
  <desc id="desc">Dark safe card listing the two-product revenue maximization objective, two machine constraints, non-negativity, and the source CSV.</desc>
  <rect width="980" height="300" fill="{COLORS['bg']}"/>
  <rect x="28" y="28" width="924" height="244" rx="18" fill="{COLORS['panel']}" stroke="{COLORS['grid']}" stroke-width="2"/>
  <text x="54" y="68" fill="{COLORS['text']}" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="24" font-weight="700">Source-verified LP formulation</text>
  <text x="54" y="105" fill="{COLORS['orange']}" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="20">maximize  {problem.price_a:g} A + {problem.price_b:g} B</text>
  <text x="54" y="145" fill="{COLORS['cyan']}" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="18">Machine 1: {problem.a1:g} A + {problem.b1:g} B &lt;= {problem.cap1:g}</text>
  <text x="54" y="180" fill="{COLORS['purple']}" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="18">Machine 2: {problem.a2:g} A + {problem.b2:g} B &lt;= {problem.cap2:g}</text>
  <text x="54" y="215" fill="{COLORS['green']}" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="18">A &gt;= 0, B &gt;= 0; continuous variables from PuLP LpVariable(lowBound=0)</text>
  <text x="54" y="250" fill="{COLORS['muted']}" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="13">Source: revenew_proj/optimization_problem_data.csv and revenew_proj/optimizador/optimizer.py. CLI route is documented separately because main.py is not verified.</text>
</svg>
'''
    output.write_text(svg)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--png", type=Path, default=DEFAULT_PNG)
    parser.add_argument("--svg", type=Path, default=DEFAULT_SVG)
    parser.add_argument("--provenance", type=Path, default=DEFAULT_JSON)
    args = parser.parse_args(argv)

    problem = load_problem(args.csv)
    result = render_png(problem, args.png)
    render_svg(problem, args.svg)
    args.provenance.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "reproducibility": "deterministic_from_tracked_fixture",
        "script": str(Path(__file__).relative_to(ROOT)),
        "script_sha256": _sha256(Path(__file__)),
        "source_csv": str(args.csv.relative_to(ROOT)),
        "source_csv_sha256": _sha256(args.csv),
        "optimizer_source": "revenew_proj/optimizador/optimizer.py",
        "assets": [str(args.png.relative_to(ROOT)), str(args.svg.relative_to(ROOT))],
        **result,
        "old_readme_example": {
            "Product_A": 4.0,
            "Product_B": 2.0,
            "Machine_1_Usage": problem.a1 * 4.0 + problem.b1 * 2.0,
            "Machine_2_Usage": problem.a2 * 4.0 + problem.b2 * 2.0,
            "status": "infeasible because Machine_2_Usage exceeds cap 10",
        },
    }
    args.provenance.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
