"""Helper functions for the Streamlit application.

This is the integration/presentation layer: it reuses the existing
algorithms and benchmark infrastructure (Members 2-4) rather than
reimplementing sorting, timing, or memory-measurement logic.
"""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from benchmark.run_benchmark import execute_worker, dataset_path  # noqa: E402


DATA_DIR = PROJECT_ROOT / "data" / "generated"
RESULTS_CSV = PROJECT_ROOT / "results" / "benchmark_results.csv"
PLOTS_DIR = PROJECT_ROOT / "plots"

CONDITION_LABELS = {
    "Random": "random",
    "Sorted": "sorted",
    "Reverse Sorted": "reverse_sorted",
    "Nearly Sorted": "nearly_sorted",
    "Duplicate Heavy": "duplicate_heavy",
}

ALGORITHM_LABELS = {
    "Bubble Sort": "bubble",
    "Selection Sort": "selection",
    "Insertion Sort": "insertion",
    "Merge Sort": "merge",
    "Quick Sort": "quick",
}

COMPLEXITY = {
    "bubble": {
        "label": "Bubble Sort",
        "best": "O(n)",
        "average": "O(n\u00b2)",
        "worst": "O(n\u00b2)",
        "note": "Early termination when a full pass makes no swaps gives the "
                "best case; the current implementation scans adjacent pairs "
                "and swaps out-of-order records.",
    },
    "selection": {
        "label": "Selection Sort",
        "best": "O(n\u00b2)",
        "average": "O(n\u00b2)",
        "worst": "O(n\u00b2)",
        "note": "Always scans the remaining unsorted portion to find the "
                "minimum, so its comparison count does not improve on "
                "already-sorted input.",
    },
    "insertion": {
        "label": "Insertion Sort",
        "best": "O(n)",
        "average": "O(n\u00b2)",
        "worst": "O(n\u00b2)",
        "note": "Shifts records instead of swapping; the best case occurs "
                "when the input is already sorted.",
    },
    "merge": {
        "label": "Merge Sort",
        "best": "O(n log n)",
        "average": "O(n log n)",
        "worst": "O(n log n)",
        "note": "Divide-and-conquer with a reusable auxiliary buffer; "
                "performance is consistent regardless of input order.",
    },
    "quick": {
        "label": "Quick Sort",
        "best": "O(n log n)",
        "average": "O(n log n)",
        "worst": "O(n\u00b2)",
        "note": "Uses a deterministic middle-element pivot with Hoare "
                "partitioning and recurses into the smaller partition first "
                "in the current implementation.",
    },
}


def get_available_sizes() -> list[int]:
    """Detect dataset sizes present for every input condition.

    A size is only offered if the CSV exists for all five conditions, so
    any selected combination is guaranteed to be runnable.
    """
    sizes_per_condition: list[set[int]] = []
    for folder in CONDITION_LABELS.values():
        condition_dir = DATA_DIR / folder
        if not condition_dir.is_dir():
            sizes_per_condition.append(set())
            continue
        found = set()
        for csv_file in condition_dir.glob(f"students_*_{folder}.csv"):
            try:
                size = int(csv_file.stem.split("_")[1])
            except (IndexError, ValueError):
                continue
            found.add(size)
        sizes_per_condition.append(found)

    if not sizes_per_condition or not all(sizes_per_condition):
        return []

    common = set.intersection(*sizes_per_condition)
    return sorted(common)


def find_dataset(size: int, condition_folder: str) -> Optional[Path]:
    """Return the dataset path if it exists, otherwise None."""
    path = dataset_path(PROJECT_ROOT, size, condition_folder)
    return path if path.exists() else None


def run_selected_algorithm(
    size: int,
    condition_folder: str,
    key: str,
    algorithm_key: str,
    timeout: float,
) -> dict:
    """Run exactly one algorithm/key/dataset combination.

    Reuses the existing benchmark worker via execute_worker, so timing,
    metrics, memory measurement, sort verification, and timeout handling
    all come from Member 4's implementation. The worker loads its own copy
    of the CSV in a separate process, so the original file is never
    modified.
    """
    dataset = find_dataset(size, condition_folder)
    if dataset is None:
        return {"status": "MISSING_DATASET"}

    return execute_worker(PROJECT_ROOT, dataset, algorithm_key, key, timeout)


def get_complexity(algorithm_key: str) -> dict:
    return COMPLEXITY[algorithm_key]


def _read_benchmark_rows() -> list[dict]:
    if not RESULTS_CSV.exists():
        return []
    with RESULTS_CSV.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def create_result_chart(size: int, condition_folder: str, key: str, highlight_algorithm: str):
    """Build an Algorithm vs Execution Time bar chart for one experiment.

    Uses the existing results/benchmark_results.csv (produced by
    ``python -m benchmark.run_benchmark``) so this does not duplicate the
    benchmarking logic. Returns None if no precomputed data exists for
    this exact combination.
    """
    rows = _read_benchmark_rows()
    if not rows:
        return None

    grouped: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        if (
            row.get("status") == "COMPLETED"
            and row.get("verified") == "True"
            and row.get("sorting_key") == key
            and row.get("condition") == condition_folder
            and row.get("dataset_size") == str(size)
        ):
            try:
                grouped[row["algorithm"]].append(float(row["execution_time_sec"]))
            except (TypeError, ValueError):
                continue

    if not grouped:
        return None

    import matplotlib.pyplot as plt

    order = ["bubble", "selection", "insertion", "merge", "quick"]
    labels, values, colors = [], [], []
    for algorithm in order:
        if algorithm in grouped:
            labels.append(COMPLEXITY[algorithm]["label"])
            values.append(sum(grouped[algorithm]) / len(grouped[algorithm]))
            colors.append("#d62728" if algorithm == highlight_algorithm else "#1f77b4")

    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.bar(labels, values, color=colors)
    ax.set_xlabel("Algorithm")
    ax.set_ylabel("Execution Time (seconds)")
    ax.set_title(
        f"Algorithm vs Execution Time\n"
        f"({size:,} records, {condition_folder.replace('_', ' ').title()}, key={key})"
    )
    ax.bar_label(bars, fmt="%.4f", padding=3, fontsize=8)
    fig.tight_layout()
    return fig