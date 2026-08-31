#!/usr/bin/env python3
"""Verify loopgen's docs-as-runtime contracts.

This is intentionally lightweight: loopgen is a prompt generator, not a Python
runtime. The verifier renders the frontier body with and without the
benchmark-frontier overlay and checks the invariants that must be visible in
the generated prompts. It also renders all four archetype bodies against
fixture placeholders (the dead-sections contract), cross-checks SKILL.md's
derivation read contract and STATE.md key lists against the body/reference
files they name, and mirrors SKILL.md's axis matrix against classify.py.

Run via `make check` from the repo root, or directly as
`python3 tools/verify_loopgen_contracts.py`.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import classify  # noqa: E402  (sibling module in tools/, mirrors SKILL.md's axis matrix)


ROOT = Path(__file__).resolve().parents[1]

FRONTIER_BODY = ROOT / "loopgen/templates/bodies/frontier-body.md"
GOAL_BODY = ROOT / "loopgen/templates/bodies/goal-body.md"
STORY_BODY = ROOT / "loopgen/templates/bodies/story-body.md"
GREENFIELD_BODY = ROOT / "loopgen/templates/bodies/greenfield-body.md"
BENCHMARK_FRONTIER = ROOT / "loopgen/primitives/benchmark-frontier.md"
PRESSURE_ACCOUNTING = ROOT / "loopgen/primitives/pressure-accounting.md"
SUBAGENT_PATTERNS = ROOT / "loopgen/primitives/subagent-patterns.md"
HUMAN_LOOK_GATE = ROOT / "loopgen/primitives/human-look-gate.md"
CONSULT_CAPABILITY = ROOT / "loopgen/primitives/consult-capability.md"
EXTERNAL_TRUST_BOUNDARY = ROOT / "loopgen/primitives/external-trust-boundary.md"
BENCHMARK_ARTIFACTS = ROOT / "loopgen/references/benchmark-frontier-artifacts.md"
BENCHMARK_EXAMPLE = ROOT / "loopgen/references/benchmark-frontier-example.md"
FRONTLOAD_AUDIT = ROOT / "loopgen/primitives/frontload-audit.md"
SKILL = ROOT / "loopgen/SKILL.md"
COMPOSED_PROMPT = ROOT / "loopgen/templates/composed-prompt.md"
CONTEXT_STACK = ROOT / "loopgen/primitives/context-stack.md"
PRESSURE = ROOT / "loopgen/primitives/pressure.md"
FRONTIER_VECTOR_ADEQUACY = ROOT / "loopgen/primitives/frontier-vector-adequacy.md"

NON_FRONTIER_BODIES = (
    GOAL_BODY,
    STORY_BODY,
    GREENFIELD_BODY,
)
PRESSURE_ACCOUNTING_INCLUDE = "{{INCLUDE primitives/pressure-accounting.md}}"
CONTEXT_STACK_INCLUDE = "{{INCLUDE primitives/context-stack.md}}"
QUEUE_INCLUDE = "{{INCLUDE primitives/queue-as-second-artifact.md}}"

# The context-stack memory model (ADR 0004). The single JOURNAL.jsonl history
# surface enumerates exactly these record types; the STATE.md keys that used to
# be append-only history now live in JOURNAL.jsonl or DERIVATION.md, so they must
# be absent from every STATE.md key list.
JOURNAL_RECORD_TYPES = (
    "attempt",
    "oracle_change",
    "pressure",
    "consult",
    "alignment_review",
    "checkpoint",
    "halt",
    "score_quarantine",
    "bootstrap",
    "consolidation",
)

NO_PROMOTION_REASONS = (
    "duplicate-of",
    "covered-by",
    "out-of-scope",
    "transient-flake",
    "criterion-local",
    "reverted-before-effect",
)
MOVED_STATE_KEYS = (
    "pressure_ledger",
    "pressure_consulted",
    "oracle_change_notes",
    "capability_list",
    "primitive_bundle",
    "divergences",
    "overlays",
    "derivation_read_set",
    "frontload",
)

BODY_PATHS = {
    "frontier": FRONTIER_BODY,
    "goal": GOAL_BODY,
    "story": STORY_BODY,
    "greenfield": GREENFIELD_BODY,
}


# The one fixture authority for the seed vector (fva-U4): the pure render, the
# generalized body render, and the closure-basis guard fixtures all derive
# from this constant so they cannot drift apart.
FRONTIER_VECTOR_FIXTURE = "- correctness\n- legibility\n- evaluator trustworthiness"

PLACEHOLDERS = {
    "MOTIVE": "Improve the repository's quality frontier without a fixed finish line.",
    "FRONTIER_VECTOR": FRONTIER_VECTOR_FIXTURE,
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
    # Always-on emitted slots, filled for every composed prompt.
    "PROVENANCE": "> Loop provenance — composed by /loopgen (verifier fixture).",
    "FRONTLOAD_PREAMBLE": "> Frontload — resolved: [motive]; defaulted: [thresholds]; open gaps: [none].",
    # PRESSURE_SURFACE is now ALWAYS-ON (ADR 0004): render_frontier / render_body
    # substitute the pressure.md block directly, so it is not a static "" here.
    # {{SUBAGENT_PATTERNS}} stays gated — emitted only at consult-tier >= 1; the
    # verifier renders the tier-0 pure case, so it is stripped (empty) exactly as
    # composed-prompt.md step 8 strips it.
    "SUBAGENT_PATTERNS": "",
}


Pattern = tuple[str, str]


PURE_FRONTIER_BANNED_PATTERNS: tuple[Pattern, ...] = (
    ("DOMAIN_SPEC role", r"\bDOMAIN_SPEC\b"),
    ("BENCHMARK role", r"\bBENCHMARK\b"),
    ("CANDIDATES role", r"\bCANDIDATES\b"),
    ("FRONTIER role", r"\bFRONTIER\b"),
    ("candidate_id", r"\bcandidate_id\b"),
    ("parent_candidate_id", r"\bparent_candidate_id\b"),
    ("candidate row contract", r"Candidate row contract"),
    ("candidate lifecycle", r"Candidate lifecycle"),
    ("operator enum", r"`operator`|operator:"),
    ("holdout role", r"\bholdout\b|holdout_trace|holdout_confirmed|holdout_regressed"),
    ("eval_health", r"\beval_health\b"),
)

PRESSURE_REQUIRED = (
    "pressure_status",
    "pressure_debt",
    "checkpoint_reason",
    "next_pressure",
)

# ── canonical rehydration cadence: ONE table checked against BOTH the
# context-stack authority and all four Operational-core projections (step 2.2b).
REHYDRATION_CADENCE = (
    ("rolling-lossy", "after any detected compaction"),
    ("fresh-episode", "at every episode start"),
    ("unknown", "at every iteration start"),
)

CHECKPOINT_REASON_VALUES = (
    "plateau_after_active_pressure",
    "budget_exhausted",
    "evaluator_invalid",
    "risk_limit_hit",
    "target_gap_unresolved",
    "negative_result_saved",
)

BENCHMARK_REQUIRED_PATTERNS: tuple[Pattern, ...] = (
    ("mode header", r"^## Benchmark Frontier Mode\b"),
    ("DOMAIN_SPEC role", r"\bDOMAIN_SPEC\b"),
    ("BENCHMARK role", r"\bBENCHMARK\b"),
    ("CANDIDATES role", r"\bCANDIDATES\b"),
    ("FRONTIER role", r"\bFRONTIER\b"),
    ("trace role path", r"traces/<candidate>/<case>/evaluation\.json"),
    ("candidate_id field", r"\bcandidate_id\b"),
    (
        "operator enum",
        # Prefix-anchored: benchmark-frontier.md appends the structural-negative
        # bridge operators (consult | architect | build) after `compress`, while
        # the artifacts reference still lists only the core eight (pre-existing
        # drift, tracked separately). Match the core prefix, not the exact tail.
        r"`operator`: `draft \| debug \| improve \| ablate \| stress \| "
        r"falsify \| transfer \| compress",
    ),
    ("holdout set", r"\bholdout set\b"),
    ("eval_health token", r"\beval_health\b"),
    ("green-trace rule", r"Green search traces"),
)


class ContractError(Exception):
    """Verifier setup failed before contract assertions could run."""


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def frontier_template() -> str:
    text = read(FRONTIER_BODY)
    notes_marker = "\n---\n\n## Derivation notes"
    notes_start = text.find(notes_marker)
    if notes_start == -1:
        raise ContractError("missing derivation-notes marker")

    pre_notes = text[:notes_start]
    md_fences = list(re.finditer(r"(?m)^```md\s*$", pre_notes))
    if len(md_fences) != 1:
        raise ContractError(
            "expected exactly one template ```md fence before derivation notes, "
            f"found {len(md_fences)}"
        )

    start = md_fences[0].end() + 1
    closing_fences = [
        match
        for match in re.finditer(r"(?m)^```\s*$", pre_notes)
        if match.start() > start
    ]
    if not closing_fences:
        raise ContractError("missing closing fence for frontier prompt template")
    end = closing_fences[-1].start()
    return text[start:end]


def include_text(match: re.Match[str]) -> str:
    """Resolve `{{INCLUDE primitives/X.md}}` to the primitive's runtime block.

    Per composed-prompt.md step 2, an include inlines only the block that
    follows the `---` spec separator (authoring scaffolding above it — title,
    Purpose, Include-when — is stripped). A primitive with no separator cannot
    be resolved; that is a hard failure, never a silent whole-file fallback.
    """
    rel = match.group(1).strip()
    raw = read(ROOT / "loopgen" / rel)
    sep = "\n---\n"
    idx = raw.find(sep)
    if idx == -1:
        raise ContractError(
            f"included primitive {rel} lacks a '---' spec separator; "
            "cannot resolve its runtime block (composed-prompt.md step 2)"
        )
    return raw[idx + len(sep):].lstrip("\n")


def benchmark_mode() -> str:
    primitive = read(BENCHMARK_FRONTIER)
    start = primitive.index("## Benchmark Frontier Mode")
    return primitive[start:]


FRONTIER_REOPEN_POLICY_FILE = ROOT / "loopgen/templates/bodies/frontier-reopen-policy.md"

REOPEN_POLICY_HEADINGS = {
    "equilibrium": "## Equilibrium variant",
    "terminal": "## Terminal variant",
}


def reopen_policy_variant(variant: str) -> str:
    """Extract a {{FRONTIER_REOPEN_POLICY}} variant from its authoring file by
    heading (composed-prompt.md steps 3/5). The verifier never duplicates the
    block text — the file is the single source."""
    heading = REOPEN_POLICY_HEADINGS[variant]
    raw = read(FRONTIER_REOPEN_POLICY_FILE)
    start = raw.index(heading) + len(heading)
    next_headings = [
        raw.index(h, start) for h in REOPEN_POLICY_HEADINGS.values() if h in raw[start:]
    ]
    end = min(next_headings) if next_headings else len(raw)
    return raw[start:end].strip("\n")


def render_frontier(
    *,
    benchmark_overlay: bool,
    reopen_policy: str = "equilibrium",
    placeholder_overrides: dict[str, str] | None = None,
) -> str:
    prompt = frontier_template()
    mode = benchmark_mode() if benchmark_overlay else ""
    prompt = prompt.replace("{{BENCHMARK_FRONTIER_MODE}}", mode)
    prompt = prompt.replace(
        "{{FRONTIER_REOPEN_POLICY}}", reopen_policy_variant(reopen_policy)
    )
    prompt = re.sub(r"\{\{INCLUDE ([^}]+)\}\}", include_text, prompt)
    # Pressure surface is always-on (ADR 0004): substitute the pressure.md block.
    prompt = prompt.replace("{{PRESSURE_SURFACE}}", resolve_gated_block(PRESSURE))
    # render_frontier renders the tier-0 pure case: the run-host channel check
    # strips byte-identical (composed-prompt step 8), eating its blank line,
    # and the tier-0 human-look gate fills (composed-prompt step 7b).
    prompt = prompt.replace("{{RUN_HOST_VERIFICATION}}\n\n", "")
    prompt = prompt.replace(
        "{{HUMAN_LOOK_GATE}}", resolve_gated_block(HUMAN_LOOK_GATE).rstrip("\n")
    )
    placeholders = dict(PLACEHOLDERS)
    if placeholder_overrides:
        placeholders.update(placeholder_overrides)
    for key, value in placeholders.items():
        prompt = prompt.replace("{{" + key + "}}", value)
    leftovers = sorted(set(re.findall(r"\{\{[^}]+\}\}", prompt)))
    if leftovers:
        raise AssertionError(f"unsubstituted placeholders: {leftovers}")
    return prompt


# ── playbook render + frozen golden (R3, dev/plans/2026-06-23-001 U4) ──
# The playbook is the executable portion of the rendered frontier prompt:
# everything except the provenance preamble and the frontload preamble, which
# legitimately vary per composition (provenance/frontload metadata is out of
# R3's byte-identity scope). Fixed sentinels keep the render deterministic and
# independent of the metadata-bearing fixtures, so frontload/provenance
# contract changes (e.g. new reopening-contract fields) never dirty the golden.

GOLDEN_DIR = ROOT / "tools/golden"
FRONTIER_EQUILIBRIUM_GOLDEN = GOLDEN_DIR / "frontier-body.equilibrium.md"
FRONTIER_BENCHMARK_GOLDEN = GOLDEN_DIR / "frontier-body.benchmark.equilibrium.md"

PLAYBOOK_SENTINELS = {
    "PROVENANCE": "(provenance preamble — out of playbook scope)",
    "FRONTLOAD_PREAMBLE": "(frontload preamble — out of playbook scope)",
}


def render_frontier_playbook() -> str:
    """Pure-frontier playbook (effective-equilibrium reopen policy, no
    benchmark overlay), provenance/frontload normalized to fixed sentinels.
    This is the surface the frozen golden pins byte-for-byte.

    Regeneration path for INTENTIONAL playbook edits:
    `python3 tools/verify_loopgen_contracts.py --capture-golden` (then commit
    the golden together with the edit that moved it)."""
    return render_frontier(
        benchmark_overlay=False, placeholder_overrides=PLAYBOOK_SENTINELS
    )


def render_frontier_benchmark_playbook() -> str:
    """Benchmark-overlay playbook (effective-equilibrium reopen policy),
    provenance/frontload normalized to the same sentinels — the second frozen
    golden (fva-U3), so overlay-visible contract text (green-trace reroute,
    projection parity) is pinned byte-for-byte alongside the pure render."""
    return render_frontier(
        benchmark_overlay=True, placeholder_overrides=PLAYBOOK_SENTINELS
    )


# ── guarded halt-shape resolution: executable spec (U4b) ──
# Mirrors primitives/halt-shape.md's guarded closed-corpus resolution the way
# classify.py mirrors SKILL.md's axis matrix; the guard_prose_conjuncts check
# pins the prose so the two cannot drift silently. Field encoding: a named
# value is the string itself; "none" is the literal token; None means the
# field is absent (legacy artifacts / fixtures only — a fresh frontier
# composition must emit the fields); "unresolved" means frontload could not
# resolve it.


class DerivationGap(Exception):
    """Non-emittable path: an open_gaps entry, never a silent default."""


CLOSURE_BASIS_KEYS = (
    "work_source_domain",
    "declared_surfaces",
    "exhaustion_criterion",
    "initial_frontier_vector",
)
LEGACY_CLOSURE_BASIS_KEYS = CLOSURE_BASIS_KEYS[:3]


def closure_basis_established(closure_basis: dict | None) -> bool:
    """The compose-time closure contract: an enumerated observable work-source
    domain, the declared search surfaces, the criterion that will establish
    declared-workset exhaustion at runtime, and the initial frontier vector
    (part of the declared workset's identity — fva-U2). All four, non-empty,
    for a fresh composition — a bare flag cannot prove a closed-world
    inference. Back-compat ONLY (mirrors the absent-reopening-fields rule): a
    pre-existing artifact that never recorded `initial_frontier_vector` (key
    absent) keeps resolving under its original three-field semantics; a
    *present but empty* fourth field is partial closure evidence, never
    legacy."""
    if not isinstance(closure_basis, dict):
        return False
    if "initial_frontier_vector" not in closure_basis:
        return all(closure_basis.get(key) for key in LEGACY_CLOSURE_BASIS_KEYS)
    return all(closure_basis.get(key) for key in CLOSURE_BASIS_KEYS)


def resolve_effective_halt_shape(
    *,
    archetype: str,
    requested: str,
    reopening_signal: str | None,
    reopen_contract: str | None,
    closure_basis: dict | None,
) -> tuple[str, bool]:
    """Returns (effective_halt_shape, compiler_derived_divergence)."""
    if archetype != "frontier":
        return requested, False
    if reopening_signal is None and reopen_contract is None:
        # Backward-compatibility ONLY (pre-existing artifacts, fixtures):
        # composition-side, absent fields are a derivation gap for frontier.
        return requested, False
    if reopening_signal is None or reopen_contract is None:
        # A fresh composition emits both fields together; one without the
        # other is incomplete frontload evidence, never a resolvable state.
        raise DerivationGap("partially recorded reopening contract")
    if "unresolved" in (reopening_signal, reopen_contract):
        raise DerivationGap("reopening contract unresolved")
    named_signal = reopening_signal != "none"
    named_contract = reopen_contract != "none"
    if named_signal and not named_contract:
        raise DerivationGap("named signal without an observable delivery channel")
    if named_contract and not named_signal:
        raise DerivationGap("delivery channel without a named signal")
    if not named_signal and not named_contract:
        if not closure_basis_established(closure_basis):
            raise DerivationGap(
                "reopen_contract none without an established closure basis "
                f"(needs non-empty {', '.join(CLOSURE_BASIS_KEYS)})"
            )
        if requested == "equilibrium":
            return "terminal", True  # the guarded implication
        return requested, False  # explicit terminal honored as requested
    return requested, False  # live reopen contract → pass through


# ── generalized render, all four archetype bodies (dead-sections contract) ──
# render_frontier() above is kept as-is (existing frontier-specific checks
# assert on its exact fixture values). This is a second, generalized renderer
# used only to prove every body's placeholders are all substitutable and that
# no {{...}} token survives (composed-prompt.md step 8's dead-section rule),
# for all four bodies, not just frontier.

COMMON_BODY_PLACEHOLDERS = {
    "PROVENANCE": "> Loop provenance — composed by /loopgen (verifier fixture).",
    "FRONTLOAD_PREAMBLE": "> Frontload — resolved: [motive]; defaulted: [thresholds]; open gaps: [none].",
    "MOTIVE": "Improve the repository's quality frontier without a fixed finish line.",
    # PRESSURE_SURFACE is always-on (ADR 0004) — render_body substitutes the
    # pressure.md block directly. {{SUBAGENT_PATTERNS}} stays gated: stripped at
    # tier-0, filled by render_body(..., consult_tier=N).
}

ARCHETYPE_BODY_PLACEHOLDERS = {
    "frontier": {
        "FRONTIER_VECTOR": FRONTIER_VECTOR_FIXTURE,
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
    },
    "goal": {
        "GOAL_VERSION": "goal-v1-fixture",
        "SCOPE_BASELINE": "0123456789abcdef0123456789abcdef01234567",
        "REGRESSION_MODE": "",
        "STUCK_ATTEMPT_N": "3",
        "CHEAP_CHANNEL": "make check",
        "FINAL_VERIFY": "make check",
        "TOPOLOGY": "all criteria independent.",
        "SCOPE_MANIFEST": "Scope: fixture acceptance inventory.",
        "FORBIDDEN_SHORTCUTS": "None beyond the defaults below.",
        "REPO_SPECIFIC_OVERLAY": "",
    },
    "story": {
        "LANE": "Surface Taste Lane",
        "SURFACE_CLASS": "fixture surface",
        "STORYBOARD_PATH": "docs/storyboard.md",
    },
    "greenfield": {
        "CAPABILITY_LIST": "- none yet.",
        "INVARIANTS": "1. Fixture invariant placeholder.",
        "PHASE_GATES": "- research: owner loop, status yes",
    },
}


def raw_body_template(path: Path) -> str:
    """Extract the fenced prompt template from a body file, generalizing
    frontier_template() to bodies that use a four-backtick fence (goal,
    story, greenfield nest ```yaml/```text/```json blocks, so their outer
    fence widens to four backticks) as well as frontier's three-backtick one.
    """
    text = read(path)
    notes_marker = "\n---\n\n## Derivation notes"
    notes_start = text.find(notes_marker)
    if notes_start == -1:
        raise ContractError(f"{path.name}: missing derivation-notes marker")

    pre_notes = text[:notes_start]
    fence_open = re.search(r"(?m)^(`{3,4})md\s*$", pre_notes)
    if not fence_open:
        raise ContractError(f"{path.name}: missing opening md fence before derivation notes")
    ticks = fence_open.group(1)
    start = fence_open.end() + 1
    close_re = re.compile(rf"(?m)^{ticks}\s*$")
    closing_fences = [m for m in close_re.finditer(pre_notes) if m.start() > start]
    if not closing_fences:
        raise ContractError(f"{path.name}: missing closing fence for prompt template")
    end = closing_fences[-1].start()
    return text[start:end]


def resolve_gated_block(path: Path) -> str:
    """The runtime block below a primitive's '---' spec separator (same
    resolution rule as include_text(), factored out for gated placeholders
    that are substituted directly rather than via an {{INCLUDE ...}} marker).
    """
    raw = read(path)
    sep = "\n---\n"
    idx = raw.find(sep)
    if idx == -1:
        raise ContractError(f"{path.name} lacks a '---' spec separator")
    return raw[idx + len(sep):].lstrip("\n")


def _filter_subagent_patterns(
    block: str, consult_tier: int, pollable_channel: bool
) -> str:
    """composed-prompt.md step 7b: emit only the B/C/D bullets the detected
    tier meets — D at tier ≥ 1; B at tier 3; C at tier 3, or tier ≥ 1 when
    frontload bound a pollable job channel. Bullets are dropped at
    substitution time (a content filter), never stripped afterwards, so a
    tier-1/2 host never sees a tier-3 pattern inlined."""
    closing_marker = "Only the patterns at or below"
    idx = block.find(closing_marker)
    if idx == -1:
        raise ContractError(
            "subagent-patterns block: closing paragraph marker missing"
        )
    head, closing = block[:idx], block[idx:]
    keep = {
        "D": consult_tier >= 1,
        "B": consult_tier >= 3,
        "C": consult_tier >= 3 or (consult_tier >= 1 and pollable_channel),
    }
    kept: list[str] = []
    for part in re.split(r"(?m)^(?=- \*\*[A-Z] — )", head):
        m = re.match(r"- \*\*([A-Z]) — ", part)
        if m and not keep.get(m.group(1), False):
            continue
        kept.append(part)
    return "".join(kept).rstrip("\n") + "\n\n" + closing


def render_body(
    archetype: str,
    *,
    consult_tier: int = 0,
    pollable_channel: bool = False,
    placeholder_overrides: dict[str, str] | None = None,
) -> str:
    if type(consult_tier) is not int or consult_tier not in (0, 1, 2, 3):
        raise ContractError(
            f"render_body: consult_tier must be an int in 0..3, got {consult_tier!r}"
        )
    if type(pollable_channel) is not bool:
        raise ContractError(
            f"render_body: pollable_channel must be a bool, got {pollable_channel!r}"
        )
    prompt = raw_body_template(BODY_PATHS[archetype])
    if archetype == "frontier":
        prompt = prompt.replace("{{BENCHMARK_FRONTIER_MODE}}", "")
        prompt = prompt.replace(
            "{{FRONTIER_REOPEN_POLICY}}", reopen_policy_variant("equilibrium")
        )
    prompt = re.sub(r"\{\{INCLUDE ([^}]+)\}\}", include_text, prompt)
    # Pressure surface is always-on (ADR 0004).
    prompt = prompt.replace("{{PRESSURE_SURFACE}}", resolve_gated_block(PRESSURE))

    if consult_tier >= 1:
        block = _filter_subagent_patterns(
            resolve_gated_block(SUBAGENT_PATTERNS), consult_tier, pollable_channel
        )
        block = block.replace("{{CONSULT_TIER}}", f"tier-{consult_tier}")
        prompt = prompt.replace("{{SUBAGENT_PATTERNS}}", block)
        run_host = resolve_gated_block(CONSULT_CAPABILITY).replace(
            "{{CONSULT_TIER}}", f"tier-{consult_tier}"
        )
        prompt = prompt.replace("{{RUN_HOST_VERIFICATION}}", run_host.rstrip("\n"))
    else:
        prompt = prompt.replace("{{SUBAGENT_PATTERNS}}", "")
        # tier-0: strip byte-identical, eating the slot's blank line (step 8).
        prompt = prompt.replace("{{RUN_HOST_VERIFICATION}}\n\n", "")
    # The human-look gate is ALWAYS filled (composed-prompt step 7b): a
    # consulted prompt may downgrade to effective tier-0 mid-run, so the
    # fallback must already be in the prompt when the downgrade lands on it.
    prompt = prompt.replace(
        "{{HUMAN_LOOK_GATE}}", resolve_gated_block(HUMAN_LOOK_GATE).rstrip("\n")
    )

    values = dict(COMMON_BODY_PLACEHOLDERS)
    values.update(ARCHETYPE_BODY_PLACEHOLDERS[archetype])
    if placeholder_overrides:
        values.update(placeholder_overrides)
    for key, value in values.items():
        prompt = prompt.replace("{{" + key + "}}", value)

    leftovers = sorted(set(re.findall(r"\{\{[^}]+\}\}", prompt)))
    if leftovers:
        raise AssertionError(f"{archetype}: unsubstituted placeholders: {leftovers}")
    return prompt


def require(condition: bool, name: str, detail: str = "") -> tuple[bool, str]:
    if condition:
        return True, f"[PASS] {name}"
    suffix = f": {detail}" if detail else ""
    return False, f"[FAIL] {name}{suffix}"


def missing_tokens(text: str, tokens: tuple[str, ...]) -> list[str]:
    return [token for token in tokens if token not in text]


def missing_patterns(text: str, patterns: tuple[Pattern, ...]) -> list[str]:
    return [
        name
        for name, pattern in patterns
        if re.search(pattern, text, re.MULTILINE) is None
    ]


def leaked_patterns(text: str, patterns: tuple[Pattern, ...]) -> list[str]:
    return [
        name
        for name, pattern in patterns
        if re.search(pattern, text, re.MULTILINE) is not None
    ]


def one_line(text: str) -> str:
    return " ".join(text.split())


def stale_deferred_status(text: str) -> bool:
    return bool(re.search(r"(?m)^\s*-\s*`?DEFERRED`?\b", text))


# Candidate-row contract, verdict-driven. Mirrors the rule in
# references/benchmark-frontier-artifacts.md: a status may not outrun its
# evidence OR its verdict, and deferred pressure is a FRONTIER-level fact,
# never a candidate-row status. This is a contract fixture test (proving the
# documented rule rejects the documented-invalid states), not a runtime
# row validator.
VALID_ROW_STATUSES = {
    "proposed",
    "compliance_checked",
    "smoke_checked",
    "search_scored",
    "frontier_member",
    "rejected",
    "holdout_confirmed",
    "holdout_regressed",
    "pressure_paid",
}


def _pressure_paid_supported(traces: dict[str, object]) -> bool:
    if traces.get("holdout") == "pass":
        return True
    adversarial = traces.get("adversarial")
    if (
        isinstance(adversarial, dict)
        and adversarial.get("expected_green")
        and adversarial.get("expected_red")
    ):
        return True
    return bool(traces.get("meta_eval"))


def candidate_row_violations(row: dict[str, object]) -> list[str]:
    """Return the contract violations for a candidate row (empty == valid)."""
    violations: list[str] = []
    status = row.get("status")
    traces = row.get("traces", {})

    if status not in VALID_ROW_STATUSES:
        violations.append(f"{status!r} is not a candidate-row status")
        return violations

    holdout = traces.get("holdout")  # "pass" | "fail" | "regress" | None
    if status == "holdout_confirmed" and holdout != "pass":
        violations.append("holdout_confirmed needs a passing holdout_trace verdict")
    if status == "holdout_regressed" and holdout not in {"fail", "regress"}:
        violations.append("holdout_regressed needs a failing/regressing holdout_trace verdict")
    if status == "pressure_paid" and not _pressure_paid_supported(traces):
        violations.append("pressure_paid needs a stronger-pressure trace with a supporting verdict")
    return violations


CANDIDATE_ROW_FIXTURES: tuple[tuple[str, dict[str, object], bool], ...] = (
    ("holdout_confirmed + passing holdout", {"status": "holdout_confirmed", "traces": {"holdout": "pass"}}, True),
    ("holdout_confirmed + null holdout", {"status": "holdout_confirmed", "traces": {"holdout": None}}, False),
    ("holdout_confirmed + failing holdout (verdict mismatch)", {"status": "holdout_confirmed", "traces": {"holdout": "fail"}}, False),
    ("pressure_paid + only search evidence", {"status": "pressure_paid", "traces": {}}, False),
    ("pressure_paid + adversarial without expected_red", {"status": "pressure_paid", "traces": {"adversarial": {"expected_green": True, "expected_red": False}}}, False),
    ("pressure_paid + adversarial controls recorded", {"status": "pressure_paid", "traces": {"adversarial": {"expected_green": True, "expected_red": True}}}, True),
    ("pressure_deferred is not a candidate status", {"status": "pressure_deferred", "traces": {}}, False),
    ("frontier_member with holdout deferred (null) — deferral lives in FRONTIER", {"status": "frontier_member", "traces": {"holdout": None}}, True),
)


# ── oracle-integrity contract (benchmark-frontier overlay) ──────────────────
# Guards the row -> property -> trace bijection the code review caught drifting
# (the P1 "oracle-provenance" name collision and the P4/P5 transposition). The
# eight oracle.* rows in benchmark-frontier.md, the mapping table beneath them,
# and the P1-P8 list in frontload-audit.md must all agree, 1:1, by name and order.

_ORACLE_GUARDS_HEADER = "| id | guards against |"
_ORACLE_MAP_HEADER = "| row | audit property | candidate trace |"
_PROP_NAME = r"[a-z][a-z\- ]*[a-z]"


def _table_block(text: str, header: str) -> str:
    i = text.find(header)
    if i == -1:
        return ""
    block = text[i:]
    end = block.find("\n\n")
    return block[:end] if end != -1 else block


def _guards_rows(primitive: str) -> list[str]:
    block = _table_block(primitive, _ORACLE_GUARDS_HEADER)
    return re.findall(r"(?m)^\|\s*`(oracle\.[a-z0-9-]+)`\s*\|", block)


def _mapping_rows(primitive: str) -> list[tuple[str, str, str, str]]:
    block = _table_block(primitive, _ORACLE_MAP_HEADER)
    rows: list[tuple[str, str, str, str]] = []
    for line in block.splitlines():
        m = re.match(
            rf"^\|\s*`(oracle\.[a-z0-9-]+)`\s*\|\s*(P\d)\s+({_PROP_NAME})\s*\|\s*(.+?)\s*\|$",
            line,
        )
        if m:
            rows.append((m.group(1), m.group(2), m.group(3), m.group(4)))
    return rows


def _frontload_properties(audit_text: str) -> list[tuple[str, str, str]]:
    return re.findall(
        rf"(?m)^-\s+\*\*(P\d)\s+({_PROP_NAME})\*\*\s*\(`(oracle\.[a-z0-9-]+)`\)",
        audit_text,
    )


def oracle_integrity_bijection_violations() -> list[str]:
    primitive = read(BENCHMARK_FRONTIER)
    audit = read(FRONTLOAD_AUDIT)
    artifacts = read(BENCHMARK_ARTIFACTS)
    v: list[str] = []

    guards = _guards_rows(primitive)
    mapping = _mapping_rows(primitive)
    fl = _frontload_properties(audit)

    if len(guards) != 8:
        v.append(f"guards table has {len(guards)} oracle rows (expected 8)")
    if len(mapping) != 8:
        v.append(f"mapping table has {len(mapping)} rows (expected 8)")
    if len(fl) != 8:
        v.append(f"frontload audit lists {len(fl)} properties (expected 8)")

    guards_ids = set(guards)
    mapping_ids = {r[0] for r in mapping}
    fl_ids = {r[2] for r in fl}
    if guards_ids != mapping_ids:
        v.append(f"guards vs mapping row-id mismatch: {sorted(guards_ids ^ mapping_ids)}")
    if mapping_ids != fl_ids:
        v.append(f"mapping vs frontload row-id mismatch: {sorted(mapping_ids ^ fl_ids)}")

    map_by_id = {r[0]: (r[1], r[2]) for r in mapping}
    fl_by_id = {r[2]: (r[0], r[1]) for r in fl}
    for rid in sorted(mapping_ids & fl_ids):
        if map_by_id[rid] != fl_by_id[rid]:
            v.append(f"{rid}: mapping {map_by_id[rid]} != frontload {fl_by_id[rid]}")

    expected_pnums = [f"P{i}" for i in range(1, 9)]
    if sorted(r[1] for r in mapping) != expected_pnums:
        v.append(f"mapping P-numbers not a 1..8 bijection: {sorted(r[1] for r in mapping)}")
    if sorted(r[0] for r in fl) != expected_pnums:
        v.append(f"frontload P-numbers not a 1..8 bijection: {sorted(r[0] for r in fl)}")

    for rid, _pnum, _name, trace in mapping:
        m = re.fullmatch(r"`([a-z_]+)`", trace.strip())
        if m and m.group(1) not in artifacts:
            v.append(f"{rid}: trace field `{m.group(1)}` not present in artifacts reference")

    return v


def seed_double_gate_violations() -> list[str]:
    """The seed imperative must carry the second gate (trusted-or-mutated), so a
    deterministic-oracle overlay seeds nothing and the byte-identity negative path
    holds. A bare 'On overlay activation, seed ...' widens it to any benchmark."""
    primitive = read(BENCHMARK_FRONTIER)
    v: list[str] = []
    if re.search(r"On overlay activation,\s+seed these rows", primitive):
        v.append("seed imperative dropped the trusted-or-mutated gate (bare 'On overlay activation, seed')")
    if "trusted-or-mutated" not in one_line(primitive):
        v.append("missing 'trusted-or-mutated' seed qualifier")
    return v


def oracle_integrity_authority_violations() -> list[str]:
    """Guards the two Codex P2 findings on PR #3:
    (1) overlay-seeded rows must be `source: overlay`, not `source: mined` (which
        would conflict with the latent-mining low/salience + provenance contract);
    (2) the gate caps `claim_scope`, never an undefined candidate status -- the
        candidate-status enum has no `pending-needs-cross-seed` / `pending`."""
    primitive = read(BENCHMARK_FRONTIER)
    audit = read(FRONTLOAD_AUDIT)
    v: list[str] = []

    if "`source: overlay`" not in primitive:
        v.append("oracle rows are not declared `source: overlay`")
    if re.search(r"seed these rows.*?`source: mined`", primitive, re.S):
        v.append("oracle rows still declared `source: mined` (conflicts with the mined entry rule)")

    for text, where in ((primitive, "benchmark-frontier"), (audit, "frontload-audit")):
        for tok in ("pending-needs-cross-seed", "caps status at", "caps the candidate at"):
            if tok in text:
                v.append(f"{where}: undefined-candidate-status phrasing {tok!r} (cap via claim_scope instead)")
    return v


def halt_shared_cause_violations() -> list[str]:
    """signal-starvation is a quiet-signal-checkpoint cause: frontier+story carry
    it; goal (terminal, no quiet-signal machinery) must not. frontier's
    genuine-escalate must keep the recovered 'source conflict' detail (U2)."""
    v: list[str] = []
    goal = read(ROOT / "loopgen/templates/bodies/goal-body.md")
    story = read(ROOT / "loopgen/templates/bodies/story-body.md")
    frontier = read(FRONTIER_BODY)
    if "signal-starvation" not in frontier:
        v.append("frontier body missing signal-starvation")
    if "signal-starvation" not in story:
        v.append("story body missing signal-starvation")
    if "signal-starvation" in goal:
        v.append("goal body must not carry signal-starvation (no quiet-signal checkpoint)")
    if "source conflict" not in frontier:
        v.append("frontier genuine-escalate dropped 'source conflict'")
    return v


def scope_terminal_preflight_violations() -> list[str]:
    """Mandatory writes must fit scope, and cheap terminal checks must gate proof."""
    violations: list[str] = []
    skill = one_line(read(SKILL))
    goal_template = one_line(raw_body_template(GOAL_BODY))
    frontier_template = one_line(raw_body_template(FRONTIER_BODY))
    goal_render = render_body("goal")

    for pin, name in (
        ("mandatory-write set", "required-write derivation"),
        ("stop composition and resolve the contradiction", "composition stop"),
        ("sole operational-bootstrap exception", "bootstrap exception boundary"),
    ):
        if pin not in skill:
            violations.append(f"SKILL Phase 3 missing {name} (`{pin}`)")

    for template, archetype in (
        (goal_template, "goal"),
        (frontier_template, "frontier"),
    ):
        for pin in (
            "host-repository `.gitignore` guard for `.loop/`",
            "does not authorize any other `.gitignore` edit",
            "Every other mandatory write must be inside Allowed and outside Forbidden",
        ):
            if pin not in template:
                violations.append(
                    f"{archetype} scope manifest missing bootstrap boundary (`{pin}`)"
                )

    for pin, name in (
        ("**terminal preflight**", "terminal preflight"),
        (
            "git merge-base --is-ancestor "
            "0123456789abcdef0123456789abcdef01234567 HEAD",
            "scope-baseline ancestry gate",
        ),
        (
            "git diff --no-renames --name-only "
            "0123456789abcdef0123456789abcdef01234567...HEAD",
            "committed-path scan",
        ),
        ("git diff --cached --no-renames --name-only", "staged-path scan"),
        ("git diff --no-renames --name-only", "unstaged-path scan"),
        ("git ls-files --others --exclude-standard", "untracked-path scan"),
        ("forbidden source path cannot disappear", "rename-source coverage"),
        ("do **not** start the final-verify", "preflight failure gate"),
        ("Only after the preflight passes", "preflight success gate"),
        ("immutable compose-time Git commit", "scope baseline authority"),
    ):
        if pin not in goal_render:
            violations.append(f"goal render missing {name} (`{pin}`)")

    preflight_position = goal_render.find("**terminal preflight**")
    final_verify_position = goal_render.find("Only after the preflight passes")
    if (
        preflight_position == -1
        or final_verify_position == -1
        or preflight_position >= final_verify_position
    ):
        violations.append("goal terminal preflight does not precede final verification")

    return violations


def terminal_path_scan_executable_violations() -> list[str]:
    """Run the emitted Git scan shape over every worktree change category."""
    try:
        with tempfile.TemporaryDirectory(prefix="loopgen-terminal-preflight-") as tmp:
            fixture = Path(tmp)

            def git(*args: str) -> subprocess.CompletedProcess[str]:
                return subprocess.run(
                    ["git", *args],
                    cwd=fixture,
                    capture_output=True,
                    text=True,
                    check=True,
                )

            git("init", "-q")
            git("config", "user.name", "Loopgen Fixture")
            git("config", "user.email", "loopgen-fixture@example.invalid")
            (fixture / "allowed").mkdir()
            (fixture / "forbidden").mkdir()
            (fixture / "allowed/staged.txt").write_text("base\n", encoding="utf-8")
            (fixture / "allowed/unstaged.txt").write_text("base\n", encoding="utf-8")
            (fixture / "forbidden/renamed.txt").write_text("base\n", encoding="utf-8")
            git("add", ".")
            git("commit", "-qm", "fixture baseline")
            baseline = git("rev-parse", "HEAD").stdout.strip()

            (fixture / "allowed/committed.txt").write_text(
                "committed\n", encoding="utf-8"
            )
            git("mv", "forbidden/renamed.txt", "allowed/renamed.txt")
            git("add", "allowed/committed.txt")
            git("commit", "-qm", "fixture committed changes")
            (fixture / "allowed/staged.txt").write_text("staged\n", encoding="utf-8")
            git("add", "allowed/staged.txt")
            (fixture / "allowed/unstaged.txt").write_text(
                "unstaged\n", encoding="utf-8"
            )
            (fixture / "allowed/untracked.txt").write_text(
                "untracked\n", encoding="utf-8"
            )

            git("merge-base", "--is-ancestor", baseline, "HEAD")
            scans = (
                git("diff", "--no-renames", "--name-only", f"{baseline}...HEAD"),
                git("diff", "--cached", "--no-renames", "--name-only"),
                git("diff", "--no-renames", "--name-only"),
                git("ls-files", "--others", "--exclude-standard"),
            )
            observed = {
                path
                for scan in scans
                for path in scan.stdout.splitlines()
                if path
            }
    except (OSError, subprocess.CalledProcessError) as exc:
        return [f"terminal path scan fixture failed to execute: {exc}"]

    expected = {
        "allowed/committed.txt",
        "allowed/renamed.txt",
        "allowed/staged.txt",
        "allowed/unstaged.txt",
        "allowed/untracked.txt",
        "forbidden/renamed.txt",
    }
    if observed != expected:
        return [
            "terminal path scan fixture coverage mismatch: "
            f"expected={sorted(expected)} observed={sorted(observed)}"
        ]
    return []


def _flat(s: str) -> str:
    return " ".join(s.split())


def _section_body(text: str, heading: str) -> str | None:
    """The flattened body of a section, from `heading` to the next ##/### heading."""
    i = text.find(heading)
    if i == -1:
        return None
    rest = text[i + len(heading):]
    end = len(rest)
    for marker in ("\n## ", "\n### "):
        j = rest.find(marker)
        if j != -1:
            end = min(end, j)
    return _flat(rest[:end])


HOMEOSTASIS_AXES = (
    "Oracle trustworthiness",
    "Product capability",
    "Failure legibility",
    "Specification coherence",
    "Intervention diversity",
)


def cross_file_pin_violations() -> list[str]:
    """U4: pin drift-prone restatements at the right granularity (dev/-local).

    NOT the locked classification matrix (SKILL.md target/halt/artifact/
    convergence/cadence-shape) — these are the five *homeostasis* axes, a
    disjoint set. AskUserQuestion has 5 sites; only judgment-default (owner) and
    the greenfield-invariants copy share line 1 verbatim — the others are
    intentional paraphrases and are not pinned.
    """
    v: list[str] = []
    frontier = read(FRONTIER_BODY)
    goal = read(ROOT / "loopgen/templates/bodies/goal-body.md")
    oracle = read(ROOT / "loopgen/references/oracle-principles.md")
    judgment = read(ROOT / "loopgen/primitives/judgment-default.md")
    greenfield_inv = read(ROOT / "loopgen/references/greenfield-invariants.md")
    frontier_flat = _flat(frontier)

    # (a) status-theater prohibition — byte-identical block in goal + frontier
    st_f = _section_body(frontier, "### Status-theater prohibition")
    st_g = _section_body(goal, "### Status-theater prohibition")
    if not st_f or not st_g:
        v.append("status-theater block missing from a body")
    elif st_f != st_g:
        v.append("status-theater block drifted between frontier and goal")

    # (b) FIXED != CLOSED — one shared sentence amid divergent framing
    closure = (
        "Closure requires either the next iteration's review pass "
        "explicitly confirming, or the next pass not re-raising the finding"
    )
    if closure not in frontier_flat:
        v.append("FIXED!=CLOSED shared sentence missing from frontier")
    if closure not in _flat(oracle):
        v.append("FIXED!=CLOSED shared sentence missing from oracle-principles")

    # (c) AskUserQuestion ban — shared opening (owner + greenfield copy)
    ban = "Never call `AskUserQuestion` or any interactive / blocking / approval-prompt"
    if ban not in _flat(judgment):
        v.append("AskUserQuestion ban missing from judgment-default")
    if ban not in _flat(greenfield_inv):
        v.append("AskUserQuestion ban missing from greenfield-invariants")

    # (d) homeostasis axes — the existing five, named; never extend
    axes_block = _section_body(frontier, "### Axes") or ""
    for name in HOMEOSTASIS_AXES:
        if name not in axes_block:
            v.append(f"homeostasis axis missing: {name}")
    if axes_block.count("- **") != len(HOMEOSTASIS_AXES):
        v.append("Axes block does not enumerate exactly five axes")
    if "all five homeostasis axes" not in frontier_flat:
        v.append("'all five homeostasis axes' literal missing")
    return v


def checkpoint_reason_closedset_violations() -> list[str]:
    """U5: the FRONTIER.json checkpoint_reason field must be EXACTLY the 6 prose
    enum values plus an explicitly-labeled `null` resting value — closing the
    pipe-delimited form where `| null` leaked past the presence-only check."""
    text = read(BENCHMARK_ARTIFACTS)
    line = next(
        (ln for ln in text.splitlines() if ln.strip().startswith("checkpoint_reason:")),
        None,
    )
    if line is None:
        return ["checkpoint_reason field missing from FRONTIER.json schema"]
    rhs = line.split(":", 1)[1].split("#", 1)[0]
    tokens = {t.strip() for t in rhs.split("|") if t.strip()}
    allowed = set(CHECKPOINT_REASON_VALUES) | {"null"}
    v: list[str] = []
    if tokens - allowed:
        v.append(f"non-enum checkpoint_reason tokens: {sorted(tokens - allowed)}")
    if set(CHECKPOINT_REASON_VALUES) - tokens:
        v.append(f"missing checkpoint_reason values: {sorted(set(CHECKPOINT_REASON_VALUES) - tokens)}")
    if "null" in tokens and "resting value" not in line:
        v.append("checkpoint_reason `null` present without labeling it the resting value")
    return v


def include_target_violations() -> list[str]:
    """U6: every {{INCLUDE x}} a body pulls must RESOLVE — the target needs a
    `---` spec separator (else include_text() raises a ContractError at render),
    and the runtime block below it must not leak authoring scaffolding
    (## Purpose / ## Include when). Greenfield's evidence-tier / halt-cause /
    queue INCLUDEs went dark here because the verifier only rendered frontier."""
    v: list[str] = []
    bodies = (FRONTIER_BODY,) + NON_FRONTIER_BODIES
    seen: set[str] = set()
    for body in bodies:
        for m in re.finditer(r"\{\{INCLUDE ([^}]+)\}\}", read(body)):
            rel = m.group(1).strip()
            if not rel.endswith(".md"):
                continue  # prose example (e.g. greenfield-body's "{{INCLUDE …}}"), not a real target
            if rel in seen:
                continue
            seen.add(rel)
            raw = read(ROOT / "loopgen" / rel)
            if "\n---\n" not in raw:
                v.append(f"{rel}: no '---' separator (INCLUDE would crash)")
                continue
            block = raw.split("\n---\n", 1)[1]
            if "## Purpose" in block or "## Include when" in block:
                v.append(f"{rel}: authoring scaffolding leaks below '---'")
    return v


# ── I2/I10: read-set existence, STATE-key cross-check, classify-mirror ──────


def _section_between(text: str, start_marker: str, end_marker: str) -> str:
    i = text.index(start_marker) + len(start_marker)
    j = text.index(end_marker, i)
    return text[i:j]


def derivation_read_set_violations() -> list[str]:
    """R1: every concrete `path.md` backtick-cited in SKILL.md's Derivation
    read contract (both tiers, plus the 'After classification, also read'
    conditional list) must exist under loopgen/. Placeholder paths like
    `archetypes/<nearest>.md` or `primitives/<axis>.md` are intentionally
    unresolvable at this level (the `<...>` template variable is not a
    filename character) and are skipped, not asserted."""
    skill = read(SKILL)
    start = skill.index("## Derivation read contract")
    end = skill.index("## Phase 1", start)
    section = skill[start:end]
    paths = sorted(set(re.findall(r"`([a-z][a-z0-9_-]*(?:/[a-z0-9_.-]+)*\.md)`", section)))
    if not paths:
        return ["no concrete read-set paths parsed from SKILL.md (parser drift?)"]
    return [p for p in paths if not (ROOT / "loopgen" / p).exists()]


def _common_state_keys(skill: str) -> list[str]:
    block = _section_between(
        skill,
        "**Required `.loop/<loop-id>/STATE.md` keys, every archetype:**",
        "**Archetype-specific `.loop/<loop-id>/STATE.md` keys:**",
    )
    keys: list[str] = []
    for span in re.findall(r"`([^`]+)`", block):
        m = re.match(r"[a-z][a-z0-9_]*", span)
        if m:
            keys.append(m.group(0))
    return keys


def _archetype_state_keys(skill: str, archetype: str) -> list[str]:
    m = re.search(rf"-\s*`{archetype}`\s*—\s*((?:`[a-z_]+`,?\s*)+)\.", skill)
    if not m:
        return []
    return re.findall(r"`([a-z_]+)`", m.group(1))


# Composer/provenance bookkeeping keys: SKILL.md's Phase 4 writes these once
# at emit time (archetype, identity, primitive_bundle, divergences, overlays,
# consult_tier, evaluator_tier, derivation_read_set, current_artifact); no
# archetype body's iteration-protocol prose narrates them in its own
# "Artifacts to maintain" section, and that gap is consistent across all four
# bodies — i.e. it is an intentional split between emit-time provenance and
# runner-facing iteration state, not per-archetype drift. `archetype` is left
# checkable since every body happens to name its own or a sibling archetype
# in prose (routing / wrong-loop text); the rest are excluded from R2 so the
# check stays focused on genuine iteration-state gaps.
_BOOKKEEPING_KEYS = frozenset(
    {
        "identity",
        "primitive_bundle",
        "divergences",
        "overlays",
        "consult_tier",
        "evaluator_tier",
        "derivation_read_set",
        "current_artifact",
    }
)


def state_key_body_violations() -> dict[str, list[str]]:
    """R2: every STATE.md key SKILL.md requires for an archetype (common +
    archetype-specific), excluding the emit-time bookkeeping keys in
    `_BOOKKEEPING_KEYS` (see comment above), should be mentioned somewhere in
    that archetype's body text — tolerant of `snake_case` vs "spaced words"
    (goal-body says "goal version", not `goal_version`), case, and a body's
    own soft line-wrap (e.g. "stuck\ncounters" across two source lines still
    reads as "stuck counters"). Returns {archetype: [missing keys]} for
    archetypes with a gap; empty dict if none."""
    skill = read(SKILL)
    common = _common_state_keys(skill)
    violations: dict[str, list[str]] = {}
    for archetype, path in BODY_PATHS.items():
        keys = [k for k in common + _archetype_state_keys(skill, archetype) if k not in _BOOKKEEPING_KEYS]
        body_text = re.sub(r"\s+", " ", read(path))
        missing = [
            key
            for key in keys
            if re.search(re.sub("_", "[_ ]", key), body_text, re.IGNORECASE) is None
        ]
        if missing:
            violations[archetype] = missing
    return violations


def _axis_matrix_from_skill(skill: str) -> tuple[dict[str, int], dict[str, dict[str, str]], dict[str, set[str]]]:
    start = skill.index("**Axes that vary by archetype**")
    end = skill.index("Max weighted-Hamming distance", start)
    table = skill[start:end]
    rows = [
        ln.strip()
        for ln in table.splitlines()
        if ln.strip().startswith("|") and not re.match(r"^\|[-\s|]+\|$", ln.strip())
    ]

    weights: dict[str, int] = {}
    defaults: dict[str, dict[str, str]] = {"frontier": {}, "goal": {}, "story": {}, "greenfield": {}}
    values: dict[str, set[str]] = {}
    for row in rows:
        cells = [c.strip() for c in row.strip("|").split("|")]
        if cells[0].lower() == "axis":
            continue
        axis = cells[0].strip("`")
        values[axis] = {v.strip() for v in cells[1].split("·")}
        defaults["frontier"][axis] = cells[2]
        defaults["goal"][axis] = cells[3]
        defaults["story"][axis] = cells[4]
        defaults["greenfield"][axis] = cells[5]
        weights[axis] = int(cells[6])
    return weights, defaults, values


def classify_mirror_violations() -> list[str]:
    """R3: SKILL.md's locked axis matrix (weights, per-archetype defaults,
    the value sets) must equal classify.py's WEIGHTS/DEFAULTS/VALUES —
    classify.py is documented as a mirror, not a second source of truth, so
    the two must never silently diverge. Also cross-checks the three
    documented contradiction pairs (finite-criteria + equilibrium /
    manual-gated / homeostatic-checkpoint) against classify.contradictions(),
    best-effort — SKILL.md's contradiction prose is not a table, so this half
    is a targeted match on the documented pairs, not a generic parser."""
    skill = read(SKILL)
    v: list[str] = []

    weights, defaults, values = _axis_matrix_from_skill(skill)
    if weights != classify.WEIGHTS:
        v.append(f"weights mismatch: SKILL.md={weights} classify.py={classify.WEIGHTS}")
    for archetype in defaults:
        if defaults[archetype] != classify.DEFAULTS.get(archetype):
            v.append(
                f"{archetype} defaults mismatch: SKILL.md={defaults[archetype]} "
                f"classify.py={classify.DEFAULTS.get(archetype)}"
            )
    for axis, vals in values.items():
        classify_vals = classify.VALUES.get(axis)
        if classify_vals != vals:
            v.append(
                f"{axis} values mismatch: SKILL.md={sorted(vals)} "
                f"classify.py={sorted(classify_vals) if classify_vals else None}"
            )

    contra_start = skill.find("**Contradictions**")
    contra_text = skill[contra_start:contra_start + 400] if contra_start != -1 else ""
    required_tokens = (
        "target: finite-criteria",
        "halt: equilibrium",
        "manual-gated",
        "convergence: homeostatic-checkpoint",
    )
    if contra_start == -1 or any(tok not in contra_text for tok in required_tokens):
        v.append("could not locate the documented contradiction pair text in SKILL.md (mirror check skipped)")
    else:
        documented_bundles = (
            {"target-shape": "finite-criteria", "halt-shape": "equilibrium"},
            {"target-shape": "finite-criteria", "halt-shape": "manual-gated"},
            {"target-shape": "finite-criteria", "convergence-shape": "homeostatic-checkpoint"},
        )
        for bundle in documented_bundles:
            if not classify.contradictions(bundle):
                v.append(f"classify.contradictions() does not flag documented pair: {bundle}")
    return v


# ── U11: context-stack memory-model contracts ──────────────────────────────


def _context_stack_archetype_keys(cs: str) -> dict[str, list[str]]:
    """Parse context-stack.md's `| <archetype> | <backticked keys> |` per-archetype
    STATE-key table into {archetype: [keys]}."""
    result: dict[str, list[str]] = {}
    for arch in ("goal", "story", "frontier", "greenfield"):
        m = re.search(rf"(?m)\|\s*`{arch}`\s*\|\s*(.+?)\s*\|\s*$", cs)
        if m:
            result[arch] = re.findall(r"`([a-z_]+)`", m.group(1))
    return result


def _context_stack_journal_types(cs: str) -> list[str]:
    """The record-type column of context-stack.md's JOURNAL.jsonl table (dropping
    the `t` header cell)."""
    i = cs.find("Record types (`t`)")
    if i == -1:
        return []
    block = cs[i:]
    j = block.find("Access:")
    if j != -1:
        block = block[:j]
    return [t for t in re.findall(r"(?m)^\|\s*`([a-z_]+)`\s*\|", block) if t != "t"]


def body_include_violations() -> list[str]:
    """U11: every archetype body must INCLUDE both `context-stack.md` and the
    queue-growth block — the two primitives SKILL.md claims every body carries
    (the audit caught the queue claim being false while no body wired it). A body
    that drops either INCLUDE silently loses the memory model / growth discipline."""
    v: list[str] = []
    for arch, path in BODY_PATHS.items():
        text = read(path)
        if CONTEXT_STACK_INCLUDE not in text:
            v.append(f"{arch} body missing {CONTEXT_STACK_INCLUDE}")
        if QUEUE_INCLUDE not in text:
            v.append(f"{arch} body missing {QUEUE_INCLUDE}")
    skill = read(SKILL)
    if "context-stack" not in skill:
        v.append("SKILL.md does not claim context-stack is emitted every prompt")
    if "queue-as-second-artifact" not in skill:
        v.append("SKILL.md does not claim queue-as-second-artifact is wired")
    return v


def tiered_read_violations() -> list[str]:
    """U11: no body's iteration protocol may mandate an unqualified whole-file read
    of an append-only artifact — each body's read step must carry the tiered-read
    vocabulary (a bounded `tail -n 20` journal read and an `index` queue read). A
    regression to whole-file reads drops these tokens."""
    v: list[str] = []
    for arch, path in BODY_PATHS.items():
        text = read(path)
        if "tail -n 20" not in text:
            v.append(f"{arch}: no bounded `tail -n 20` journal read in the protocol")
        if "index" not in text.lower():
            v.append(f"{arch}: no index/bounded queue-read language in the protocol")
    return v


def state_key_mirror_violations() -> list[str]:
    """U11: SKILL.md's STATE-key lists must mirror context-stack.md's schema, and
    every key moved out of STATE.md (to DERIVATION.md or JOURNAL.jsonl) must be
    absent from both SKILL STATE lists (common + per-archetype)."""
    skill = read(SKILL)
    cs = read(CONTEXT_STACK)
    v: list[str] = []

    common = _common_state_keys(skill)
    skill_state: set[str] = set(common)
    skill_arch: dict[str, set[str]] = {}
    for a in ("goal", "story", "frontier", "greenfield"):
        keys = set(_archetype_state_keys(skill, a))
        skill_arch[a] = keys
        skill_state |= keys

    for mk in MOVED_STATE_KEYS:
        if mk in skill_state:
            v.append(f"moved key `{mk}` still listed as a STATE.md key in SKILL.md")

    for k in common:
        if f"`{k}`" not in cs:
            v.append(f"SKILL common STATE key `{k}` absent from context-stack.md schema")

    cs_arch = _context_stack_archetype_keys(cs)
    for a in ("goal", "story", "frontier", "greenfield"):
        ck = set(cs_arch.get(a, []))
        if skill_arch[a] != ck:
            v.append(
                f"{a} STATE-key mirror mismatch: SKILL={sorted(skill_arch[a])} "
                f"context-stack={sorted(ck)}"
            )
    return v


def journal_enum_violations() -> list[str]:
    """U11: the JOURNAL.jsonl record-type enumeration must agree across
    context-stack.md (the schema table) and SKILL.md (the common-file contract),
    and context-stack.md's table must list exactly the canonical set."""
    cs = read(CONTEXT_STACK)
    skill = read(SKILL)
    v: list[str] = []
    canonical = set(JOURNAL_RECORD_TYPES)
    for t in JOURNAL_RECORD_TYPES:
        if f"`{t}`" not in cs:
            v.append(f"context-stack.md missing journal record type `{t}`")
        if f"`{t}`" not in skill:
            v.append(f"SKILL.md missing journal record type `{t}`")
    table = set(_context_stack_journal_types(cs))
    if table - canonical:
        v.append(f"context-stack journal table has non-canonical types: {sorted(table - canonical)}")
    if canonical - table:
        v.append(f"context-stack journal table missing types: {sorted(canonical - table)}")
    return v


def u13_hardening_violations() -> list[str]:
    """U13: the pre-ship hardening contracts (ADR 0004 amendment). The static
    verifier cannot prove runtime obedience, but it can prove the in-loop
    detector and the authority rules actually ride the emitted text:
    context-health check present and routed, tiers bound to access paths (no
    stale one-tier-per-artifact phrasing), queue index authoritative
    (single-writer), evidence write-ahead, structured no-promotion enum, and
    pressure decay/merge-before-halt."""
    v: list[str] = []
    cs = read(CONTEXT_STACK)
    composed = read(COMPOSED_PROMPT)
    queue = read(ROOT / "loopgen/primitives/queue-as-second-artifact.md")
    pressure = read(ROOT / "loopgen/primitives/pressure.md")

    emitted = cs.split("\n---\n", 1)[-1]
    if "### Context-health check" not in emitted:
        v.append("context-stack emitted block missing `### Context-health check`")
    for marker in ("parses as JSONL", "resolve", "index row", "pressure-cap", "derivation-gap"):
        if marker not in emitted:
            v.append(f"context-health block missing marker `{marker}`")
    if "write-ahead" not in emitted:
        v.append("context-stack emitted block missing evidence write-ahead rule")
    if "never truncate a required field" not in emitted:
        v.append("context-stack emitted block missing the no-truncation rule on journal records")
    if "access path" not in cs.split("\n---\n", 1)[0] or "access path" not in emitted:
        v.append("context-stack tiers not bound to access paths on both sides of ---")
    for stale in ("artifact is assigned **exactly one** tier", "artifact below has exactly one tier"):
        if stale in cs:
            v.append(f"stale one-tier-per-artifact phrasing survives: `{stale}`")
    if composed.lower().count("context-health check") < 2:
        v.append("composed-prompt.md Operational core spec must name the context-health check in §3a and assembly step 4")
    if "single-writer" not in queue or "index is authoritative" not in queue.lower():
        v.append("queue-as-second-artifact missing the index-authoritative single-writer rule")
    for reason in NO_PROMOTION_REASONS:
        if reason not in pressure:
            v.append(f"pressure.md no-promotion enum missing `{reason}`")
    if "no-effect" not in pressure or "consecutive consults" not in pressure:
        v.append("pressure.md missing repeated-no-effect decay rule")
    if "merge/retire pass first" not in pressure:
        v.append("pressure.md cap overflow must run a merge/retire pass before halting")
    return v


def u14_consolidation_violations() -> list[str]:
    """U14: the consolidation round is the contract-layer checkpoint (ADR 0005).
    Prove the emitted contracts carry the round: forced triggers alongside the
    cadence, the field read over the pressure set, the three-way substrate
    classification, debt-conserving merge, the recorded decision, the
    context-health consolidation line, the HUD recency stamp, and the
    stand-alone constraint on compose-time lens borrowing."""
    v: list[str] = []
    cs = read(CONTEXT_STACK)
    composed = read(COMPOSED_PROMPT)
    pressure = read(ROOT / "loopgen/primitives/pressure.md")

    emitted = cs.split("\n---\n", 1)[-1]
    if "### Consolidation round" not in emitted:
        v.append("context-stack emitted block missing the `### Consolidation round` section")
    for marker in (
        "correct-looking fixes",
        "impossible observation",
        "checked at\n   runtime",
        "inferred from config",
        "unverified",
        "suspected_substrate",
    ):
        if marker.replace("\n   ", " ") not in emitted.replace("\n   ", " "):
            v.append(f"consolidation round missing marker `{marker}`")
    health = emitted.split("### Context-health check", 1)[-1]
    if "consolidation" not in health:
        v.append("context-health check missing the consolidation-due line (line 7)")
    if "run the Consolidation round now" not in health:
        v.append("context-health routing missing the overdue/triggered-consolidation route")

    pressure_emitted = pressure.split("\n---\n", 1)[-1]
    if "## Consolidation" not in pressure_emitted:
        v.append("pressure.md emitted block missing the consolidation field-read section")
    for marker in ("one\nfield", "merged-into", "suspected_substrate", "last consolidation: iter N"):
        if marker.replace("\n", " ") not in pressure_emitted.replace("\n", " "):
            v.append(f"pressure.md field read missing marker `{marker}`")
    if "never a launder" not in pressure_emitted:
        v.append("pressure.md merge must be marked as never a launder (debt conserved)")

    flat_composed = " ".join(composed.split())
    if "never as a required dependency" not in flat_composed or "stand alone" not in flat_composed:
        v.append("composed-prompt.md lens borrowing missing the stand-alone / no-required-dependency constraint")
    return v


DIMENSION_OUTCOME_VALUES = ("pending", "admitted", "falsified", "handoff")

DISTURBED_AXIS_VALUES = (
    "oracle-trustworthiness",
    "product-capability",
    "failure-legibility",
    "specification-coherence",
)


def u15_vector_adequacy_violations() -> list[str]:
    """U15 (fva-U1): the earned frontier-dimension lifecycle contract is pinned.
    Pins the closed dimension_outcome enum, the outcome→status mapping, the
    probe→disturbed_axis mapping (closed four, never a candidate id), terminal
    non-mutation authority, the eight-dimension cap, the independence gate for
    same-pass closure, the checkpoint-record commit semantics, and seed-vs-live
    vector authority. Runtime placement and mode authority are pinned by U17."""
    if not FRONTIER_VECTOR_ADEQUACY.exists():
        return ["missing loopgen/primitives/frontier-vector-adequacy.md"]
    text = read(FRONTIER_VECTOR_ADEQUACY)
    if "\n---\n" not in text:
        return ["frontier-vector-adequacy.md missing the `---` spec separator"]
    v: list[str] = []
    emitted = text.split("\n---\n", 1)[-1]
    flat = " ".join(emitted.split())
    authoring_flat = " ".join(text.split("\n---\n", 1)[0].split())

    for stale in ("Currently dormant", "not yet composed into rendered prompts"):
        if stale in authoring_flat:
            v.append(f"vector-adequacy authoring contract still claims `{stale}`")

    for leak in ("## Purpose", "## Include when", "## Authoring guidance"):
        if leak in emitted:
            v.append(f"emitted block leaks authoring scaffolding `{leak}`")

    line = next((ln for ln in emitted.splitlines() if "dimension_outcome:" in ln), None)
    if line is None:
        v.append("dimension_candidate schema missing the dimension_outcome field")
    else:
        tokens = {t.strip() for t in line.split(":", 1)[1].split("|") if t.strip()}
        if tokens != set(DIMENSION_OUTCOME_VALUES):
            v.append(
                f"dimension_outcome enum must be exactly {DIMENSION_OUTCOME_VALUES}, "
                f"got {sorted(tokens)}"
            )

    for pin in (
        "`pending` → `OPEN`",
        "`admitted` → `CLOSED_CONFIRMED`",
        "`falsified` → `CLOSED_CONFIRMED`",
        "`handoff` → `PAUSED_EXTERNAL`",
    ):
        if pin not in flat:
            v.append(f"outcome→status mapping missing `{pin}`")

    for axis in DISTURBED_AXIS_VALUES:
        if f"`{axis}`" not in emitted:
            v.append(f"probe-axis mapping missing closed value `{axis}`")
    if "never enter" not in flat or "closed `disturbed_axis` vocabulary" not in flat:
        v.append("missing the candidate-id-never-a-disturbed_axis pin")

    for pin, name in (
        ("never mutate the live vector", "terminal non-mutation rule"),
        ("no live-vector delta", "terminal no-delta invariant"),
        ("never append a ninth", "eight-dimension cap"),
        ("at most **one** bounded probe attempt", "terminal single-probe bound"),
        ("one candidate per provisional-balance event", "single-candidate bound"),
    ):
        if pin not in flat:
            v.append(f"missing {name} (`{pin}`)")

    if "outside the candidate's change cone" not in flat:
        v.append("missing the independence gate (change-cone clause)")
    if "may not author, mutate, or validate its own confirming channel" not in flat:
        v.append("missing the self-confirmation prohibition")
    if "does not imply `stop-and-summarize`" not in flat:
        v.append("missing the checkpoint-record-does-not-halt pin")
    if "STATE is the sole authority" not in flat:
        v.append("missing the seed-vs-live authority statement")

    skill = read(SKILL)
    if "primitives/frontier-vector-adequacy.md" not in skill:
        v.append("SKILL.md frontier read list missing frontier-vector-adequacy")
    archetype = read(ROOT / "loopgen/archetypes/frontier.md")
    if "frontier-vector-adequacy" not in archetype:
        v.append("archetypes/frontier.md missing the dimension-lifecycle extra")
    if "body wiring lands with" in " ".join(archetype.split()):
        v.append("archetypes/frontier.md still describes vector adequacy as future wiring")
    return v


def u16_workset_identity_violations() -> list[str]:
    """U16 (fva-U2): storage, authority, and workset compatibility. Pins the
    four-field fresh closure contract + loop-id-as-version rule in the
    authoring surfaces (frontload-audit, halt-shape, context-stack), the
    seed-vs-live vector authority and compact row schema in the frontier body,
    and the legacy paths (three-field basis; name-only vector rows never
    dropped). The executable half lives in closure_basis_established and the
    guard_cases fixtures."""
    v: list[str] = []
    frontload = " ".join(read(FRONTLOAD_AUDIT).split())
    halt_shape = " ".join(read(ROOT / "loopgen/primitives/halt-shape.md").split())
    cs = " ".join(read(CONTEXT_STACK).split())
    body = " ".join(read(FRONTIER_BODY).split())

    for pin, where, name in (
        ("four named, non-empty fields", frontload, "frontload four-field contract"),
        ("`initial_frontier_vector`", frontload, "frontload fourth field"),
        ("`declared_workset_version: <loop-id>`", frontload, "frontload version rule"),
        ("full frontier scan", frontload, "frontload exhaustion criterion scope"),
        ("legacy back-compat only, never a fresh-composition path", frontload,
         "frontload legacy sentence"),
        ("`initial_frontier_vector`", halt_shape, "halt-shape fourth field"),
        ("never implies the frame changed", halt_shape, "version≠identity rule"),
        ("a derivation gap, never legacy", halt_shape, "halt-shape empty-field rule"),
        ("`declared_workset_version: <loop-id>`", cs, "DERIVATION version field"),
        ("write-once, so a running loop can never mint", cs, "no-self-mint rule"),
        ("(bootstrap seed)", body, "body seed label"),
        ("STATE is the sole authority for the live vector", body, "body live authority"),
        ("never dropped, never given an invented channel", body, "legacy row conversion"),
        ("never append a ninth dimension", body, "body cap"),
    ):
        if pin not in where:
            v.append(f"missing {name} (`{pin}`)")

    # max-pack arithmetic: the documented STATE schema at its documented worst
    # case — every common + frontier live key one line each, plus 12 in-force
    # pressure rows (one line each; the vector + guardrail keys stay one line
    # regardless of dimension count ≤ 8) — must fit the ~50-line PINNED bound.
    skill = read(SKILL)
    common = _common_state_keys(skill)
    frontier_keys = _archetype_state_keys(skill, "frontier")
    if not common or not frontier_keys:
        v.append("max-pack: state-key parsers returned empty (parser drift?)")
    else:
        max_pack = len(common) + len(frontier_keys) + 12
        if max_pack > 50:
            v.append(
                f"max-pack STATE arithmetic exceeds the ~50-line bound: "
                f"{len(common)} common + {len(frontier_keys)} frontier + 12 "
                f"pressure rows = {max_pack}"
            )
    return v


def u17_admission_wiring_violations() -> list[str]:
    """U17 (fva-U3): every vector-mutation path routes through the adequacy
    lifecycle. The expansion-ramp scan line is replaced by the vector-adequacy
    line; cash-out option 2 no longer instructs a direct vector edit; the
    benchmark green-trace expansion routes dimension growth through the
    lifecycle with atomic projection parity; the reopen-policy variants split
    the authority (equilibrium admits in-episode and continues, terminal never
    mutates and hands off); the shared halt precondition names the adequacy
    result."""
    v: list[str] = []
    body = read(FRONTIER_BODY)
    body_flat = " ".join(body.split())
    if "expansion ramp:" in body:
        v.append("expansion-ramp scan line survives in the body (must be replaced)")
    if "vector adequacy: <adequate" not in body:
        v.append("halt scan missing the vector-adequacy line")
    for non_halting_result in ("candidate-opened", "candidate-admitted"):
        if non_halting_result in next(
            (line for line in body.splitlines() if line.startswith("vector adequacy:")),
            "",
        ):
            v.append(
                f"halt scan admits non-halting vector result `{non_halting_result}`"
            )
    if "candidate-falsified-confirmed" not in body:
        v.append("halt scan does not distinguish confirmed falsification")
    if "update the frontier vector" in body_flat:
        v.append("direct vector-mutation instruction survives (cash-out option 2)")
    if "never a direct edit" not in body_flat:
        v.append("cash-out reroute missing the never-a-direct-edit clause")
    stale_early_halt = (
        "If all axes are in balance and no intervention is available, "
        "the loop is quiescent."
    )
    if stale_early_halt in body_flat:
        v.append("iteration protocol still declares quiescence before vector adequacy")
    if "provisional balance" not in body_flat or "not yet quiescent" not in body_flat:
        v.append("iteration protocol missing provisional-balance ordering")

    equilibrium = " ".join(reopen_policy_variant("equilibrium").split())
    terminal = " ".join(reopen_policy_variant("terminal").split())
    if "admitted in-episode" not in equilibrium:
        v.append("equilibrium variant missing in-episode admission authority")
    if "the loop continues" not in equilibrium:
        v.append("equilibrium variant missing admission-continues semantics")
    if "full frontier scan" not in equilibrium or "vector adequacy" not in equilibrium:
        v.append("equilibrium variant narrows the halt proof to homeostasis")
    if "admitted in-episode" in terminal or "may be **admitted" in terminal:
        v.append("terminal variant carries admission authority (must be handoff-only)")
    for pin, name in (
        ("never mutates", "terminal non-mutation"),
        ("`handoff` output for a new declared-workset version", "terminal handoff route"),
        ("at most one bounded probe attempt", "terminal single-probe bound"),
    ):
        if pin not in terminal:
            v.append(f"terminal variant missing {name} (`{pin}`)")
    if "full frontier scan" not in terminal or "vector adequacy" not in terminal:
        v.append("terminal variant narrows declared-workset exhaustion to homeostasis")

    bench = " ".join(read(BENCHMARK_FRONTIER).split())
    for pin, name in (
        ("through the vector-adequacy lifecycle", "green-trace reroute"),
        ("atomic projection change", "atomicity clause"),
        ("partial backfill means not admitted yet", "partial-backfill rule"),
        ("never a silent overspend", "backfill budget rule"),
    ):
        if pin not in bench:
            v.append(f"benchmark overlay missing {name} (`{pin}`)")
    artifacts = " ".join(read(BENCHMARK_ARTIFACTS).split())
    if "changes only through the frontier-vector admission" not in artifacts:
        v.append("FRONTIER role missing the pareto_dimensions parity rule")
    example = " ".join(read(BENCHMARK_EXAMPLE).split())
    for pin, name in (
        ("one evidence-anchored pressure-discovery expansion", "example bounded expansion"),
        ("vector adequacy resolves adequate", "example earned halt route"),
    ):
        if pin not in example:
            v.append(f"benchmark example missing {name} (`{pin}`)")

    halt_cause = " ".join(
        read(ROOT / "loopgen/primitives/halt-cause-classifier.md").split()
    )
    if "record the frontier-vector adequacy result" not in halt_cause:
        v.append("halt precondition missing the adequacy-result requirement")
    if "candidate awaiting its probe or next-pass confirmation" not in halt_cause:
        v.append("halt validity missing probe/confirmation invalidation")
    if "newly admitted dimension requiring continuation" not in halt_cause:
        v.append("halt validity missing admitted-dimension continuation")
    return v


# ── U1-c1: the Operational core is body-carried, parity-pinned, first-80 ───

OPERATIONAL_CORE_HEADING = "## Operational core"

OPERATIONAL_CORE_SHARED_TOKENS = (
    "The context window is a lossy cache",
    "sed -n '1,80p' .loop/<loop-id>/PROMPT.md",
    # U3: the mode-aware cadence law, pinned verbatim (the truth-table check
    # additionally parses the clause whole for enum exactness).
    "`rolling-lossy` → after any detected compaction",
    "`fresh-episode` → at every episode start",
    "`unknown` → at every iteration start (conservative — neither lifecycle assumed).",
    "**Context budget**",
    "| `.loop/<loop-id>/PRESSURE.md` | PINNED | in-force rows ≤ `pressure-cap` (default 12); re-read every pass |",
    "| `.loop/<loop-id>/STATE.md` | PINNED | ≤ ~50 lines, live status only; re-read every pass |",
    "| `JOURNAL.jsonl` tail-20 | WORKING | `tail -n 20 .loop/<loop-id>/JOURNAL.jsonl`; once per iteration |",
    "| journal by key · `archive/*` · `DERIVATION.md` | ON-DEMAND | keyed reads only (`jq` / section), never whole-file |",
    "| `VERIFY.md` (terminal only) · journal `checkpoint` records | WRITE-ONLY | written in-loop, never re-read |",
    "**Context-health check**",
    "a failed line is a routing",
    "**Halt causes (quick list):**",
    # One contiguous completion clause, not three separable sentences — text
    # inserted anywhere inside it (e.g. between the scan requirement and the
    # classifier pointer) now breaks the match.
    "No shared cause claims the artifact complete; any non-success halt "
    "requires the full search-surface scan first. The Halt section below "
    "carries the full classifier.",
    "**Iteration skeleton**",
    # U1 closeout: the human-watch one-liner and the health revalidation line
    # are shared content — pinned verbatim so neither single-body drift nor a
    # coordinated four-body edit can silently change or remove them.
    "Human watch: `tail -5 .loop/<loop-id>/JOURNAL.jsonl | jq -r "
    "'[.iter,.t,.ac//.id//.packet,(.verdict//.to//.question//.changed)"
    "|if (type==\"object\" or type==\"array\") then tojson else . end]|@tsv'`",
    "6. `consult_tier_effective` in `STATE.md` still matches this host "
    "(`n/a` at tier-0); stale after any runner change — re-verify before "
    "consulting.",
)


def _operational_core_section(raw_prompt: str) -> str | None:
    """The Operational core section text, heading to the next `## ` heading."""
    i = raw_prompt.find("\n" + OPERATIONAL_CORE_HEADING + "\n")
    if i == -1:
        return None
    rest = raw_prompt[i + 1:]
    j = rest.find("\n## ", 1)
    return rest[:j] if j != -1 else rest


def operational_core_violations() -> list[str]:
    """U1-c1 (F1): every archetype body carries exactly one Operational core,
    positioned between Motive and the runner-contract INCLUDE; the shared
    segments (intro paragraph, shared budget rows, context-health check,
    closing completion law) are pinned so the four copies cannot drift —
    only the WORKING queue row, the halt quick list, and the iteration
    skeleton legitimately vary by archetype."""
    v: list[str] = []
    intro_segments: dict[str, str] = {}
    health_segments: dict[str, str] = {}
    for archetype, path in BODY_PATHS.items():
        raw = raw_body_template(path)
        count = raw.count(OPERATIONAL_CORE_HEADING)
        if count != 1:
            v.append(f"{archetype}: expected exactly one Operational core, found {count}")
            continue
        motive = raw.find("## Motive")
        runner = raw.find("{{INCLUDE primitives/runner-contract.md}}")
        pos = raw.find(OPERATIONAL_CORE_HEADING)
        if not (motive != -1 and runner != -1 and motive < pos < runner):
            v.append(f"{archetype}: Operational core is not between Motive and the runner contract")
        # U1 closeout: adjacency, not mere ordering — nothing may sit between
        # the Motive slot and the core (the incidental end-bound headroom is
        # 0-1 lines at tier-1 today, and would silently reopen if the core
        # ever shrank).
        if "{{MOTIVE}}\n\n" + OPERATIONAL_CORE_HEADING + "\n" not in raw:
            v.append(f"{archetype}: Operational core is not immediately after the Motive slot")
        section = _operational_core_section(raw) or ""
        # U1 closeout: the run-host slot lives inside the core, between health
        # line 6 and the halt quick list — a coordinated relocation across all
        # four bodies preserved parity, so position is pinned per body.
        slot = section.find("{{RUN_HOST_VERIFICATION}}")
        item6 = section.find("6. `consult_tier_effective`")
        halt = section.find("**Halt causes")
        if slot == -1:
            v.append(f"{archetype}: RUN_HOST_VERIFICATION slot left the Operational core")
        elif not (item6 != -1 and halt != -1 and item6 < slot < halt):
            v.append(
                f"{archetype}: RUN_HOST_VERIFICATION slot is not between health "
                "line 6 and the halt quick list"
            )
        flat = _flat(section)
        for token in OPERATIONAL_CORE_SHARED_TOKENS:
            if token not in flat:
                v.append(f"{archetype}: Operational core missing shared token `{token[:44]}`")
        intro_segments[archetype] = flat.split("**Context budget**", 1)[0]
        health_segments[archetype] = (
            flat.split("**Context-health check**", 1)[-1].split("**Halt causes", 1)[0]
        )
    if len(set(intro_segments.values())) > 1:
        v.append("Operational core intro paragraph drifted between bodies")
    if len(set(health_segments.values())) > 1:
        v.append("Operational core context-health check drifted between bodies")
    return v


# The fixture PROVENANCE is one line (real: the 8-line composed-prompt format,
# +7) and the fixture MOTIVE is one line (a real one-sentence motive may wrap
# to two physical lines, +1), so a fixture render ending at N lands at N+8 in
# a real composition. The bound additionally banks two lines of real headroom:
# 80 - 7 - 1 - 2 = 70. The canonical-fixture check below measures the <= 78
# promise directly instead of by arithmetic.
OPERATIONAL_CORE_SENTINEL_BOUND = 70

EXPECTED_PROVENANCE_LINES = [
    "> **Loop provenance — composed by `/loopgen`.**",
    "> Archetype: `<nearest>`  ·  Divergences: `<axis: value (source); …>` or `none`.",
    "> Overlays: `<benchmark-frontier; …>` or `none`.",
    "> Consult-capability: `tier-N` (`<channel, or \"none — human-look gate substituted\">`).",
    "> Evaluator tier: `<T0–T6, or n/a>`.",
    "> Frontload — resolved: [`…`]; defaulted: [`…`]; open gaps: [`…`].",
    "> Primitive sources: `<files whose values diverged from the archetype defaults>`.",
    "> Re-derive (do not hand-edit) when intent, sources, or environment change.",
]


def production_provenance() -> str:
    """F6: the canonical provenance measured for the first-80 budget is
    EXTRACTED from composed-prompt.md's production `## Provenance preamble`
    fenced block, never hand-copied — so adding a provenance line
    automatically tightens the measured line budget instead of staying
    false-green. The block's `<...>` placeholders are irrelevant to a
    line-count measurement; only the line count is load-bearing."""
    text = read(COMPOSED_PROMPT)
    anchor = "## Provenance preamble (ALWAYS"
    i = text.find(anchor)
    if i == -1:
        raise ContractError("composed-prompt.md: production provenance preamble not found")
    # Line-anchored fences (whole ```md / ``` lines), not substring finds, so a
    # stray inline ``` cannot mis-bound the block.
    fence = re.search(r"(?m)^```md$", text[i:])
    if not fence:
        raise ContractError("composed-prompt.md: provenance preamble has no whole-line ```md fence")
    start = i + fence.end() + 1
    close = re.search(r"(?m)^```$", text[start:])
    if not close:
        raise ContractError("composed-prompt.md: provenance ```md fence is unclosed")
    block = text[start: start + close.start()].rstrip("\n")
    lines = block.splitlines()
    # The provenance preamble is a FIXED literal template (its values are the
    # `<placeholder>` tokens, not runtime-filled), so the block is verified by
    # exact whole-line equality against the canonical eight lines. This is the
    # closed full-match: any reorder, collapse, decoy label, inline duplicate,
    # trailing residue, or whitespace drift fails, and adding a ninth line
    # still trips the budget measurement downstream.
    if lines != EXPECTED_PROVENANCE_LINES:
        for idx, (got, want) in enumerate(zip(lines, EXPECTED_PROVENANCE_LINES)):
            if got != want:
                raise ContractError(
                    f"composed-prompt.md: provenance row {idx} is `{got[:70]}` "
                    f"(want `{want[:70]}`)"
                )
        raise ContractError(
            f"composed-prompt.md: provenance block has {len(lines)} rows, "
            f"want exactly {len(EXPECTED_PROVENANCE_LINES)}"
        )
    return block


CANONICAL_MOTIVE = (
    "Keep the visible product surface honest against its storyboard overnight,\n"
    "promoting only fixture-clean stories — a two-line motive exercising wrap."
)


def operational_core_render_violations() -> list[str]:
    """U1-c1 (F1): in every render path — render_frontier (both variants) and
    render_body (all four archetypes, tier-0 and tier-1 with the run-host
    block filled) — the Operational core appears exactly once, starts near
    the top, and ENDS within the sentinel bound, so the promised
    `sed -n '1,80p'` rehydration read captures it under a real 8-line
    provenance preamble too."""
    v: list[str] = []
    renders: dict[str, str] = {
        "frontier-pure": render_frontier(benchmark_overlay=False),
        "frontier-benchmark": render_frontier(benchmark_overlay=True),
    }
    for archetype in BODY_PATHS:
        renders[f"render_body-{archetype}-tier0"] = render_body(archetype)
        renders[f"render_body-{archetype}-tier1"] = render_body(
            archetype, consult_tier=1
        )
    for name, text in renders.items():
        lines = text.splitlines()
        starts = [i + 1 for i, line in enumerate(lines) if line.strip() == OPERATIONAL_CORE_HEADING]
        if len(starts) != 1:
            v.append(f"{name}: expected exactly one Operational core, found {len(starts)}")
            continue
        start = starts[0]
        if start > 20:
            v.append(f"{name}: Operational core starts at line {start} (> 20)")
        end = next(
            (i + 1 for i, line in enumerate(lines) if i + 1 > start and line.startswith("## ")),
            len(lines),
        )
        if end > OPERATIONAL_CORE_SENTINEL_BOUND:
            v.append(
                f"{name}: Operational core runs to line {end} "
                f"(> {OPERATIONAL_CORE_SENTINEL_BOUND}; the first-80 "
                "rehydration bound breaks under a real provenance preamble)"
            )
    return v


def operational_core_canonical_violations() -> list[str]:
    """U3: the first-80 promise measured DIRECTLY under canonical fixtures —
    the real 8-line provenance preamble and a two-physical-line motive — for
    every archetype at tier-0 and tier-1 plus render_frontier. The core must
    end by line 78, keeping >= 2 lines of real headroom inside the promised
    `sed -n '1,80p'` rehydration read."""
    v: list[str] = []
    overrides = {"PROVENANCE": production_provenance(), "MOTIVE": CANONICAL_MOTIVE}
    renders: dict[str, str] = {
        "frontier-pure-canonical": render_frontier(
            benchmark_overlay=False, placeholder_overrides=overrides
        ),
    }
    for archetype in BODY_PATHS:
        for tier in (0, 1):
            renders[f"{archetype}-tier{tier}-canonical"] = render_body(
                archetype, consult_tier=tier, placeholder_overrides=overrides
            )
    for name, text in renders.items():
        lines = text.splitlines()
        starts = [
            i + 1 for i, line in enumerate(lines)
            if line.strip() == OPERATIONAL_CORE_HEADING
        ]
        if len(starts) != 1:
            v.append(f"{name}: expected exactly one Operational core, found {len(starts)}")
            continue
        end = next(
            (i + 1 for i, line in enumerate(lines) if i + 1 > starts[0] and line.startswith("## ")),
            len(lines),
        )
        if end > 78:
            v.append(
                f"{name}: core ends at line {end} under canonical provenance "
                "(> 78; the first-80 promise keeps < 2 lines of real headroom)"
            )
    return v


def run_host_verification_violations() -> list[str]:
    """U1-c3 (F3 + the never-emitted residual): the Run-host channel check is
    a real emittable block — filled inside the Operational core at consult
    tier ≥ 1, stripped byte-identical at tier-0 — and consult_tier_effective
    is canonical STATE with a revalidation line in every body's health
    check."""
    v: list[str] = []
    marker = "**Run-host channel check**"
    for archetype in BODY_PATHS:
        tier0 = render_body(archetype)
        tier1 = render_body(archetype, consult_tier=1)
        if marker in tier0:
            v.append(f"{archetype}: run-host check leaked into a tier-0 render")
        if "{{RUN_HOST" in tier0 or "{{RUN_HOST" in tier1:
            v.append(f"{archetype}: dead RUN_HOST_VERIFICATION placeholder survives")
        if tier1.count(marker) != 1:
            v.append(
                f"{archetype}: expected exactly one run-host check at tier-1, "
                f"found {tier1.count(marker)}"
            )
        # U1 closeout: emitted inside the Operational core, not merely present.
        if marker not in (_operational_core_section(tier1) or ""):
            v.append(
                f"{archetype}: run-host check emitted outside the Operational "
                "core at tier-1"
            )
        flat1 = one_line(tier1)
        if "consult_tier_effective" not in flat1:
            v.append(f"{archetype}: tier-1 render never names consult_tier_effective")
        # step 2.2: the freshness AUTHORITY (context-stack, ungated) must emit at
        # EVERY tier — including tier-0, where the run-host block strips entirely.
        for tier_name, text in (("tier-0", tier0), ("tier-1", tier1)):
            if "no consult contract to keep fresh" not in one_line(text):
                v.append(
                    f"{archetype}/{tier_name}: consult-freshness authority absent "
                    "from the render (context-stack Context-health check)"
                )
    for name in ("pure", "benchmark"):
        text = render_frontier(benchmark_overlay=(name == "benchmark"))
        if marker in text or "{{RUN_HOST" in text:
            v.append(f"render_frontier-{name}: run-host check must strip at tier-0")
    skill = read(SKILL)
    cs = read(CONTEXT_STACK)
    if "`consult_tier_effective`" not in skill:
        v.append("SKILL.md required STATE keys omit consult_tier_effective")
    if "`consult_tier_effective`" not in cs:
        v.append("context-stack.md STATE schema omits consult_tier_effective")
    if "\n---\n" not in read(CONSULT_CAPABILITY):
        v.append("consult-capability.md has no emittable block below a '---'")
    # U1 closeout: continuous revalidation is a contract, not a courtesy —
    # the emitted block and the spec both carry it (neither is golden-pinned,
    # so removing the language stayed green before these pins).
    # step 2.2: freshness is AUTHORED in context-stack (emits in every family and
    # tier); the gated run-host block only REFERENCES it. Conjuncts pinned
    # independently so a partial rewrite cannot pass.
    ctx_flat = one_line(resolve_gated_block(CONTEXT_STACK))
    for pin, label in (
        ("there is no consult contract to keep fresh",
         "tier-0 has no consult contract"),
        ("A runner change, or any promised channel failing, invalidates the cached value",
         "runner/channel failure invalidates the cache"),
        ("re-verify the promised channels **non-interactively**",
         "re-verification is non-interactive"),
        ("overwrite the value and its per-channel basis",
         "value + basis are overwritten"),
        ("degrade **only** the channels that are actually missing",
         "only missing channels degrade"),
    ):
        if pin not in ctx_flat:
            v.append(f"context-stack lost the consult-freshness conjunct: {label}")
    cc_flat = one_line(resolve_gated_block(CONSULT_CAPABILITY))
    if "health line 6" in cc_flat:
        v.append("consult-capability run-host block still cites a body line number")
    if "Context-health check" not in cc_flat:
        v.append(
            "consult-capability run-host block does not reference the co-emitted "
            "Context-health authority"
        )
    if "absent or stale" not in cc_flat:
        v.append(
            "consult-capability run-host entry still self-gates on presence, "
            "not freshness"
        )
    consult_flat = one_line(read(CONSULT_CAPABILITY))
    for pin in (
        "re-verifies (overwrite-in-place, never trusting the cached value)",
        "a cached effective tier must not outlive its host",
    ):
        if pin not in consult_flat:
            v.append(f"consult-capability.md lost its revalidation law: `{pin}`")
    return v


# ── U1-c2: exact D/B/C tier filtering + advisory-authority language ────────


def subagent_pattern_filter_violations() -> list[str]:
    """U1-c2 (F2): render_body emits exactly the bullets each (tier,
    pollable-channel) case meets — with negative assertions, so a tier-3
    pattern can never be inlined at tier ≤ 2 again. Also pins the advisory
    language (a separate look is never acceptance authority) and bans
    unearned independence claims in the emitted block."""
    markers = {"D": "- **D — ", "B": "- **B — ", "C": "- **C — "}
    cases = (
        # (tier, pollable, want_d, want_b, want_c)
        (0, False, False, False, False),
        (0, True, False, False, False),
        (1, False, True, False, False),
        (1, True, True, False, True),
        (2, False, True, False, False),
        (2, True, True, False, True),
        (3, False, True, True, True),
        (3, True, True, True, True),
    )
    v: list[str] = []
    for tier, pollable, want_d, want_b, want_c in cases:
        text = render_body("story", consult_tier=tier, pollable_channel=pollable)
        wanted = {"D": want_d, "B": want_b, "C": want_c}
        for pattern, marker in markers.items():
            # U1 closeout: exact count, not presence — a duplicated bullet in
            # the source block satisfied the old presence check.
            n = text.count(marker)
            want = 1 if wanted[pattern] else 0
            if n != want:
                v.append(
                    f"tier-{tier} pollable={pollable}: pattern {pattern} "
                    f"appears {n}x, expected {want}"
                )
        block_present = "## Subagent patterns" in text
        if (tier == 0) == block_present:
            v.append(
                f"tier-{tier}: subagent block "
                f"{'present' if block_present else 'absent'} (gate broken)"
            )
        if tier >= 1:
            flat = one_line(text)
            for pin in (
                "never a required gate",
                "None is required to accept an iteration",
                "advisory, never acceptance authority",
                "Emitted is not verified",
            ):
                if pin not in flat:
                    v.append(f"tier-{tier}: advisory pin missing: `{pin}`")
    emitted_block = resolve_gated_block(SUBAGENT_PATTERNS)
    for pattern, marker in markers.items():
        n = emitted_block.count(marker)
        if n != 1:
            v.append(f"source block carries {n}x pattern {pattern}, expected exactly 1")
    if re.search(r"independen", emitted_block, re.IGNORECASE):
        v.append(
            "emitted subagent block claims independence — separation is not "
            "attested isolation; say `separate`"
        )
    # U1 closeout (P2): the compose-detected tier is a detection record, not a
    # liveness claim — every pattern instruction subordinates to the run-host
    # consult_tier_effective (+ per-channel basis).
    flat_block = one_line(emitted_block)
    for pin in (
        "detected on the composing host",
        "`consult_tier_effective` in `STATE.md` (value + per-channel basis",
        "treat that pattern as absent on this runner",
    ):
        if pin not in flat_block:
            v.append(f"emitted subagent block lost its effective-tier pin: `{pin}`")
    for stale in ("this host's consult channel", "consult tier are live"):
        if stale in flat_block:
            v.append(
                f"emitted subagent block presents the compose-detected tier as "
                f"live on this host: `{stale}`"
            )
    return v


# ── U1-c5: evidence-tier names the goal exclusion it always practiced ──────


def evidence_tier_goal_violations() -> list[str]:
    """U1-c5 (adjudicated residual): evidence-tier.md's Include-when claimed
    'every composed prompt' while the recipe (§8) and SKILL.md deliberately
    exclude `goal` — goal's evidence surface is oracle principles + the
    acceptance inventory. The primitive must name the exclusion, goal must
    stay Signal-hierarchy-free, and the three carrying bodies must keep it."""
    v: list[str] = []
    et = read(ROOT / "loopgen/primitives/evidence-tier.md")
    include_when = _section_body(et, "## Include when") or ""
    if "except `goal`" not in include_when:
        v.append("evidence-tier.md Include-when does not name the goal exclusion")
    goal_template = raw_body_template(GOAL_BODY)
    if "## Signal hierarchy" in goal_template or "evidence-tier.md}}" in goal_template:
        v.append("goal template carries a Signal hierarchy / evidence-tier INCLUDE")
    if "## Signal hierarchy" in render_body("goal"):
        v.append("goal render emits a standalone Signal hierarchy section")
    # U1 closeout (P3): goal's always-on pressure block consumes the tier-1/2
    # vocabulary, so the goal body must define the mapping it excludes the
    # hierarchy for — and the primitive's Include-when must name that mapping.
    goal_flat = one_line(render_body("goal"))
    for pin in (
        "**Evidence tiers for this loop.**",
        "never satisfy or retire a pressure row",
    ):
        if pin not in goal_flat:
            v.append(f"goal render lost its pressure tier mapping: `{pin}`")
    if "compact tier mapping" not in include_when:
        v.append("evidence-tier.md Include-when does not name the goal tier mapping")
    if "## Signal hierarchy" not in read(FRONTIER_BODY):
        v.append("frontier body lost its inline Signal hierarchy")
    for path in (STORY_BODY, GREENFIELD_BODY):
        if "{{INCLUDE primitives/evidence-tier.md}}" not in read(path):
            v.append(f"{path.stem} lost its evidence-tier INCLUDE")
    return v


# ── U1-c4: derivation provenance is owned by write-once DERIVATION.md ──────


# Fail-CLOSED derivation-ownership check, bounded to the CLAUSE containing each
# mention (not a ±140 char window, so unrelated prose two sentences away cannot
# false-red). Within its clause a `derivation_read_set` mention must (a) name
# DERIVATION.md as the home and (b) contain no competing artifact filename
# except in the one sanctioned form — a contrastive exclusion ("not `STATE.md`",
# "unlike `STATE.md`"). Any competitor in any other relation ("in `STATE.md`",
# "`STATE.md` stores …", "→ `STATE.md`", or a bare unrecognized mention) fails.
# Clause boundaries are sentence/`;` terminators followed by whitespace;
# filename periods (".md", ".loop/") are never boundaries (no trailing space).
_CLAUSE_BOUND = re.compile(r"[.;]\s")
_OWN_EXCLUDE = re.compile(r"(?:\bnot|\bnever|\bunlike|rather\s+than|instead\s+of)\s+(?:in\s+)?`?$", re.I)
# Negation of DERIVATION.md AS THE HOME — a negation directly governing a
# storage word (closed set) that leads to DERIVATION.md ("is not stored in
# DERIVATION.md"), or "DERIVATION.md is not …". "never changes in DERIVATION.md"
# does NOT match: "changes" is not a storage word, so DERIVATION.md stays home.
# The gap uses `[^;]` (not `[^.;]`) so it crosses the periods in the repo's
# canonical path `.loop/<loop-id>/DERIVATION.md`; the clause is already
# sentence-bounded, so widening the gap cannot reach a neighbouring statement.
_STORAGE = r"(?:stored|kept|held|recorded|lives?|located|belongs?|placed|written|home)"
_HOME_NEG = re.compile(
    r"\b(?:not|never|n't)\s+(?:\w+\s+){0,2}?" + _STORAGE + r"\b[^;]{0,60}?DERIVATION\.md", re.I
)
_HOME_NEG2 = re.compile(r"DERIVATION\.md`?[^;]{0,25}?\bis\s+not\b", re.I)


def _clause_around(flat: str, start: int, end: int) -> str:
    lo = 0
    for m in _CLAUSE_BOUND.finditer(flat, 0, start):
        lo = m.end()
    hi = len(flat)
    m = _CLAUSE_BOUND.search(flat, end)
    if m:
        hi = m.start() + 1
    return flat[lo:hi]


def derivation_ownership_violations() -> list[str]:
    """U1-c4 (F6/R3): ADR 0004 moved the derivation record
    (derivation_read_set, classification, frontload) out of STATE.md into
    write-once DERIVATION.md. Around every mention, DERIVATION.md must be the
    named home, unnegated, and no competing file (STATE.md / JOURNAL.jsonl)
    may be the assignment target. A structural guard, not proximity: the
    legit contrastive shape ("in `DERIVATION.md`, not `STATE.md`") passes and
    the reassignment shapes ("in `STATE.md`"; "DERIVATION.md is not its home
    … in STATE.md") are caught. It is a drift heuristic — deliberately
    ownership-lying prose can still evade it — not a semantic parser."""
    v: list[str] = []
    # U1 closeout: scan every skill source file plus the README — the former
    # four-file list left the body templates free to reassign ownership.
    # docs/adr/ stays out deliberately: ADRs may describe the pre-move world.
    scanned = tuple(
        (str(path.relative_to(ROOT)), path)
        for path in sorted((ROOT / "loopgen").rglob("*.md")) + [ROOT / "README.md"]
    )
    needle = "derivation_read_set"
    for label, path in scanned:
        flat = one_line(read(path))
        start = 0
        while True:
            i = flat.find(needle, start)
            if i == -1:
                break
            start = i + len(needle)
            clause = _clause_around(flat, i, start)
            if "DERIVATION.md" not in clause:
                v.append(f"{label}: derivation_read_set clause names no DERIVATION.md home: `…{clause[:120]}…`")
                continue
            if _HOME_NEG.search(clause) or _HOME_NEG2.search(clause):
                v.append(f"{label}: derivation_read_set clause negates the DERIVATION.md home: `…{clause[:120]}…`")
                continue
            flagged = False
            for comp in ("STATE.md", "JOURNAL.jsonl"):
                for cm in re.finditer(re.escape(comp), clause):
                    if not _OWN_EXCLUDE.search(clause[max(0, cm.start() - 16): cm.start()]):
                        v.append(
                            f"{label}: derivation_read_set clause names {comp} not as an "
                            f"exclusion: `…{clause[:120]}…`"
                        )
                        flagged = True
                        break
                if flagged:
                    break
    readme_flat = one_line(read(ROOT / "README.md"))
    if "DERIVATION.md` records classification and frontload" not in readme_flat:
        v.append("README.md durable-state bullet no longer names DERIVATION.md as the classification/frontload record")
    return v


def derivation_scope_violations() -> list[str]:
    """U1 closeout (P1): the derivation-record instruction must be obeyable by
    every invocation mode. A decline emits no artifacts and mints no loop id
    (SKILL.md loop-necessity gate), and DERIVATION.md is write-once at
    bootstrap (context-stack.md), so only successful composition may persist
    `derivation_read_set`; declines report their read list in the decline
    response, Diagnostic mode in its diagnostic output."""
    v: list[str] = []
    skill_flat = one_line(read(SKILL))
    for pin in (
        "Persisting that list is scoped to successful composition",
        "names its Tier-1 read list in the decline response",
        "never writes the target loop's write-once `DERIVATION.md`",
        "records whichever tiers the successful composition actually read",
    ):
        if pin not in skill_flat:
            v.append(f"SKILL.md derivation read contract lost its scope pin: `{pin}`")
    if "Every authoring run reads a bounded, provenance- relevant set of files and records" in skill_flat:
        v.append("SKILL.md re-acquired the unscoped every-run-records instruction")
    readme_flat = one_line(read(ROOT / "README.md"))
    if "On successful composition, record `derivation_read_set`" not in readme_flat:
        v.append("README.md Skill Behavior bullet lost its successful-composition scope")
    if "Always record `derivation_read_set`" in readme_flat:
        v.append("README.md re-acquired the unscoped always-record bullet")
    return v


def context_mode_violations() -> list[str]:
    """U2: the context-mode split — a compiler-owned request in the DERIVATION
    frontload, a run-host resolution in STATE — under the strict authority
    rule: `context_mode_effective` resolves only from operator-declared /
    runner-attested / unknown. Observation is never a basis — model-visible
    history proves neither mode (a fresh runner may be handed replayed
    context; a rolling window may already be compacted); what the window
    shows is recorded separately as `history_visibility_observed`."""
    v: list[str] = []
    emitted = one_line(resolve_gated_block(CONTEXT_STACK))
    for pin in (
        "`context_mode_effective`",
        "`operator-declared` / `runner-attested` / `unknown` — never observation",
        "proves neither mode",
        "`history_visibility_observed`",
        "never converts into a mode claim",
        "`context_mode_requested`",
        "`context_mode_compose_basis`",
        "compiler-owned half of the context-mode split",
    ):
        if pin not in emitted:
            v.append(f"context-stack emitted block missing context-mode pin: `{pin}`")
    skill_flat = one_line(read(SKILL))
    for pin in (
        "`context_mode_effective`, `context_mode_resolution_basis`",
        "operator-declared / runner-attested / unknown — never observation",
        "`context_mode_requested`",
        "never inferred from what the composing window shows",
        # F5: the reservation must live in emitted + SKILL authority, not
        # only the ADR — else the loop can invent the deferred runner protocol.
        "runner-attested is reserved, no current producer",
    ):
        if pin not in skill_flat:
            v.append(f"SKILL.md missing context-mode pin: `{pin}`")
    # F5: the emitted context-stack block carries the reservation too.
    if "`runner-attested` is reserved — no current runner emits an attestation" not in emitted:
        v.append("context-stack emitted block omits the runner-attested reservation")
    if "Runner attestation is **reserved**" not in one_line(read(CONTEXT_STACK)):
        v.append("context-stack memory-model intro omits the runner-attested reservation")
    for archetype in BODY_PATHS:
        flat = one_line(render_body(archetype))
        if "context_mode_effective" not in flat or "proves neither mode" not in flat:
            v.append(f"{archetype}: render lost the context-mode schema")
        # step 2.2b: every Operational-core intro PROJECTS the cadence; the
        # authority is context-stack. Same canonical table, both sides.
        for mode, when in REHYDRATION_CADENCE:
            if when not in flat:
                v.append(
                    f"{archetype}: Operational-core cadence projection lost "
                    f"`{mode}` -> {when}"
                )
    # step 2.2b: the cadence AUTHORITY itself (context-stack, ungated, 56/56).
    for mode, when in REHYDRATION_CADENCE:
        if f"`{mode}`" not in emitted or when not in emitted:
            v.append(
                f"context-stack rehydration-cadence authority missing "
                f"`{mode}` -> {when}"
            )
    # the trigger/basis firewall: observation may FIRE the cadence, never RESOLVE
    # the mode. Without this, cadence language silently reopens observation as a
    # resolution basis.
    for pin in (
        "A trigger is not a basis",
        "fires the cadence for an **already-resolved** mode",
        "neither determines `context_mode_effective`",
    ):
        if pin not in emitted:
            v.append(
                f"context-stack rehydration-cadence missing firewall pin: `{pin}`"
            )
    # Exactness, not presence: the closed sets admit no extra authority — an
    # added basis (e.g. model-observed) is a violation even though every
    # required token is still present.
    basis = re.search(
        r"`context_mode_resolution_basis` from the closed set (.+?)— never observation",
        emitted,
    )
    # Full-match the ENTIRE slash-delimited grammar, not a token extraction:
    # the captured span must equal the canonical expression exactly, so any
    # residue — an unquoted `model.observed /` prefix, a reordering, an extra
    # member in any quoting — fails, not just backticked odd members.
    BASIS_GRAMMAR = "`operator-declared` / `runner-attested` / `unknown`"
    MODE_GRAMMAR = "`fresh-episode` / `rolling-lossy` / `unknown`"
    if not basis:
        v.append("context-stack: resolution-basis closed-set sentence not parseable")
    elif basis.group(1).strip() != BASIS_GRAMMAR:
        v.append(f"context-stack: resolution-basis grammar drifted: `{basis.group(1).strip()}`")
    for label, pattern in (
        ("effective-mode", r"`context_mode_effective` — [^(]*\(([^)]+)\)"),
        ("requested-mode", r"`context_mode_requested` \(([^)]+)\)"),
    ):
        m = re.search(pattern, emitted)
        if not m:
            v.append(f"context-stack: {label} enum not parseable")
        elif m.group(1).strip() != MODE_GRAMMAR:
            v.append(f"context-stack: {label} enum grammar drifted: `{m.group(1).strip()}`")
    skill_basis = re.search(
        r"`context_mode_resolution_basis`\s*\(([^)]+)\)", skill_flat
    )
    if not skill_basis:
        v.append("SKILL.md: resolution-basis parenthetical not parseable")
    else:
        prefix = skill_basis.group(1).split("—")[0].strip()
        if prefix != "operator-declared / runner-attested / unknown":
            v.append(f"SKILL.md: resolution-basis grammar drifted: `{prefix}`")
        if "runner-attested is reserved, no current producer" not in skill_flat:
            v.append("SKILL.md: resolution-basis parenthetical lost the reservation clause")
    # U3 truth table: the core's cadence clause pairs each mode with exactly
    # its cadence — parsed and compared whole, so an added mode or a swapped
    # cadence fails even while every individual token is still present.
    expected_cadence = (
        "`rolling-lossy` → after any detected compaction; "
        "`fresh-episode` → at every episode start; "
        "`unknown` → at every iteration start (conservative — neither lifecycle assumed)"
    )
    for archetype in BODY_PATHS:
        flat = one_line(render_body(archetype))
        m = re.search(r"\(`STATE\.md`\) sets: (.+?)\. Read keys,", flat)
        if not m:
            v.append(f"{archetype}: core cadence clause not parseable")
        elif m.group(1) != expected_cadence:
            v.append(f"{archetype}: cadence truth table drifted: `{m.group(1)[:90]}`")
    return v


def human_look_gate_violations() -> list[str]:
    """The consult fallback is ALWAYS carried — a consulted prompt may
    lawfully downgrade to effective tier-0 mid-run (the Run-host channel
    check), so every render at every tier must define the gate exactly once,
    dormant behind its in-block liveness condition. Packets are provisional
    (never pressure payment, finding closure, or acceptance authority) and
    join the canonical journal schema (packet + question fields, surfaced by
    the watch projection). No render carries an executable phantom-consult
    instruction."""
    marker = "## Human-look gate (consult fallback)"
    phantom = "ask the available consult channel"
    v: list[str] = []
    renders: dict[str, str] = {
        "frontier-pure": render_frontier(benchmark_overlay=False),
        "frontier-benchmark": render_frontier(benchmark_overlay=True),
    }
    for archetype in BODY_PATHS:
        for tier in (0, 1, 2, 3):
            renders[f"{archetype}-tier{tier}"] = render_body(archetype, consult_tier=tier)
    for name, text in renders.items():
        if text.count(marker) != 1:
            v.append(f"{name}: expected exactly one human-look gate, found {text.count(marker)}")
        if "{{HUMAN_LOOK" in text:
            v.append(f"{name}: dead HUMAN_LOOK_GATE placeholder survives")
        if phantom in text:
            v.append(f"{name}: render still instructs `{phantom}`")
        flat = one_line(text)
        for pin in (
            "**Live condition.**",
            # The live PREDICATE itself, not just the later dormancy sentence:
            # flipping "effectively tier-0" to "tier-1" here must red.
            "This gate is live wherever consult capability is *effectively* tier-0",
            # Dormancy is the whole point of always-carrying the gate: a
            # mutation that makes it fire under a live consult channel must
            # break this pin, not stay green.
            "While a live consult channel covers a need, the gate stays dormant.",
            "cannot pay a pressure row, close a finding, or serve as acceptance authority",
            "reversible probes only",
            "`packet` (stable id, `hlp-<iter>-<n>`)",
            "else the tier-0 Human-look gate's review packet",
            CANONICAL_WATCH_PROJECTION,
        ):
            if pin not in flat:
                v.append(f"{name}: human-look gate pin missing: `{pin}`")
    for name in ("frontier-pure", "frontier-benchmark"):
        flat = one_line(renders[name])
        if "route the trace bundle to the consult resolution" not in flat:
            v.append(f"{name}: structural bridge lost its consult-resolution routing")
        # The bridge must branch on effective tier — the live channel OR the
        # tier-0 packet — not issue an unconditional consult instruction.
        if "`consult_tier_effective` proves live, or at tier-0 the" not in flat:
            v.append(f"{name}: structural bridge lost its effective-tier branch")
        if "provisional and self-authored" not in flat:
            v.append(f"{name}: bridge tier-0 classification is not marked provisional")
    if "cites the packet id and stays provisional" not in one_line(
        renders["frontier-benchmark"]
    ):
        v.append("frontier-benchmark: consult lineage row lacks its provisional packet backing")
    cs_emitted = one_line(resolve_gated_block(CONTEXT_STACK))
    if (
        "as a Human-look review packet also `packet` (stable id), `question`"
        not in cs_emitted
    ):
        v.append("context-stack journal table does not join the packet schema")
    skill = read(SKILL)
    tier2 = skill.split("**Tier 2 — read for composition", 1)[-1].split("**After classification", 1)[0]
    if "primitives/human-look-gate.md" not in tier2:
        v.append("SKILL.md Tier-2 composition reads omit human-look-gate.md")
    # Exactly ONE live-condition paragraph with exactly ONE live predicate, and
    # that predicate is tier-0 — so retaining the tier-0 sentence while adding a
    # second "…effectively tier-1…" live declaration fails (presence-pinning the
    # tier-0 sentence alone would stay green).
    gate_src = resolve_gated_block(HUMAN_LOOK_GATE)
    if gate_src.count("**Live condition.**") != 1:
        v.append(f"human-look gate: {gate_src.count('**Live condition.**')} Live-condition paragraphs (want 1)")
    # Capture the WHOLE tier expression up to the clause terminator, not one
    # digit — so "…effectively tier-0 and tier-1:" reads as `tier-0 and tier-1`
    # and fails, instead of matching only the leading `tier-0`.
    live = re.findall(
        r"live wherever consult capability is\s+\*effectively\*\s+(tier-[^:.]*)", one_line(gate_src)
    )
    if [t.strip() for t in live] != ["tier-0"]:
        v.append(f"human-look gate: live predicate(s) {[t.strip() for t in live]} (want exactly one, `tier-0`)")
    return v


CANONICAL_WATCH_PROJECTION = (
    "[.iter,.t,.ac//.id//.packet,(.verdict//.to//.question//.changed)"
    '|if (type=="object" or type=="array") then tojson else . end]|@tsv'
)


def stale_watch_command_violations() -> list[str]:
    """All-callsite scan: EVERY journal-watch jq one-liner in the tree (bodies,
    primitives, README, and the ADRs — the ADR:79 copy is what this catches)
    must be the object/array-safe canonical projection. A bare
    `.verdict//.to//.changed` feeds an object straight into @tsv and crashes
    the named packet consumer; a repo-wide scan stops any stale copy — new or
    surviving — from shipping."""
    v: list[str] = []
    # Discover watch commands by the jq+@tsv SIGNATURE (a `jq -r '<expr>@tsv…'`
    # in either quote style), never by a `[.iter` prefix — so a reordered
    # projection, a space after the bracket, or trailing jq residue is still
    # discovered — then require the whole quoted argument to equal the canonical
    # projection exactly. The double-quoted arm consumes backslash escapes
    # (`(?:[^"\\]|\\.)*`) so a shell-valid `jq -r "…\"object\"…@tsv"` is parsed,
    # not truncated at its first internal quote; such a command carries `\"`
    # escapes the single-quoted canonical lacks, so it is (correctly) flagged
    # non-canonical — the repo's watch command is single-quoted throughout.
    watch_expr = re.compile(
        r"""jq -r (?:'([^']*@tsv[^']*)'|"((?:[^"\\]|\\.)*@tsv(?:[^"\\]|\\.)*)")"""
    )
    # Scan git-tracked markdown only — precisely the callsites that ship.
    # gitignored scratch (`.research/`, `dev/`, the scratchpad) is not a
    # callsite and must not gate the check.
    try:
        tracked = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", "-z", "*.md"],
            capture_output=True, text=True, check=True,
        ).stdout.split("\0")
        paths = [ROOT / rel for rel in tracked if rel]
    except (OSError, subprocess.CalledProcessError):
        paths = [p for p in sorted(ROOT.rglob("*.md"))
                 if not any(part in {".git", ".research", "scratchpad", "dev"} for part in p.parts)]
    for path in paths:
        for m in watch_expr.finditer(read(path)):
            arg = m.group(1) if m.group(1) is not None else m.group(2)
            if arg != CANONICAL_WATCH_PROJECTION:
                v.append(f"{path.relative_to(ROOT)}: non-canonical watch command `…{arg[:60]}…`")
    return v


