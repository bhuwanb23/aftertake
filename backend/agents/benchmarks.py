"""Performance benchmark computation for a creator's catalog (Schema 2).

Per Phase 0 Step 9 (Schema 2 note): these five values are calculated
mathematically in Python BEFORE the catalog is passed to the DNA agent.
The LLM does not do arithmetic on numbers reliably — never ask it for these.

Input: list of dicts shaped like SourceVideo (performance nested).
Output: dict shaped like PerformanceBenchmarks.
"""
from __future__ import annotations


def _avg(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _quartile_views(views: list[int], top: bool) -> float:
    """Threshold view count for the top/bottom quartile.

    top=True:  the minimum views among the top 25% of videos —
               what "a hit" means for this specific creator.
    top=False: the maximum views among the bottom 25% —
               below which a video is underperforming.
    """
    if not views:
        return 0.0
    s = sorted(views)
    n = len(s)
    k = max(1, n // 4)  # size of each quartile
    return float(s[n - k] if top else s[k - 1])


def compute_performance_benchmarks(videos: list[dict]) -> dict:
    """Compute the five PerformanceBenchmarks values from catalog videos.

    `videos` entries need a `performance` dict with views, and optionally
    ctr / avg_retention (None = unknown, skipped from averages).
    """
    views = [v["performance"]["views"] for v in videos if v.get("performance", {}).get("views") is not None]
    ctrs = [v["performance"]["ctr"] for v in videos if v.get("performance", {}).get("ctr") is not None]
    rets = [v["performance"]["avg_retention"] for v in videos if v.get("performance", {}).get("avg_retention") is not None]

    return {
        "avg_views": round(_avg(views), 1) if views else 0.0,
        "avg_ctr": round(_avg(ctrs), 1) if ctrs else 0.0,
        "avg_retention": round(_avg(rets), 1) if rets else 0.0,
        "top_quartile_views": _quartile_views(views, top=True),
        "bottom_quartile_views": _quartile_views(views, top=False),
    }
