"""Statistics students implement (M2 judge calibration, M4 paired bootstrap).

Rules: a judge is a classifier -- measure it like one. A higher mean is not
"better" until the paired CI of the difference excludes 0.
Reference values to self-check are in tests/test_lab9_stats.py.
"""

from __future__ import annotations

from collections.abc import Sequence

POS = "FAIL"   # the judge's job is to FIND failures, so FAIL is the positive class


def confusion(human: Sequence[str], judge: Sequence[str]) -> dict[str, int]:
    """tp/fp/fn/tn with FAIL as positive."""
    counts = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}

    for actual, predicted in zip(human, judge, strict=True):
        if actual not in ("PASS", "FAIL") or predicted not in ("PASS", "FAIL"):
            raise ValueError("Labels must be PASS or FAIL")

        if actual == "FAIL":
            counts["tp" if predicted == "FAIL" else "fn"] += 1
        else:
            counts["fp" if predicted == "FAIL" else "tn"] += 1

    return counts


def precision_recall(human: Sequence[str], judge: Sequence[str]) -> tuple[float, float]:
    counts = confusion(human, judge)
    tp = counts["tp"]
    fp = counts["fp"]
    fn = counts["fn"]

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0

    return precision, recall


def cohen_kappa(human: Sequence[str], judge: Sequence[str]) -> float:
    counts = confusion(human, judge)
    tp, fp, fn, tn = (counts[key] for key in ("tp", "fp", "fn", "tn"))
    total = tp + fp + fn + tn

    if total == 0:
        raise ValueError("Cohen's kappa requires at least one label pair")

    observed = (tp + tn) / total
    expected = (
        (tp + fn) * (tp + fp)  # Human FAIL × judge FAIL
        + (tn + fp) * (tn + fn)  # Human PASS × judge PASS
    ) / total**2

    if expected == 1.0:
        raise ValueError("Cohen's kappa is undefined when expected agreement is 1")

    return (observed - expected) / (1 - expected)


def rogan_gladen(observed_rate: float, sensitivity: float, specificity: float) -> float:
    denominator = sensitivity + specificity - 1.0
    if denominator == 0.0:
        raise ValueError("Rogan–Gladen is undefined when sensitivity + specificity == 1")

    corrected_rate = (observed_rate + specificity - 1.0) / denominator
    return max(0.0, min(1.0, corrected_rate))


def paired_bootstrap(a: Sequence[float], b: Sequence[float], *, n_resamples: int = 1000,
                     rng: int = 2027, confidence: float = 0.95) -> tuple[float, float, float]:
    """a[i], b[i] = per-item mean over seeds, SAME items, SAME order.
    Return (mean(a)-mean(b), lo, hi) with scipy.stats.bootstrap(paired=True, method="percentile",
    rng=numpy.random.default_rng(rng)). If a == b everywhere return (0.0, 0.0, 0.0)."""
    import numpy as np
    from scipy.stats import bootstrap

    left, right = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if left.ndim != 1 or right.ndim != 1 or left.shape != right.shape or not left.size:
        raise ValueError("paired samples must be nonempty, one-dimensional and equal length")
    if not np.isfinite(left).all() or not np.isfinite(right).all():
        raise ValueError("paired samples must be finite")
    if n_resamples < 1 or not 0 < confidence < 1:
        raise ValueError("invalid bootstrap parameters")
    delta = float(np.mean(left - right))
    if np.array_equal(left, right):
        return 0.0, 0.0, 0.0
    if left.size < 2:
        raise ValueError("bootstrap requires at least two pairs")

    def difference(x, y, axis=-1):
        return np.mean(x - y, axis=axis)

    result = bootstrap((left, right), difference, paired=True, method="percentile",
                       n_resamples=n_resamples, confidence_level=confidence,
                       rng=np.random.default_rng(rng))
    return delta, float(result.confidence_interval.low), float(result.confidence_interval.high)


def pass_at_k(n: int, c: int, k: int) -> float:
    """Probability that AT LEAST ONE of k trials drawn from n (c of them passing) passes.
    Unbiased estimator (Chen et al. 2021): 1 - C(n-c, k) / C(n, k). Raise ValueError if k > n."""
    # TODO M6
    raise NotImplementedError


def pass_hat_k(n: int, c: int, k: int) -> float:
    """pass^k (tau-bench, Yao et al. 2024): probability that ALL k trials drawn from n pass.
    Unbiased estimator: C(c, k) / C(n, k). Raise ValueError if k > n.
    pass^k <= pass@1 <= pass@k; a reliable agent keeps pass^k close to pass@1."""
    # TODO M6
    raise NotImplementedError
