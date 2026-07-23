"""Matplotlib renderer for M9 instrumentation panels."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from .instrumentation import Panel


def _format_value(value: float | int | bool) -> str:
    if isinstance(value, bool):
        return "PASS" if value else "FAIL"
    if isinstance(value, int):
        return str(value)
    magnitude = abs(value)
    if magnitude != 0.0 and (magnitude < 1.0e-3 or magnitude >= 1.0e4):
        return f"{value:.5e}"
    return f"{value:.8g}"


def render_panel(panel: Panel, output_path: str | Path) -> Path:
    import matplotlib

    matplotlib.use("Agg", force=True)
    import matplotlib.pyplot as plt

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    figure = plt.figure(figsize=(10, 7), constrained_layout=True)
    axis = figure.add_subplot(111)
    axis.axis("off")
    status = "PASS" if panel.passed else "FAIL"
    lines = [
        panel.title,
        f"Sector: {panel.sector}    Task: {panel.task}    Status: {status}",
        f"Acceptance: {panel.acceptance_passed}/{panel.acceptance_total}",
        "",
        "Metrics",
    ]
    lines.extend(f"  {label}: {_format_value(value)}" for label, value in panel.metrics)
    lines.extend(("", "Established"))
    lines.extend(f"  • {statement}" for statement in panel.establishes)
    lines.extend(("", "Not established"))
    lines.extend(f"  • {statement}" for statement in panel.does_not_establish)
    axis.text(0.02, 0.98, "\n".join(lines), va="top", family="monospace", fontsize=11)
    figure.savefig(path, dpi=150)
    plt.close(figure)
    return path


def show_dashboard(panels: Sequence[Panel]) -> None:
    import matplotlib.pyplot as plt

    count = len(panels)
    figure, axes = plt.subplots(count, 1, figsize=(11, max(5, 4 * count)), squeeze=False)
    for axis, panel in zip(axes[:, 0], panels, strict=True):
        axis.axis("off")
        status = "PASS" if panel.passed else "FAIL"
        lines = [
            f"{panel.title} — {status}",
            f"Acceptance {panel.acceptance_passed}/{panel.acceptance_total}",
        ]
        lines.extend(f"{label}: {_format_value(value)}" for label, value in panel.metrics)
        lines.append("Not established:")
        lines.extend(f"• {item}" for item in panel.does_not_establish)
        axis.text(0.01, 0.99, "\n".join(lines), va="top", family="monospace")
    figure.suptitle("OpenWave M9 research instrumentation")
    plt.show()
