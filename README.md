# Design and Comparative Analysis of Sorting Algorithms for Large-Scale Student Records

## Project Overview

This project experimentally compares five sorting algorithms — Bubble Sort,
Selection Sort, Insertion Sort, Merge Sort, and Quick Sort — on large,
reproducible student-record datasets. For each experiment the project
measures **execution time**, **comparisons**, **swaps**, **moves**, and
**peak auxiliary memory**, and presents both the measured results and the
algorithm's theoretical time complexity through an interactive Streamlit
application.

## Objectives

- Compare theoretical and practical sorting performance
- Study the effect of dataset size on each algorithm
- Study the effect of input ordering (random, sorted, reverse sorted, nearly sorted, duplicate-heavy)
- Compare operation counts (comparisons, swaps, moves) across algorithms
- Study peak auxiliary memory usage
- Identify where quadratic-time algorithms become practically inefficient

## Features

- Reproducible dataset generation with a fixed random seed
- Five input conditions per dataset size
- Four dataset sizes (1K / 10K / 50K / 100K records)
- Three sorting keys (Student_ID, CGPA, Marks)
- Five sorting algorithms with operation counters
- Process-isolated benchmarking with per-run timeout handling
- Automated result validation
- Aggregate analysis and graph generation
- Interactive Streamlit application for live demonstration

---

## Dataset

### Columns

| Column | Type | Notes |
|---|---|---|
| Student_ID | Integer | Unique |
| Name | String | Non-empty |
| Department | String | CSE / ECE / ME / CE / EEE |
| Semester | Integer | 1–8 |
| CGPA | Decimal | 0–10 |
| Attendance | Decimal | 0–100 |
| Marks | Integer | 0–100 |

### Sizes
1,000 / 10,000 / 50,000 / 100,000

### Input Conditions
Random, Sorted, Reverse Sorted, Nearly Sorted (~5% of records displaced from sorted order), Duplicate Heavy (CGPA/Marks values repeated; Student_ID stays unique)

### Sorting Keys
Student_ID, CGPA, Marks

The dataset generator uses a fixed random seed of **42**, so regenerating
the datasets produces identical output every time.

---

## Algorithms

| Algorithm | Best | Average | Worst |
|---|---|---|---|
| Bubble Sort | O(n) | O(n²) | O(n²) |
| Selection Sort | O(n²) | O(n²) | O(n²) |
| Insertion Sort | O(n) | O(n²) | O(n²) |
| Merge Sort | O(n log n) | O(n log n) | O(n log n) |
| Quick Sort | O(n log n) | O(n log n) | O(n²) |

These are theoretical complexities describing asymptotic growth — they
should not be confused with the measured benchmark performance shown by
the application and in `results/`.

Quick Sort uses a deterministic middle-element pivot with Hoare
partitioning, and recurses into the smaller partition first so large,
unbalanced inputs do not cause Python recursion-depth failures.

---

## Complete Setup (Virtual Environment)

### Windows

```bash
git clone <repository-url>
cd Analysis-of-Sorting-Algorithms-for-Large-Scale-Student-Records

python -m venv .venv
.venv\Scripts\activate

python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.venv\Scripts\Activate.ps1
```

### Linux/macOS

```bash
git clone <repository-url>
cd Analysis-of-Sorting-Algorithms-for-Large-Scale-Student-Records

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Verify Installation

```bash
python --version
pip --version
python -m unittest discover -s tests -v
```

All tests should pass before using the application.

---

## Generate Datasets

```bash
python generator/dataset_generator.py
python generator/validator.py
```

Datasets are written to `data/generated/<condition>/students_<size>_<condition>.csv`.

---

## Run Benchmark

Quick test:

```bash
python -m benchmark.run_benchmark --sizes 1000 --timeout 30
```

Full benchmark (all sizes, conditions, keys, algorithms):

```bash
python -m benchmark.run_benchmark --sizes 1000,10000,50000,100000 --timeout 10
```

Each algorithm/key/dataset combination runs in its own process with a
configurable timeout. O(n²) algorithms may legitimately produce `TIMEOUT`
at large sizes — this is an experimental result, not a program failure,
and is never converted into a fake execution time.

---

## Run Analysis

```bash
python -m analysis.analyze_results
```

This aggregates completed, verified benchmark runs into
`results/benchmark_summary.csv` and generates five graphs under `plots/`:
execution time, comparisons, swaps/moves, and memory usage vs. dataset
size, plus an input-order effect comparison.

---

## Run Application

```bash
python -m streamlit run app/app.py
```

The application opens in your browser. From the sidebar, select:

- **Dataset Size** (only sizes present for all five conditions are offered)
- **Input Condition**
- **Sorting Key**
- **Algorithm**
- **Timeout**

Click **Run Sorting Experiment** to execute one selected combination. The
application displays:

- Execution Time
- Comparisons
- Swaps
- Moves
- Peak Auxiliary Memory
- Correctness verification (YES/NO)
- Theoretical time complexity (best/average/worst) with an explanation
- A performance comparison chart for the selected combination, built from `results/benchmark_results.csv`
- The five full-project benchmark plots from `plots/`

The application runs exactly one experiment per click — the full
4-size × 5-condition × 3-key × 5-algorithm sweep is only available through
`python -m benchmark.run_benchmark`, to keep the live demo responsive.

If a dataset is missing or an experiment times out, the application shows
a clear message instead of crashing.

---

## Project Structure

```text
project/
│
├── app/
│   ├── __init__.py
│   ├── app.py
│   └── helpers.py
│
├── algorithms/
│   ├── __init__.py
│   ├── basic_sorts.py
│   └── efficient_sorts.py
│
├── analysis/
│   ├── __init__.py
│   └── analyze_results.py
│
├── benchmark/
│   ├── __init__.py
│   ├── worker.py
│   └── run_benchmark.py
│
├── data/
│   └── generated/
│       ├── random/
│       ├── sorted/
│       ├── reverse_sorted/
│       ├── nearly_sorted/
│       └── duplicate_heavy/
│
├── generator/
│   ├── dataset_generator.py
│   └── validator.py
│
├── plots/
├── results/
├── tests/
├── screenshots/
├── requirements.txt
└── README.md
```

---

## Team Contributions

### Member 1 — Dataset & Data Generation
Student-record schema, dataset generation, five input conditions,
validation, reproducibility (fixed seed 42).

### Member 2 — Basic Sorting Algorithms
Bubble Sort, Selection Sort, Insertion Sort, operation counters,
complexity documentation.

### Member 3 — Efficient Sorting Algorithms
Merge Sort, Quick Sort, operation counters, complexity documentation.

### Member 4 — Benchmarking & Analysis
Process-isolated benchmark execution, timing, comparisons, swaps/moves,
peak memory measurement, timeout handling, result CSV, aggregate
analysis and graphs.

### Member 5 — Application & Integration
Interactive Streamlit application, integration of all modules, final
testing, final documentation, README, repository cleanup.

---

## Notes on Generated Results

`results/` and `plots/` contain output from an actual benchmark run and
are kept as evidence for the project report and demonstration. They can
be regenerated at any time with the commands above.