def watch_command_executable_violations() -> list[str]:
    """Executable jq fixture: extract the projection from a real emitted render
    and RUN it over canonical mixed records — a `checkpoint` whose `.changed`
    is an object, a record whose `.to` is an ARRAY and one whose `.changed` is
    an array (both fields the projection actually reads), plus packet and
    attempt — asserting exit 0 and the COMPLETE output. Proves the emitted
    command works on every structured type it can encounter, not merely that a
    string matches. Called only when jq is installed (else a visible SKIP)."""
    render = render_body("goal", consult_tier=0)
    m = re.search(r"jq -r '(\[\.iter[^']*)'", render)
    if not m:
        return ["goal render carries no extractable watch projection"]
    projection = m.group(1)
    records = "\n".join((
        '{"iter":5,"t":"checkpoint","changed":{"phase":"verify"}}',
        '{"iter":6,"t":"attempt","ac":"AC-1","verdict":"PASS"}',
        '{"iter":7,"t":"alignment_review","packet":"hlp-7-1","question":"ok?"}',
        '{"iter":9,"t":"pressure","id":"p1","to":["x","y"]}',
        '{"iter":10,"t":"checkpoint","changed":["k"]}',
    ))
    proc = subprocess.run(
        ["jq", "-r", projection], input=records, capture_output=True, text=True
    )
    if proc.returncode != 0:
        return [f"emitted watch command errored on canonical records: {proc.stderr.strip()}"]
    expected = [
        '5\tcheckpoint\t\t{"phase":"verify"}',
        "6\tattempt\tAC-1\tPASS",
        "7\talignment_review\thlp-7-1\tok?",
        '9\tpressure\tp1\t["x","y"]',
        '10\tcheckpoint\t\t["k"]',
    ]
    rows = proc.stdout.splitlines()
    if rows != expected:
        return [f"emitted watch command produced unexpected complete output: {rows}"]
    return []


