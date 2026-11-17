"""CI gate: compare a PR eval report with the main-branch baseline using the metric spec.

    python -m lab9.gate --pr reports/eval_workflow.json --baseline reports/baseline_v1.json

exit 0 = merge, exit 1 = blocked. Safety metrics: max 0, no averaging away.
Capability metrics: meet the floor AND the paired CI of (PR - main) is not entirely below 0.
Thresholds may only get stricter on the same eval-set version (ratchet).
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from lab8.console import utf8_stdio
from lab9 import stats
from lab9.eval import SPEC, load_spec, per_item


def integrity_check(pr: dict, base: dict, spec: dict, base_spec: dict | None = None) -> list[str]:
    """M7 (Expert): refuse to compare reports that cannot be trusted. Return a list of problems
    (empty = trustworthy). A gate that passes a broken report is worse than no gate.
    Must catch at least:
      - any metric value in pr["metrics"] that is NaN or inf
      - len(pr["rows"]) != manifest items x len(manifest seeds)   (dropped / duplicated rows)
      - the (item_id, seed) set of PR differs from the baseline's (cherry-picked seeds/items)
      - pr["evaluator_failures"] non-empty, or a row whose value for a graded spec metric is
        None (a crashed grader silently scores as "missing" and drops out of the mean)
      - base_spec given and a threshold in spec is LOOSER than in base_spec for the same
        eval-set version (ratchet: max may not rise, min may not fall, a blocking metric may
        not become non-blocking, a metric may not disappear; the same for spec["slices"],
        including dropping no_significant_drop)
      - an item's slice tags in PR rows differ from the baseline's (relabelling an item out of a
        slice hides its regression from the slice gate)"""
    problems = []
    graded = {m["id"] for m in spec.get("metrics", [])
              if m.get("grader") == "code" or m["id"] == "pass_rate"}
    pair_sets, tags = [], []
    for label, report in (("PR", pr), ("baseline", base)):
        rows, manifest = report.get("rows", []), report.get("manifest", {})
        if report.get("evaluator_failures"):
            problems.append(f"{label}: evaluator_failures nonempty")
        seeds = manifest.get("seeds", [])
        if not seeds or len(set(seeds)) != len(seeds):
            problems.append(f"{label}: missing or duplicate manifest seeds")
        pairs = [(r.get("item_id"), r.get("seed")) for r in rows]
        unique = set(pairs)
        items = {i for i, _ in unique}
        if len(rows) != manifest.get("items", 0) * len(seeds):
            problems.append(f"{label}: row count differs from manifest")
        if len(unique) != len(pairs):
            problems.append(f"{label}: duplicate item/seed rows")
        if len(items) != manifest.get("items") or unique != {(i, s) for i in items for s in seeds}:
            problems.append(f"{label}: incomplete item/seed grid")
        pair_sets.append(unique)
        item_tags = {}
        for row in rows:
            current = frozenset(row.get("slices") or [])
            item = row.get("item_id")
            if item in item_tags and item_tags[item] != current:
                problems.append(f"{label}: inconsistent slice tags for {item}")
            item_tags[item] = current
            for mid in graded:
                if type(row.get(mid)) is not bool:
                    problems.append(f"{label}: missing/invalid graded value {item}/{mid}")
        tags.append(item_tags)
        for mid, value in report.get("metrics", {}).items():
            if isinstance(value, (int, float)) and not math.isfinite(value):
                problems.append(f"{label}: nonfinite metric {mid}")
        for m in spec.get("metrics", []):
            value = report.get("metrics", {}).get(m["id"])
            if not isinstance(value, (int, float)) or not math.isfinite(value):
                problems.append(f"{label}: missing/invalid aggregate {m['id']}")
    if pair_sets[0] != pair_sets[1]:
        problems.append("PR item/seed set differs from baseline")
    if tags[0] != tags[1]:
        problems.append("PR slice tags differ from baseline")

    if base_spec and spec.get("eval_set_version") == base_spec.get("eval_set_version"):
        def ratchet(old_entries, new_entries, key, nested):
            new = {key(m): m for m in new_entries}
            for old in old_entries:
                ident = key(old)
                if ident not in new:
                    problems.append(f"ratchet: removed {ident}")
                    continue
                cur = new[ident]
                if old.get("blocking") and not cur.get("blocking"):
                    problems.append(f"ratchet: removed blocking {ident}")
                a = old.get("threshold", {}) if nested else old
                b = cur.get("threshold", {}) if nested else cur
                for field in ("min", "max", "max_increase"):
                    if field in a and (field not in b or
                        (b[field] < a[field] if field == "min" else b[field] > a[field])):
                        problems.append(f"ratchet: loosened {ident}/{field}")
                if a.get("no_significant_drop") and not b.get("no_significant_drop"):
                    problems.append(f"ratchet: removed no_significant_drop {ident}")
        ratchet(base_spec.get("metrics", []), spec.get("metrics", []), lambda m: m["id"], True)
        ratchet(base_spec.get("slices", []), spec.get("slices", []), lambda m: (m["name"], m["metric"]), False)
    return list(dict.fromkeys(problems))


def slice_check(pr: dict, base: dict, spec: dict) -> tuple[list[str], list[str]]:
    """M5 (Advanced): an average can hide a regression on a small, important slice.
    For each entry of spec["slices"] ({"name", "metric", "min"?, "no_significant_drop"?, "blocking"}):
      - value = mean of per_item(pr, metric, slice_name=name)
      - fail if below "min", or if no_significant_drop and the paired CI over the slice's items
        lies entirely below 0
    Return (blocked ids like "slice:money_movement/pass_rate", report lines)."""
    blocked, lines = [], []
    bs = spec.get("bootstrap", {})
    for entry in spec.get("slices", []):
        name, metric = entry["name"], entry["metric"]
        key = f"slice:{name}/{metric}"
        a, b = per_item(pr, metric, name), per_item(base, metric, name)
        reasons = []
        if not a or set(a) != set(b):
            reasons.append("missing or mismatched slice items")
            value = None
        else:
            value = sum(a.values()) / len(a)
            if "min" in entry and value < entry["min"]:
                reasons.append(f"below floor {entry['min']}")
            if entry.get("no_significant_drop"):
                keys = sorted(a)
                if len(keys) < 2:
                    reasons.append("insufficient paired items")
                else:
                    d, lo, hi = stats.paired_bootstrap(
                        [a[k] for k in keys], [b[k] for k in keys],
                        n_resamples=bs.get("n_resamples", 1000), rng=bs.get("rng", 2027),
                        confidence=bs.get("confidence", .95))
                    lines.append(f"  {key} Δ {d:+.3f} CI [{lo:+.3f}, {hi:+.3f}]")
                    if hi < 0:
                        reasons.append("significant drop")
        if reasons and entry.get("blocking"):
            blocked.append(key)
        verdict = "BLOCK" if reasons and entry.get("blocking") else "warn" if reasons else "ok"
        lines.append(f"  {key} {value} {verdict} {'; '.join(reasons)}")
    return blocked, lines


def check(pr: dict, base: dict, spec: dict, base_spec: dict | None = None) -> tuple[list[str], list[str]]:
    if pr["manifest"]["eval_set_sha"] != base["manifest"]["eval_set_sha"]:
        return ["eval_set_sha"], ["  EVAL SET differs from the baseline's: re-run the baseline on the same eval set"]
    problems = integrity_check(pr, base, spec, base_spec)
    if problems:
        return ["integrity"], [f"  INTEGRITY {p}" for p in problems]
    blocked, lines = [], []
    bs = spec.get("bootstrap", {})
    for m in spec["metrics"]:
        mid, th, val = m["id"], m.get("threshold", {}), pr["metrics"].get(m["id"])
        verdict, note = "ok", ""
        if val is None:
            verdict = "missing"
        elif "max" in th and val > th["max"]:
            verdict = "fail"
        elif "min" in th and val < th["min"]:
            verdict = "fail"
        elif "max_increase" in th and base["metrics"].get(mid):
            if val > base["metrics"][mid] * (1 + th["max_increase"]):
                verdict = "fail"
        if th.get("no_significant_drop") and val is not None:
            a, b = per_item(pr, mid), per_item(base, mid)
            keys = sorted(set(a) & set(b))
            d, lo, hi = stats.paired_bootstrap([a[k] for k in keys], [b[k] for k in keys],
                                               n_resamples=bs.get("n_resamples", 1000), rng=bs.get("rng", 2027))
            note = f"Δ {d:+.3f} CI [{lo:+.3f}, {hi:+.3f}]"
            if hi < 0:
                verdict = "fail"
        if verdict != "ok" and m.get("blocking"):
            blocked.append(mid)
        label = {"ok": "ok", "missing": "MISSING"}.get(verdict, "BLOCK" if m.get("blocking") else "warn")
        lines.append(f"  {mid:<22} {val!s:<8} {json.dumps(th):<40} {note:<28} {label}")
    if spec.get("slices"):
        sb, sl = slice_check(pr, base, spec)
        blocked += sb
        lines += sl
    return blocked, lines


def main(argv: list[str] | None = None) -> int:
    utf8_stdio()
    ap = argparse.ArgumentParser(prog="lab9.gate")
    ap.add_argument("--pr", required=True)
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--spec", default=str(SPEC))
    ap.add_argument("--base-spec", help="metric spec on main, for the ratchet check (M7)")
    args = ap.parse_args(argv)
    pr = json.loads(Path(args.pr).read_text(encoding="utf-8"))
    base = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
    base_spec = load_spec(Path(args.base_spec)) if args.base_spec else None
    blocked, lines = check(pr, base, load_spec(Path(args.spec)), base_spec)
    print(f"gate: PR {pr['run_id']} vs main {base['run_id']} · eval set {pr['manifest']['eval_set_sha']}")
    print("\n".join(lines))
    if blocked:
        print(f"exit 1 — blocked: {', '.join(blocked)}")
        return 1
    print("exit 0 — merge")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
