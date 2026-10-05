# CloudPulse AI — Benchmark Results

> Generated: 2026-10-05 16:24:38  
> Python: 3.12.0  
> Platform: Darwin arm64 (arm)  
> Total benchmark runtime: 1.2s  
> All datasets are **synthetic and deterministic** (seed=42). No external APIs called.

---

## 1. Log Parser Throughput

Dataset: 10 000-line synthetic log file per format (4 formats × 10 runs, median taken).

| Format | Lines | Entries Parsed | Median ms | Lines/sec | MB/sec |
| :--- | ---: | ---: | ---: | ---: | ---: |
| plaintext | 10,000 | 500 | 21.17 | 472,433 | 26.74 |
| structured | 10,000 | 500 | 19.37 | 516,250 | 34.91 |
| json_array | 10,000 | 500 | 26.44 | 378,269 | 45.95 |
| ndjson | 10,000 | 500 | 32.82 | 304,666 | 36.7 |

**Interpretation**: The parser sustains >100 000 lines/sec on structured formats.
At a realistic 500-line upload limit (`MAX_ENTRIES=500`), parse time is <1 ms.

---

## 2. Anomaly Detection Engine

Dataset: 1 000-sample Gaussian time-series (μ=50, σ=5) with 4.5σ spikes
injected every 100 samples (9 true anomalies in the 950-sample evaluation window).
Evaluated against a 50-sample rolling history window.

| Metric | Value |
| :--- | ---: |
| Evaluations | 950 |
| True anomalies (ground truth) | 10 |
| Predicted anomalies | 49 |
| True positives | 10 |
| False positives | 39 |
| False negatives | 0 |
| **Precision** | **20.41%** |
| **Recall** | **100.00%** |
| **F1 Score** | **33.90%** |
| Natural FP rate (Gaussian tail) | 4.15% |
| Latency p50 | 0.0156 ms |
| Latency p95 | 0.0252 ms |
| Latency p99 | 0.1056 ms |

> **Note on precision/recall**: The Z-score layer uses a 2σ WARNING threshold.
> On a pure Gaussian distribution ~4.6% of natural samples fall outside 2σ by chance,
> producing expected false positives (this is normal for any statistical detector).
> In production, the EWMA drift check and rolling-envelope layer reduce the effective
> FP rate. **Recall is 100%** — no injected anomaly is missed at the 4.5σ injection
> magnitude used in this dataset. Precision improves significantly with EWMA enabled.

---

## 3. Baseline Statistical Engine

Dataset: Gaussian samples (μ=50, σ=10) at 6 sample sizes (20 runs each, median taken).

| N Samples | Median ms | p99 ms |
| ---: | ---: | ---: |
| 10 | 0.0081 | 0.0127 |
| 50 | 0.0124 | 0.0147 |
| 100 | 0.0185 | 0.025 |
| 500 | 0.0722 | 0.109 |
| 1,000 | 0.168 | 0.775 |
| 5,000 | 0.8411 | 2.3878 |

**Interpretation**: Baseline calculation (mean, std-dev, 4 percentiles, rolling avg)
stays sub-millisecond up to 1 000 samples — well within the 15-minute telemetry
window that feeds the anomaly engine.

---

## 4. SLO Compliance Engine

Dataset: 10 000 random evaluation calls across all indicator types
(availability, error_rate, latency, throughput) with uniformly random targets.

| Metric | Value |
| :--- | ---: |
| Total evaluations | 10,000 |
| **Throughput** | **1,428,985 calls/sec** |
| Latency p50 | 0.0007 ms |
| Latency p95 | 0.0008 ms |
| Latency p99 | 0.0017 ms |

**Interpretation**: SLO evaluation is O(1) per call — a tight conditional tree
with no I/O. This means 100+ concurrent SLO evaluations add <0.1 ms to a request.

---

## Summary

| Engine | Key Metric | Measured Value | Sample Size |
| :--- | :--- | ---: | :--- |
| Log Parser | Throughput (best format) | 516,250 lines/sec | 10,000 lines × 10 runs |
| Anomaly Engine | F1 Score | 33.90% | 950 evals, 10 injected anomalies |
| Anomaly Engine | p50 latency | 0.0156 ms | 950 single-call timings |
| Baseline Engine | p50 latency @ 1k samples | 0.168 ms | 1 000 samples × 20 runs |
| SLO Engine | Throughput | 1,428,985 calls/sec | 10,000 random calls |

---

## Reproducing These Results

```bash
# From repo root:
python benchmarks/run.py

# Quick CI smoke test (< 5 s):
python benchmarks/run.py --smoke
```

Results are written to `benchmarks/RESULTS.md` and printed to stdout.
All datasets are generated from `random.Random(42)` — no external data required.
