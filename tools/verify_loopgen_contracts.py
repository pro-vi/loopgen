#!/usr/bin/env python3
"""Verify loopgen's docs-as-runtime frontier contracts.

This is intentionally lightweight: loopgen is a prompt generator, not a Python
runtime. The verifier renders the frontier body with and without the
benchmark-frontier overlay and checks the invariants that must be visible in
the generated prompts.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

FRONTIER_BODY = ROOT / "loopgen/templates/bodies/frontier-body.md"
BENCHMARK_FRONTIER = ROOT / "loopgen/primitives/benchmark-frontier.md"
EVAL_LADDER = ROOT / "loopgen/primitives/eval-ladder.md"
SKILL = ROOT / "loopgen/SKILL.md"
COMPOSED_PROMPT = ROOT / "loopgen/templates/composed-prompt.md"


PLACEHOLDERS = {
    "MOTIVE": "Improve the repository's quality frontier without a fixed finish line.",
    "FRONTIER_VECTOR": "- correctness\n- legibility\n- evaluator trustworthiness",
    "EVALUATOR_TIER": "T3",
    "RAMP_GUIDANCE": "",
    "CHEAP_CHANNEL": "python3 tools/verify_loopgen_contracts.py",
    "EXPENSIVE_CHANNEL": "manual review of changed prompt contracts",
    "RAMP_SECTION": "",
    "RAMP_AXES_OVERRIDE": "",
    "SCOPE_MANIFEST": "Scope: loopgen prompt contracts and references.",
    "SCOPE_DRIFT_HALT": "",
    "CASH_OUT_N": "3",
    "QUIET_SIGNAL_N": "3",
    "REVIEW_CLOSURE_OVERLAY": "",
}


PURE_FRONTIER_BANNED = (
    "DOMAIN_SPEC",
    "BENCHMARK.md",
    "`BENCHMARK`",
    "CANDIDATES",
    "FRONTIER.json",
    "`FRONTIER`",
    "candidate_id",
    "parent_candidate_id",
    "Candidate row contract",
    "Candidate lifecycle",
    "operator:",
    "`operator`",
    "holdout set",
    "holdout_trace",
    "holdout_confirmed",
    "holdout_regressed",
    "eval_health",
)

PRESSURE_REQUIRED = (
    "pressure_status",
    "pressure_debt",
    "checkpoint_reason",
    "next_pressure",
)

BENCHMARK_REQUIRED = (
    "Benchmark Frontier Mode",
    "DOMAIN_SPEC",
    "BENCHMARK",
    "CANDIDATES",
    "FRONTIER",
    "traces",
    "candidate_id",
    "operator",
    "holdout set",
    "eval_health",
    "evaluator health",
    "Green search traces",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def frontier_template() -> str:
    text = read(FRONTIER_BODY)
    start = text.index("```md\n") + len("```md\n")
    end_marker = "\n```\n\n---\n\n## Derivation notes"
    end = text.index(end_marker, start)
    return text[start:end]


def include_text(match: re.Match[str]) -> str:
    rel = match.group(1).strip()
    return read(ROOT / "loopgen" / rel)


def benchmark_mode() -> str:
    primitive = read(BENCHMARK_FRONTIER)
    start = primitive.index("## Benchmark Frontier Mode")
    return primitive[start:] + "\n\n" + read(EVAL_LADDER)


def render_frontier(*, benchmark_overlay: bool) -> str:
    prompt = frontier_template()
    mode = benchmark_mode() if benchmark_overlay else ""
    prompt = prompt.replace("{{BENCHMARK_FRONTIER_MODE}}", mode)
    prompt = re.sub(r"\{\{INCLUDE ([^}]+)\}\}", include_text, prompt)
    for key, value in PLACEHOLDERS.items():
        prompt = prompt.replace("{{" + key + "}}", value)
    leftovers = sorted(set(re.findall(r"\{\{[^}]+\}\}", prompt)))
    if leftovers:
        raise AssertionError(f"unsubstituted placeholders: {leftovers}")
    return prompt


def require(condition: bool, name: str, detail: str = "") -> tuple[bool, str]:
    if condition:
        return True, f"[PASS] {name}"
    suffix = f": {detail}" if detail else ""
    return False, f"[FAIL] {name}{suffix}"


def contains_all(text: str, tokens: tuple[str, ...]) -> list[str]:
    return [token for token in tokens if token not in text]


def contains_none(text: str, tokens: tuple[str, ...]) -> list[str]:
    return [token for token in tokens if token in text]


def one_line(text: str) -> str:
    return " ".join(text.split())


def stale_deferred_status(text: str) -> bool:
    return bool(re.search(r"(?m)^\s*-\s*`?DEFERRED`?\b", text))


def run_checks() -> int:
    pure = render_frontier(benchmark_overlay=False)
    benchmark = render_frontier(benchmark_overlay=True)
    skill = read(SKILL)
    composed = read(COMPOSED_PROMPT)
    benchmark_primitive = read(BENCHMARK_FRONTIER)
    benchmark_flat = one_line(benchmark)
    primitive_flat = one_line(benchmark_primitive)
    stale_completion_token = "frontier" + "_complete"

    checks: list[tuple[bool, str]] = []

    checks.append(
        require(
            not contains_all(pure, PRESSURE_REQUIRED),
            "pure_frontier_has_pressure_accounting",
            ", ".join(contains_all(pure, PRESSURE_REQUIRED)),
        )
    )
    checks.append(
        require(
            not contains_none(pure, PURE_FRONTIER_BANNED),
            "pure_frontier_excludes_benchmark_roles",
            ", ".join(contains_none(pure, PURE_FRONTIER_BANNED)),
        )
    )
    checks.append(
        require(
            not contains_all(benchmark, BENCHMARK_REQUIRED),
            "benchmark_frontier_includes_candidate_frontier_trace_eval_roles",
            ", ".join(contains_all(benchmark, BENCHMARK_REQUIRED)),
        )
    )
    checks.append(
        require(
            "do **not** participate in classification distance" in skill
            and "benchmark-frontier" in skill,
            "benchmark_overlay_ignored_by_weighted_hamming",
        )
    )
    checks.append(
        require(
            "not a fifth archetype" in primitive_flat
            and "not a weighted classification axis" in primitive_flat,
            "benchmark_overlay_not_fifth_archetype",
        )
    )
    checks.append(
        require(
            "{{BENCHMARK_FRONTIER_MODE}}" in read(FRONTIER_BODY)
            and "Pure frontier keeps" in composed,
            "composition_has_conditional_benchmark_insert",
        )
    )
    checks.append(
        require(
            stale_completion_token not in pure
            and stale_completion_token not in benchmark
            and not stale_deferred_status(pure)
            and not stale_deferred_status(benchmark),
            "stale_completion_and_deferred_statuses_absent",
        )
    )
    checks.append(
        require(
            "Green search traces, zero OPEN generic findings" in benchmark_flat
            and "are not a checkpoint" in benchmark_flat
            and "must expand one of: candidate, case, control" in benchmark_flat,
            "weave_green_traces_shape_rejected",
        )
    )

    ok = True
    for passed, line in checks:
        ok = ok and passed
        print(line)

    pure_lines = len(pure.splitlines())
    benchmark_lines = len(benchmark.splitlines())
    print(f"pure_frontier_lines={pure_lines}")
    print(f"benchmark_frontier_lines={benchmark_lines}")
    print(f"benchmark_overlay_delta={benchmark_lines - pure_lines}")
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    if len(argv) == 3 and argv[1] == "--print":
        if argv[2] == "pure-frontier":
            print(render_frontier(benchmark_overlay=False))
            return 0
        if argv[2] == "benchmark-frontier":
            print(render_frontier(benchmark_overlay=True))
            return 0
        print("usage: verify_loopgen_contracts.py [--print pure-frontier|benchmark-frontier]", file=sys.stderr)
        return 2
    if len(argv) != 1:
        print("usage: verify_loopgen_contracts.py [--print pure-frontier|benchmark-frontier]", file=sys.stderr)
        return 2
    return run_checks()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
