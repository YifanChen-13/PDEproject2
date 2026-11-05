import csv
import os
from pathlib import Path

import numpy as np

from problem import EXACT_STAR, exact
from solver import solve

OUTPUT = Path(os.environ.get('PDE_STAGE1_OUTPUT', Path(__file__).parent))
OUTPUT.mkdir(parents=True, exist_ok=True)

rows = []
previous_error = None

for h in [0.5, 0.25, 0.125, 0.0625]:
    S, V, stats = solve(smax=400, h=h, stage=1, exact_boundary=True)

    value_error = float(np.max(np.abs(V - exact(S))))
    threshold_error = abs(stats["star"] - EXACT_STAR)
    order = (
        None if previous_error is None
        else np.log2(previous_error / value_error)
    )

    rows.append({
        "h": h,
        "value_error_Linf": value_error,
        "numerical_threshold": stats["star"],
        "threshold_error": threshold_error,
        "observed_value_order": order,
        "iterations": stats["iterations"],
        "lcp_residual": stats["lcp_residual"],
        "requested_tol": stats["requested_tol"],
        "tolerance_met": stats["met_requested_tol"],
    })
    previous_error = value_error

    order_text = "-" if order is None else f"{order:.4f}"
    print(
        f"h={h:<7g}  value error={value_error:.6e}  "
        f"S*={stats['star']:.6f}  threshold error={threshold_error:.6e}  "
        f"order={order_text}  tolerance met={stats['met_requested_tol']}"
    )

output = OUTPUT / "stage1_validation_results.csv"
with output.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)

print(f"\nSaved: {output}")

import matplotlib.pyplot as plt

V_exact = exact(S)
payoff = np.maximum(100 - S, 0)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

# Left: compare the option values and the exercise payoff.
ax1.plot(S, V_exact, color="black", label="Exact value")
ax1.plot(S, V, "--", color="tab:blue", label="Numerical value")
ax1.plot(S, payoff, ":", color="tab:orange", label="Exercise payoff")
ax1.set(xlim=(0, 200), xlabel="Asset price S", ylabel="Option value",
        title="Stage 1: constant volatility")
ax1.legend()

# Right: subtract the payoff to make the exercise region visible.
near = (S >= 69) & (S <= 74)
ax2.plot(S[near], (V_exact - payoff)[near], color="black", label="Exact gap")
ax2.plot(S[near], (V - payoff)[near], "--", color="tab:blue", label="Numerical gap")
ax2.axvline(EXACT_STAR, color="black", linestyle=":", label="Exact threshold")
ax2.axvline(stats["star"], color="tab:red", linestyle="--", label="Last contact node")
ax2.set(xlabel="Asset price S", ylabel="Option value minus payoff",
        title="Near the exercise threshold")
ax2.legend(fontsize=8)

for ax in (ax1, ax2):
    ax.grid(alpha=0.25)

fig.tight_layout()
figure_path = OUTPUT / "stage1_value_comparison.png"
fig.savefig(figure_path, dpi=300, bbox_inches="tight")
plt.close(fig)
print(f"Saved figure: {figure_path}")