def render_input_violations() -> list[str]:
    """U1 closeout: render_body rejects inputs outside the closed vocabulary
    instead of silently misfiltering them — out-of-range ints, bool/float
    stand-ins for the tier (True == 1, 1.0 == 1), and truthy non-bool
    pollable_channel values ("false" is truthy)."""
    v: list[str] = []
    for tier in (-1, 4, 99, True, 1.0):
        try:
            render_body("story", consult_tier=tier)
            v.append(f"render_body accepted invalid consult_tier={tier!r}")
        except ContractError:
            pass
    for pollable in ("false", 1, None):
        try:
            render_body("story", consult_tier=1, pollable_channel=pollable)
            v.append(f"render_body accepted invalid pollable_channel={pollable!r}")
        except ContractError:
            pass
    return v


def run_checks() -> int:
    try:
        pure = render_frontier(benchmark_overlay=False)
        benchmark = render_frontier(benchmark_overlay=True)
    except (ContractError, AssertionError) as exc:
        print(f"[FAIL] render_resolves_cleanly: {exc}")
        return 1

    skill = read(SKILL)
    composed = read(COMPOSED_PROMPT)
    benchmark_primitive = read(BENCHMARK_FRONTIER)
    pressure_primitive = read(PRESSURE_ACCOUNTING)
    benchmark_artifacts = read(BENCHMARK_ARTIFACTS)
    benchmark_flat = one_line(benchmark)
    primitive_flat = one_line(benchmark_primitive)
    stale_completion_token = "frontier" + "_complete"

    checks: list[tuple[bool, str]] = []

    checks.append(require(True, "render_resolves_cleanly"))

    checks.append(
        require(
            not missing_tokens(pure, PRESSURE_REQUIRED),
            "pure_frontier_has_pressure_accounting",
            ", ".join(missing_tokens(pure, PRESSURE_REQUIRED)),
        )
    )
    checks.append(
        require(
            not leaked_patterns(pure, PURE_FRONTIER_BANNED_PATTERNS),
            "pure_frontier_excludes_benchmark_roles",
            ", ".join(leaked_patterns(pure, PURE_FRONTIER_BANNED_PATTERNS)),
        )
    )
    checks.append(
        require(
            not missing_patterns(benchmark, BENCHMARK_REQUIRED_PATTERNS),
            "benchmark_frontier_includes_candidate_frontier_trace_eval_roles",
            ", ".join(missing_patterns(benchmark, BENCHMARK_REQUIRED_PATTERNS)),
        )
    )
    checks.append(
        require(
            not leaked_patterns(pure, BENCHMARK_REQUIRED_PATTERNS),
            "pure_frontier_excludes_overlay_specific_required_tokens",
            ", ".join(leaked_patterns(pure, BENCHMARK_REQUIRED_PATTERNS)),
        )
    )
    checks.append(
        require(
            "do **not** participate in classification distance" in skill
            and "benchmark-frontier" in skill,
            "benchmark_overlay_documented_outside_weighted_hamming",
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
            and "one evidence-anchored pressure-discovery expansion" in benchmark_flat
            and "expansion is a probe, not a mandate" in benchmark_flat,
            "weave_green_traces_shape_rejected",
        )
    )
    checkpoint_reason_missing = sorted(
        {
            token
            for text in (pure, pressure_primitive, benchmark_artifacts)
            for token in missing_tokens(text, CHECKPOINT_REASON_VALUES)
        }
    )
    checks.append(
        require(
            not checkpoint_reason_missing,
            "checkpoint_reason_enum_consistent",
            ", ".join(checkpoint_reason_missing),
        )
    )

    checkpoint_closedset = checkpoint_reason_closedset_violations()
    checks.append(
        require(
            not checkpoint_closedset,
            "checkpoint_reason_closed_set",
            "; ".join(checkpoint_closedset),
        )
    )

    include_targets = include_target_violations()
    checks.append(
        require(
            not include_targets,
            "include_targets_resolvable",
            "; ".join(include_targets),
        )
    )

    pressure_leaks: list[str] = []
    if PRESSURE_ACCOUNTING_INCLUDE not in read(FRONTIER_BODY):
        pressure_leaks.append("frontier body missing pressure-accounting include")
    for body in NON_FRONTIER_BODIES:
        if not body.exists():
            pressure_leaks.append(f"{body.name}: missing body template")
            continue
        body_text = read(body)
        if PRESSURE_ACCOUNTING_INCLUDE in body_text:
            pressure_leaks.append(f"{body.name}: pressure-accounting include marker")
        present = [token for token in PRESSURE_REQUIRED if token in body_text]
        if present:
            pressure_leaks.append(f"{body.name}: {', '.join(present)}")
    checks.append(
        require(
            not pressure_leaks,
            "pressure_accounting_only_in_pure_frontier",
            ", ".join(pressure_leaks),
        )
    )

    fixture_failures = [
        label
        for label, row, expect_valid in CANDIDATE_ROW_FIXTURES
        if (not candidate_row_violations(row)) != expect_valid
    ]
    checks.append(
        require(
            not fixture_failures,
            "candidate_row_contract_fixtures",
            ", ".join(fixture_failures),
        )
    )

    bijection = oracle_integrity_bijection_violations()
    checks.append(
        require(
            not bijection,
            "oracle_integrity_row_property_trace_bijection",
            "; ".join(bijection),
        )
    )

    seed_gate = seed_double_gate_violations()
    checks.append(
        require(
            not seed_gate,
            "oracle_integrity_seed_double_gated",
            "; ".join(seed_gate),
        )
    )

    authority = oracle_integrity_authority_violations()
    checks.append(
        require(
            not authority,
            "oracle_integrity_source_and_status_well_defined",
            "; ".join(authority),
        )
    )

    shared_causes = halt_shared_cause_violations()
    checks.append(
        require(
            not shared_causes,
            "halt_shared_causes_consistent",
            "; ".join(shared_causes),
        )
    )

    checks.append(
        require(
            "Never emit language that pretends anti-collapse" in pure,
            "frontier_degraded_coverage_present",
        )
    )

    cross_pins = cross_file_pin_violations()
    checks.append(
        require(
            not cross_pins,
            "cross_file_restatements_pinned",
            "; ".join(cross_pins),
        )
    )

    for archetype in ("frontier", "goal", "story", "greenfield"):
        try:
            render_body(archetype)
            checks.append(require(True, f"render_body_dead_sections_{archetype}"))
        except (ContractError, AssertionError) as exc:
            checks.append(require(False, f"render_body_dead_sections_{archetype}", str(exc)))

    try:
        render_body("story", consult_tier=1)
        checks.append(require(True, "render_body_subagent_patterns_tier1"))
    except (ContractError, AssertionError) as exc:
        checks.append(require(False, "render_body_subagent_patterns_tier1", str(exc)))

    # ── U1-c2: exact D/B/C tier filter + advisory-authority pins ────────────
    try:
        filter_violations = subagent_pattern_filter_violations()
    except (ContractError, AssertionError) as exc:
        filter_violations = [str(exc)]
    checks.append(
        require(
            not filter_violations,
            "subagent_patterns_exact_tier_filter",
            "; ".join(filter_violations),
        )
    )

    read_set_missing = derivation_read_set_violations()
    checks.append(
        require(
            not read_set_missing,
            "derivation_read_set_paths_exist",
            ", ".join(read_set_missing),
        )
    )

    # ── U1-c4: derivation provenance owned by DERIVATION.md, never STATE.md ─
    ownership = derivation_ownership_violations()
    checks.append(
        require(
            not ownership,
            "derivation_ownership_pinned",
            "; ".join(ownership),
        )
    )

    # ── U1 closeout (P1): persistence scoped to successful composition ──────
    scope = derivation_scope_violations()
    checks.append(
        require(
            not scope,
            "derivation_record_scoped_to_successful_composition",
            "; ".join(scope),
        )
    )

    # ── U1 closeout: renderer rejects out-of-vocabulary consult tiers ───────
    bad_inputs = render_input_violations()
    checks.append(
        require(
            not bad_inputs,
            "render_rejects_invalid_consult_tier",
            "; ".join(bad_inputs),
        )
    )

    # ── The consult fallback is always carried, provisional, and joined ─────
    try:
        human_look = human_look_gate_violations()
    except (ContractError, AssertionError) as exc:
        human_look = [str(exc)]
    checks.append(
        require(
            not human_look,
            "human_look_gate_always_carried_and_provisional",
            "; ".join(human_look),
        )
    )

    # ── The human-watch command is object/array-safe everywhere + executable ─
    stale_watch = stale_watch_command_violations()
    checks.append(
        require(
            not stale_watch,
            "watch_command_object_safe_all_callsites",
            "; ".join(stale_watch),
        )
    )
    if shutil.which("jq") is None:
        # Visible SKIP, never a silent green — the string scan still guards the
        # command shape; only the runtime execution is unavailable here.
        checks.append(require(True, "watch_command_executable_jq_fixture [SKIPPED: jq not installed]"))
    else:
        try:
            watch_exec = watch_command_executable_violations()
        except (ContractError, AssertionError) as exc:
            watch_exec = [str(exc)]
        checks.append(
            require(
                not watch_exec,
                "watch_command_executable_jq_fixture",
                "; ".join(watch_exec),
            )
        )

    # ── U2: context-mode split under the strict resolution-basis rule ───────
    context_mode = context_mode_violations()
    checks.append(
        require(
            not context_mode,
            "context_mode_split_strict_resolution_basis",
            "; ".join(context_mode),
        )
    )

    # ── U1-c5: evidence-tier goal exclusion is named and practiced ──────────
    evidence_tier_goal = evidence_tier_goal_violations()
    checks.append(
        require(
            not evidence_tier_goal,
            "evidence_tier_goal_exclusion_consistent",
            "; ".join(evidence_tier_goal),
        )
    )

    state_key_missing = state_key_body_violations()
    checks.append(
        require(
            not state_key_missing,
            "state_keys_mentioned_in_body",
            "; ".join(f"{archetype}: {', '.join(keys)}" for archetype, keys in state_key_missing.items()),
        )
    )

    classify_mirror = classify_mirror_violations()
    checks.append(
        require(
            not classify_mirror,
            "classify_py_mirrors_skill_axis_matrix",
            "; ".join(classify_mirror),
        )
    )

    # ── U11: context-stack memory-model contracts ──────────────────────────
    body_includes = body_include_violations()
    checks.append(
        require(
            not body_includes,
            "bodies_include_context_stack_and_queue",
            "; ".join(body_includes),
        )
    )

    tiered = tiered_read_violations()
    checks.append(
        require(
            not tiered,
            "bodies_use_tiered_reads",
            "; ".join(tiered),
        )
    )

    key_mirror = state_key_mirror_violations()
    checks.append(
        require(
            not key_mirror,
            "state_key_skill_context_stack_mirror",
            "; ".join(key_mirror),
        )
    )

    journal_enum = journal_enum_violations()
    checks.append(
        require(
            not journal_enum,
            "journal_record_types_consistent",
            "; ".join(journal_enum),
        )
    )

    # ── U1-c1: Operational core body-carried + first-80 in every render ─────
    core_body = operational_core_violations()
    checks.append(
        require(
            not core_body,
            "operational_core_body_carried_parity",
            "; ".join(core_body),
        )
    )
    core_render = operational_core_render_violations()
    checks.append(
        require(
            not core_render,
            "operational_core_first_80_all_renders",
            "; ".join(core_render),
        )
    )
    try:
        core_canonical = operational_core_canonical_violations()
    except (ContractError, AssertionError) as exc:
        core_canonical = [str(exc)]
    checks.append(
        require(
            not core_canonical,
            "operational_core_first_80_under_canonical_provenance",
            "; ".join(core_canonical),
        )
    )

    # ── U1-c3: run-host channel check emitted + consult_tier_effective ──────
    try:
        run_host = run_host_verification_violations()
    except (ContractError, AssertionError) as exc:
        run_host = [str(exc)]
    checks.append(
        require(
            not run_host,
            "run_host_verification_emitted_and_gated",
            "; ".join(run_host),
        )
    )

    # Always-on pressure surface + context budget must actually reach the emitted
    # prompt now (fixtures render PRESSURE_SURFACE always-on, ADR 0004).
    checks.append(
        require(
            "Mandatory promotion" in pure and "Context budget" in pure,
            "frontier_pressure_and_budget_emitted",
        )
    )
    goal_render = render_body("goal")
    checks.append(
        require(
            "final-verify not yet run" in goal_render,
            "goal_verify_header_only_guard",
        )
    )
    checks.append(
        require(
            "Mandatory promotion" in goal_render and "Context budget" in goal_render,
            "goal_pressure_and_budget_emitted",
        )
    )

    # ── U13: pre-ship hardening (ADR 0004 amendment) ────────────────────────
    scope_preflight = scope_terminal_preflight_violations()
    checks.append(
        require(
            not scope_preflight,
            "required_writes_scoped_and_terminal_preflight_gates_final_verify",
            "; ".join(scope_preflight),
        )
    )
    terminal_path_scan = terminal_path_scan_executable_violations()
    checks.append(
        require(
            not terminal_path_scan,
            "terminal_preflight_git_scan_executable_fixture",
            "; ".join(terminal_path_scan),
        )
    )

    hardening = u13_hardening_violations()
    checks.append(
        require(
            not hardening,
            "u13_hardening_contracts",
            "; ".join(hardening),
        )
    )
    checks.append(
        require(
            "Context-health check" in pure and "Context-health check" in goal_render,
            "context_health_emitted",
        )
    )

    # ── U14: consolidation round = contract-layer checkpoint (ADR 0005) ─────
    consolidation = u14_consolidation_violations()
    checks.append(
        require(
            not consolidation,
            "u14_consolidation_contracts",
            "; ".join(consolidation),
        )
    )
    checks.append(
        require(
            all(
                "Consolidation round" in render and "suspected_substrate" in render
                for render in (pure, goal_render)
            ),
            "consolidation_emitted",
        )
    )

    # ── U15: frontier-vector adequacy — earned-dimension lifecycle ──
    vector_adequacy = u15_vector_adequacy_violations()
    checks.append(
        require(
            not vector_adequacy,
            "u15_vector_adequacy_contracts",
            "; ".join(vector_adequacy),
        )
    )
    checks.append(
        require(
            "## Frontier-vector adequacy" in pure
            and "## Frontier-vector adequacy" in benchmark
            and "{{INCLUDE primitives/frontier-vector-adequacy.md}}"
            in read(FRONTIER_BODY),
            "vector_adequacy_wired_into_frontier",
            "fva-U3 wires the lifecycle into the body; the emitted block must "
            "appear in both frontier renders",
        )
    )
    for other_body in NON_FRONTIER_BODIES:
        checks.append(
            require(
                "frontier-vector-adequacy" not in read(other_body),
                f"vector_adequacy_frontier_only_{other_body.stem}",
            )
        )

    # ── U17: every vector-mutation path routes through the lifecycle (fva-U3) ──
    admission_wiring = u17_admission_wiring_violations()
    checks.append(
        require(
            not admission_wiring,
            "u17_admission_wiring_contracts",
            "; ".join(admission_wiring),
        )
    )

    # ── fva-U4 parity: single-source evidence bar + exact golden set ──
    evidence_bar = "two independent residuals"
    checks.append(
        require(
            evidence_bar in one_line(read(FRONTIER_VECTOR_ADEQUACY))
            and evidence_bar not in one_line(read(FRONTIER_BODY))
            and evidence_bar
            not in one_line(
                read(ROOT / "loopgen/templates/bodies/frontier-reopen-policy.md")
            ),
            "candidate_evidence_bar_single_source",
            "the candidate evidence threshold lives only in the primitive; "
            "variants and body defer to it rather than restating it",
        )
    )
    checks.append(
        require(
            {p.name for p in GOLDEN_DIR.glob("*.md")}
            == {FRONTIER_EQUILIBRIUM_GOLDEN.name, FRONTIER_BENCHMARK_GOLDEN.name},
            "golden_dir_exactly_two_pinned_renders",
            f"unexpected golden set: {sorted(p.name for p in GOLDEN_DIR.glob('*.md'))}",
        )
    )

    # ── U16: workset identity + seed-vs-live vector authority (fva-U2) ──
    workset_identity = u16_workset_identity_violations()
    checks.append(
        require(
            not workset_identity,
            "u16_workset_identity_contracts",
            "; ".join(workset_identity),
        )
    )
    checks.append(
        require(
            "(bootstrap seed)" in one_line(pure)
            and "STATE is the sole authority for the live vector" in one_line(pure)
            and "(bootstrap seed)" in one_line(benchmark),
            "seed_vs_live_authority_emitted",
        )
    )

    # ── reopen-policy block + guarded halt-shape resolution (U4b) ──
    playbook_equilibrium = render_frontier_playbook()
    golden_exists = FRONTIER_EQUILIBRIUM_GOLDEN.exists()
    checks.append(
        require(
            golden_exists,
            "frontier_playbook_golden_present",
            "missing tools/golden/frontier-body.equilibrium.md — run --capture-golden",
        )
    )
    if golden_exists:
        golden = FRONTIER_EQUILIBRIUM_GOLDEN.read_text(encoding="utf-8")
        checks.append(
            require(
                playbook_equilibrium == golden,
                "body_equilibrium_byte_identical",
                "playbook drifted from the frozen golden; if the edit was "
                "intentional, re-run --capture-golden and commit the golden "
                "with the edit that moved it",
            )
        )
    benchmark_golden_exists = FRONTIER_BENCHMARK_GOLDEN.exists()
    checks.append(
        require(
            benchmark_golden_exists,
            "frontier_benchmark_golden_present",
            "missing tools/golden/frontier-body.benchmark.equilibrium.md — "
            "run --capture-golden",
        )
    )
    if benchmark_golden_exists:
        benchmark_golden = FRONTIER_BENCHMARK_GOLDEN.read_text(encoding="utf-8")
        checks.append(
            require(
                render_frontier_benchmark_playbook() == benchmark_golden,
                "body_benchmark_byte_identical",
                "benchmark playbook drifted from its frozen golden; if the "
                "edit was intentional, re-run --capture-golden and commit "
                "both goldens with the edit that moved them",
            )
        )

    try:
        playbook_terminal = render_frontier(
            benchmark_overlay=False,
            reopen_policy="terminal",
            placeholder_overrides=PLAYBOOK_SENTINELS,
        )
        terminal_render_error = ""
    except (ContractError, AssertionError, KeyError) as exc:
        playbook_terminal = ""
        terminal_render_error = str(exc)
    checks.append(
        require(
            not terminal_render_error,
            "reopen_policy_terminal_renders",
            terminal_render_error,
        )
    )
    terminal_flat = one_line(playbook_terminal)
    equilibrium_flat = one_line(playbook_equilibrium)
    required_terminal_tokens = (
        "iteration halted; frontier episode terminated (declared workset exhausted)",
        "terminal reopen policy",
        "does not auto-resume",
        "an explicit per-row `reopen_condition`, a regression, or a new "
        "declared-workset version",
        "frontier episode paused",
    )
    banned_terminal_tokens = (
        "iteration halted; frontier checkpointed",
        "reopens automatically on strong new signal",
        # Policy-assuming common prose repaired in the review round: a terminal
        # render carrying any of these contradicts its own policy block.
        "A frontier halt is a checkpoint",
        "legitimate checkpoint",
        "the loop is at frontier equilibrium",
        "homeostatic-checkpoint` equilibrium",
        # The variant text serves BOTH the guarded resolution and an explicitly
        # requested terminal (which may hold a live contract): it must never
        # assert frontload field values.
        "reopen_contract: none",
        # fva-U3: admission authority is equilibrium-only; a terminal render
        # carrying it contradicts its own non-mutation policy.
        "admitted in-episode",
    )
    checks.append(
        require(
            not missing_tokens(terminal_flat, required_terminal_tokens),
            "body_terminal_semantics",
            ", ".join(missing_tokens(terminal_flat, required_terminal_tokens)),
        )
    )
    checks.append(
        require(
            bool(terminal_flat)
            and all(token not in terminal_flat for token in banned_terminal_tokens),
            "body_terminal_no_equilibrium_residue",
            "; ".join(t for t in banned_terminal_tokens if t in terminal_flat),
        )
    )
    checks.append(
        require(
            "has no quality pass-line" in terminal_flat
            and "has no quality pass-line" in equilibrium_flat,
            "objective_no_pass_line_claim_in_both_variants",
        )
    )

    reopen_policy_leaks = [
        path.name
        for path in NON_FRONTIER_BODIES
        if "FRONTIER_REOPEN_POLICY" in read(path)
        or "frontier episode terminated" in one_line(read(path))
    ]
    checks.append(
        require(
            not reopen_policy_leaks,
            "reopen_policy_frontier_only",
            ", ".join(reopen_policy_leaks),
        )
    )

    full_closure = dict(
        work_source_domain="enumerated: no inbound CI/review/schedule/dep-alert",
        declared_surfaces="duplication scan + findings ledger + oracle gaps",
        exhaustion_criterion=(
            "full frontier scan (homeostasis + pressure discovery + vector adequacy) "
            "quiescent under declared surfaces"
        ),
        initial_frontier_vector=FRONTIER_VECTOR_FIXTURE,
    )
    legacy_closure = dict(
        work_source_domain="enumerated: no inbound CI/review/schedule/dep-alert",
        declared_surfaces="duplication scan + findings ledger + oracle gaps",
        exhaustion_criterion=(
            "full frontier scan (homeostasis + pressure discovery + vector adequacy) "
            "quiescent under declared surfaces"
        ),
    )
    guard_cases: list[tuple[str, dict, object]] = [
        (
            "named signal + channel → equilibrium, no divergence",
            dict(
                requested="equilibrium",
                reopening_signal="new reviewed findings",
                reopen_contract="inbox note delivered via scheduled re-run",
                closure_basis=None,
            ),
            ("equilibrium", False),
        ),
        (
            "none + enumerated domain + closure basis → guarded terminal",
            dict(
                requested="equilibrium",
                reopening_signal="none",
                reopen_contract="none",
                closure_basis=full_closure,
            ),
            ("terminal", True),
        ),
        (
            "none without closure basis → gap",
            dict(
                requested="equilibrium",
                reopening_signal="none",
                reopen_contract="none",
                closure_basis=None,
            ),
            DerivationGap,
        ),
        (
            "named signal without delivery channel → gap",
            dict(
                requested="equilibrium",
                reopening_signal="upstream release",
                reopen_contract="none",
                closure_basis=None,
            ),
            DerivationGap,
        ),
        (
            "delivery channel without named signal → gap",
            dict(
                requested="equilibrium",
                reopening_signal="none",
                reopen_contract="ci webhook",
                closure_basis=None,
            ),
            DerivationGap,
        ),
        (
            "fields absent → legacy equilibrium, no divergence",
            dict(
                requested="equilibrium",
                reopening_signal=None,
                reopen_contract=None,
                closure_basis=None,
            ),
            ("equilibrium", False),
        ),
        (
            "unresolved → non-emittable",
            dict(
                requested="equilibrium",
                reopening_signal="unresolved",
                reopen_contract="unresolved",
                closure_basis=None,
            ),
            DerivationGap,
        ),
        (
            "explicitly requested terminal → terminal, no compiler divergence",
            dict(
                requested="terminal",
                reopening_signal="none",
                reopen_contract="none",
                closure_basis=full_closure,
            ),
            ("terminal", False),
        ),
        (
            "explicit terminal + live contract → terminal, no compiler divergence",
            dict(
                requested="terminal",
                reopening_signal="upstream release",
                reopen_contract="dep-alert delivered via scheduled re-run",
                closure_basis=None,
            ),
            ("terminal", False),
        ),
        (
            "signal recorded without the contract field → gap (partial absence)",
            dict(
                requested="equilibrium",
                reopening_signal="upstream release",
                reopen_contract=None,
                closure_basis=None,
            ),
            DerivationGap,
        ),
        (
            "contract recorded without the signal field → gap (partial absence)",
            dict(
                requested="equilibrium",
                reopening_signal=None,
                reopen_contract="none",
                closure_basis=None,
            ),
            DerivationGap,
        ),
        (
            "none + incomplete closure evidence → gap (bare flag insufficient)",
            dict(
                requested="equilibrium",
                reopening_signal="none",
                reopen_contract="none",
                closure_basis=dict(
                    work_source_domain="enumerated: none inbound",
                    declared_surfaces="",
                    exhaustion_criterion="",
                ),
            ),
            DerivationGap,
        ),
        (
            "legacy three-field basis (fourth key absent) → guarded terminal preserved",
            dict(
                requested="equilibrium",
                reopening_signal="none",
                reopen_contract="none",
                closure_basis=legacy_closure,
            ),
            ("terminal", True),
        ),
        (
            "fresh basis with empty initial_frontier_vector → gap (partial, never legacy)",
            dict(
                requested="equilibrium",
                reopening_signal="none",
                reopen_contract="none",
                closure_basis=dict(legacy_closure, initial_frontier_vector=""),
            ),
            DerivationGap,
        ),
    ]
    guard_failures: list[str] = []
    for case_name, kwargs, expected in guard_cases:
        try:
            got: object = resolve_effective_halt_shape(archetype="frontier", **kwargs)
        except DerivationGap:
            got = DerivationGap
        if got != expected:
            guard_failures.append(f"{case_name} (got {got!r})")
    if resolve_effective_halt_shape(
        archetype="goal",
        requested="terminal",
        reopening_signal=None,
        reopen_contract=None,
        closure_basis=None,
    ) != ("terminal", False):
        guard_failures.append("non-frontier passthrough")
    checks.append(
        require(
            not guard_failures,
            "guarded_halt_resolution_paths",
            "; ".join(guard_failures),
        )
    )

    halt_shape_flat = one_line(read(ROOT / "loopgen/primitives/halt-shape.md"))
    guard_conjunct_tokens = (
        "requested halt-shape == equilibrium",
        "reopen_contract == none",
        "closure_basis established",
        "not** a biconditional",
        "effective halt-shape := terminal",
        "{requested, effective, resolution_basis}",
    )
    checks.append(
        require(
            not missing_tokens(halt_shape_flat, guard_conjunct_tokens),
            "guard_prose_conjuncts",
            ", ".join(missing_tokens(halt_shape_flat, guard_conjunct_tokens)),
        )
    )
    context_stack_flat = one_line(read(CONTEXT_STACK))
    checks.append(
        require(
            "{requested, effective, resolution_basis}" in context_stack_flat,
            "divergence_triple_durable_in_derivation",
            "DERIVATION.md divergences must define the "
            "{requested, effective, resolution_basis} triple for "
            "compiler-derived halt-shape resolution",
        )
    )
    frontload_flat = one_line(read(FRONTLOAD_AUDIT))
    checks.append(
        require(
            not missing_tokens(frontload_flat, CLOSURE_BASIS_KEYS),
            "closure_basis_keys_named_in_frontload",
            "frontload-audit.md must name the closure-contract fields the "
            "executable guard requires: "
            + ", ".join(missing_tokens(frontload_flat, CLOSURE_BASIS_KEYS)),
        )
    )

    trust_marker = "## External trust boundary"
    trust_pins = (
        "Availability is not authorization.",
        "Before every commit, inspect the staged diff for secrets and restricted connector-derived content.",
        "Installing or executing a new dependency, package, plugin, extension, MCP server, downloaded binary, or remote installer is authority-needing",
    )
    trust_source_flat = one_line(read(EXTERNAL_TRUST_BOUNDARY))
    checks.append(
        require(
            trust_marker in read(EXTERNAL_TRUST_BOUNDARY)
            and all(pin in trust_source_flat for pin in trust_pins),
            "external_trust_boundary_source_contract",
            "source primitive is missing its heading or a required security guard",
        )
    )
    for archetype in BODY_PATHS:
        rendered = render_body(archetype)
        rendered_flat = one_line(rendered)
        checks.append(
            require(
                rendered.count(trust_marker) == 1,
                f"{archetype}_external_trust_boundary_once",
                f"expected one {trust_marker!r}, found {rendered.count(trust_marker)}",
            )
        )
        checks.append(
            require(
                all(pin in rendered_flat for pin in trust_pins),
                f"{archetype}_external_trust_boundary_pins",
                "rendered prompt is missing disclosure, staged-diff, or supply-chain guard",
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
    print(
        "frontier_terminal_policy_delta="
        f"{len(playbook_terminal.splitlines()) - len(playbook_equilibrium.splitlines())}"
    )
    return 0 if ok else 1


USAGE = (
    "usage: verify_loopgen_contracts.py "
    "[--print pure-frontier|benchmark-frontier|frontier-playbook] "
    "[--capture-golden]"
)


def main(argv: list[str]) -> int:
    if len(argv) == 3 and argv[1] == "--print":
        if argv[2] == "pure-frontier":
            print(render_frontier(benchmark_overlay=False))
            return 0
        if argv[2] == "benchmark-frontier":
            print(render_frontier(benchmark_overlay=True))
            return 0
        if argv[2] == "frontier-playbook":
            print(render_frontier_playbook())
            return 0
        print(USAGE, file=sys.stderr)
        return 2
    if len(argv) == 2 and argv[1] == "--capture-golden":
        GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
        FRONTIER_EQUILIBRIUM_GOLDEN.write_text(
            render_frontier_playbook(), encoding="utf-8"
        )
        print(f"captured {FRONTIER_EQUILIBRIUM_GOLDEN.relative_to(ROOT)}")
        FRONTIER_BENCHMARK_GOLDEN.write_text(
            render_frontier_benchmark_playbook(), encoding="utf-8"
        )
        print(f"captured {FRONTIER_BENCHMARK_GOLDEN.relative_to(ROOT)}")
        return 0
    if len(argv) != 1:
        print(USAGE, file=sys.stderr)
        return 2
    return run_checks()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
