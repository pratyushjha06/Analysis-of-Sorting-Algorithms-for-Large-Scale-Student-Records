"""Streamlit application entry point.

Design and Comparative Analysis of Sorting Algorithms for
Large-Scale Student Records - Member 5 integration layer.
"""

from __future__ import annotations

import csv
import io
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from helpers import (
    ALGORITHM_LABELS,
    CONDITION_LABELS,
    PLOTS_DIR,
    RESULTS_CSV,
    create_result_chart,
    find_dataset,
    get_available_sizes,
    get_complexity,
    run_selected_algorithm,
)


st.set_page_config(
    page_title="Sorting Algorithms - Student Records",
    page_icon="📊",
    layout="centered",
)

st.markdown(
    """
    <style>
    .stApp { background: radial-gradient(circle at top left, #1A1D29 0%, #0E1117 55%); }
    h1 { font-weight: 800 !important; letter-spacing: -0.5px; }
    h2, h3 { font-weight: 700 !important; }
    .subtitle { color: #9CA3AF; font-size: 1.05rem; margin-top: -0.6rem; margin-bottom: 1.4rem; }
    .top-banner {
        background: linear-gradient(120deg, rgba(124,58,237,0.22), rgba(59,130,246,0.10));
        border: 1px solid rgba(124,58,237,0.35);
        border-radius: 18px;
        padding: 1.3rem 1.6rem;
        margin-bottom: 1.6rem;
    }
    .top-banner .pill {
        display: inline-block; background: rgba(124,58,237,0.25); color: #DDD6FE;
        padding: 0.15rem 0.65rem; border-radius: 999px; font-size: 0.72rem;
        font-weight: 700; letter-spacing: 0.4px; margin-bottom: 0.5rem;
    }
    .hero-card {
        background: linear-gradient(135deg, rgba(124,58,237,0.18), rgba(124,58,237,0.02));
        border: 1px solid rgba(124,58,237,0.35);
        border-radius: 16px;
        padding: 1.1rem 1.4rem;
        margin-bottom: 1.2rem;
    }
    .hero-card b { color: #C4B5FD; }
    div[data-testid="stMetric"] {
        background: #1A1D29;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 0.9rem 0.6rem 0.6rem 0.9rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.25);
    }
    div[data-testid="stMetricLabel"] { color: #9CA3AF !important; }
    section[data-testid="stSidebar"] {
        background: #14161F;
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    .stButton > button[kind="primary"] {
        border-radius: 12px;
        font-weight: 700;
        padding: 0.65rem 0;
        box-shadow: 0 4px 14px rgba(124,58,237,0.35);
        border: none;
    }
    .stDownloadButton > button {
        border-radius: 12px;
        font-weight: 600;
        border: 1px solid rgba(124,58,237,0.4);
    }
    div[data-testid="stDataFrame"], .stTable { border-radius: 12px; overflow: hidden; }
    button[data-baseweb="tab"] { font-weight: 600; }
    hr { border-color: rgba(255,255,255,0.08) !important; }
    .badge {
        display: inline-block; padding: 0.2rem 0.7rem; border-radius: 999px;
        font-size: 0.78rem; font-weight: 700; letter-spacing: 0.3px;
    }
    .badge-yes { background: rgba(34,197,94,0.15); color: #4ADE80; border: 1px solid rgba(34,197,94,0.35); }
    .badge-no { background: rgba(239,68,68,0.15); color: #F87171; border: 1px solid rgba(239,68,68,0.35); }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="top-banner">
        <div class="pill">B.TECH PBL PROJECT</div>
        <h1 style="margin:0;">📊 Sorting Algorithms on Student Records</h1>
        <div class="subtitle" style="margin-top:0.3rem;">
            Design and Comparative Analysis of Sorting Algorithms for
            Large-Scale Student Records
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

available_sizes = get_available_sizes()

with st.sidebar:
    st.header("⚙️ Experiment Setup")

    if not available_sizes:
        st.error("No dataset sizes were found under data/generated/. Run the dataset generator first: python generator/dataset_generator.py")
        st.stop()

    size = st.selectbox("📦 Dataset Size", available_sizes, format_func=lambda n: f"{n:,}")
    condition_label = st.selectbox("🔀 Input Condition", list(CONDITION_LABELS.keys()))
    key = st.selectbox("🔑 Sorting Key", ["Student_ID", "CGPA", "Marks"])
    algorithm_label = st.selectbox("🧮 Algorithm", list(ALGORITHM_LABELS.keys()))
    timeout_help_text = "The run is stopped and reported as TIMEOUT if it exceeds this limit."
    timeout = st.slider("⏱️ Timeout (seconds)", min_value=5, max_value=120, value=30, help=timeout_help_text)
    st.markdown("")
    run_clicked = st.button("▶  Run Sorting Experiment", type="primary", use_container_width=True)

    st.divider()
    st.caption("📁 Downloads")
    if RESULTS_CSV.exists():
        st.download_button(
            "⬇️ Full Benchmark Results (CSV)",
            data=RESULTS_CSV.read_bytes(),
            file_name="benchmark_results.csv",
            mime="text/csv",
            use_container_width=True,
        )
    else:
        st.caption("Run the full benchmark to enable this download.")

condition_folder = CONDITION_LABELS[condition_label]
algorithm_key = ALGORITHM_LABELS[algorithm_label]

tab_run, tab_theory, tab_charts = st.tabs(["▶️ Run Experiment", "📐 Complexity", "📈 Charts & Plots"])

with tab_run:
    if run_clicked:
        dataset = find_dataset(size, condition_folder)
        if dataset is None:
            st.error("Selected dataset is not available.")
        else:
            with st.spinner(f"Running {algorithm_label} on {size:,} records..."):
                result = run_selected_algorithm(size, condition_folder, key, algorithm_key, timeout)

            status = result.get("status")

            banner_html = (
                '<div class="hero-card"><b>Algorithm:</b> ' + algorithm_label
                + ' &nbsp;•&nbsp; <b>Dataset:</b> ' + f"{size:,}" + ' records'
                + ' &nbsp;•&nbsp; <b>Input:</b> ' + condition_label
                + ' &nbsp;•&nbsp; <b>Sorting Key:</b> ' + key + '</div>'
            )
            st.markdown(banner_html, unsafe_allow_html=True)

            if status == "COMPLETED":
                exec_ms = result["execution_time_sec"] * 1000
                peak_kb = result["peak_memory_mb"] * 1024

                col1, col2, col3 = st.columns(3)
                col1.metric("⏱️ Execution Time", f"{exec_ms:.3f} ms")
                col2.metric("🔍 Comparisons", f"{result['comparisons']:,}")
                col3.metric("💾 Peak Memory", f"{peak_kb:.1f} KB")

                col4, col5, col6 = st.columns(3)
                col4.metric("🔄 Swaps", f"{result['swaps']:,}")
                col5.metric("➡️ Moves", f"{result['moves']:,}")
                with col6:
                    st.markdown("**Correctly Sorted**")
                    badge_class = "badge-yes" if result["verified"] else "badge-no"
                    badge_text = "YES" if result["verified"] else "NO"
                    st.markdown(f'<span class="badge {badge_class}">{badge_text}</span>', unsafe_allow_html=True)

                if not result["verified"]:
                    st.warning("The output was not verified as sorted. This indicates a bug in the selected algorithm's implementation, not a problem with the interface.")

                csv_buffer = io.StringIO()
                writer = csv.writer(csv_buffer)
                writer.writerow(["field", "value"])
                writer.writerow(["algorithm", algorithm_label])
                writer.writerow(["dataset_size", size])
                writer.writerow(["input_condition", condition_label])
                writer.writerow(["sorting_key", key])
                writer.writerow(["execution_time_ms", f"{exec_ms:.3f}"])
                writer.writerow(["comparisons", result["comparisons"]])
                writer.writerow(["swaps", result["swaps"]])
                writer.writerow(["moves", result["moves"]])
                writer.writerow(["peak_memory_kb", f"{peak_kb:.1f}"])
                writer.writerow(["correctly_sorted", "YES" if result["verified"] else "NO"])

                st.download_button(
                    "⬇️  Download This Result (CSV)",
                    data=csv_buffer.getvalue(),
                    file_name=f"result_{algorithm_key}_{size}_{condition_folder}_{key}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            elif status == "TIMEOUT":
                st.error(f"⏱️ TIMEOUT - this run exceeded the {timeout}-second limit. This is an experimental result (common for O(n^2) algorithms on large datasets), not a program failure.")

            elif status == "MISSING_DATASET":
                st.error("Selected dataset is not available.")

            else:
                st.error(f"The experiment could not complete: {result.get('error', 'Unknown error')}")
    else:
        st.info("Configure your experiment in the sidebar, then click Run Sorting Experiment.")

with tab_theory:
    st.subheader(f"📐 Theoretical Time Complexity - {algorithm_label}")
    complexity = get_complexity(algorithm_key)
    st.table({
        "Case": ["Best", "Average", "Worst"],
        "Complexity": [complexity["best"], complexity["average"], complexity["worst"]],
    })
    st.caption(complexity["note"])
    st.caption("Theoretical complexity describes asymptotic growth, not measured performance - always confirm results against the benchmark data.")

with tab_charts:
    st.subheader("📈 Performance Comparison")
    fig = create_result_chart(size, condition_folder, key, algorithm_key)
    if fig is not None:
        st.pyplot(fig)
        st.caption("Mean execution time across completed, verified benchmark runs for this exact dataset size, input condition, and sorting key. The currently selected algorithm is highlighted in red.")
        chart_buffer = io.BytesIO()
        fig.savefig(chart_buffer, format="png", dpi=150, bbox_inches="tight")
        st.download_button(
            "⬇️  Download This Chart (PNG)",
            data=chart_buffer.getvalue(),
            file_name=f"chart_{size}_{condition_folder}_{key}.png",
            mime="image/png",
            use_container_width=True,
        )
    else:
        st.info("No precomputed benchmark data is available for this exact combination yet. Run the full benchmark to generate comparison data: python -m benchmark.run_benchmark")

    st.divider()
    with st.expander("🗂️ Full project benchmark plots (generated by analysis module)"):
        plot_files = sorted(PLOTS_DIR.glob("*.png")) if PLOTS_DIR.is_dir() else []
        if plot_files:
            for plot_file in plot_files:
                st.image(str(plot_file), caption=plot_file.name, use_container_width=True)
                st.download_button(
                    f"⬇️ Download {plot_file.name}",
                    data=plot_file.read_bytes(),
                    file_name=plot_file.name,
                    mime="image/png",
                    key=f"dl_{plot_file.name}",
                )
        else:
            st.write("No plots found. Generate them with: python -m analysis.analyze_results")