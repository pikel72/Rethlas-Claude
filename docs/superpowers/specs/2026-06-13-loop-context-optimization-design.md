# Loop Context Optimization — Design

Date: 2026-06-13
Status: Draft, awaiting user review
Scope: Rethlas Claude Code plugin (solver + verifier MCP, agents, skills)

## 1. Goal

Optimize the **token stream the model actually sees** during the solver↔verifier loop, so that:

- Token usage per iteration drops.
- Loop iterations **compound**: each pass leaves behind memory the next pass can directly use, instead of re-deriving the same context.
- The model's autonomy in deciding *what to do* is preserved.

The optimization target is **context density**, not **flow control**.

## 2. Constraint — The Model Decides

**Hard boundary, applies to every change in this spec:**

- Do not add hardcoded retry / backoff / short-circuit / path-selection logic in the solver↔verifier loop.
- Do not invent a fixed protocol for how the verifier hands feedback to the solver.
- Do not pre-decide which channels the model should write to, which records it should keep, or which skills it should invoke.
- Do not cap the model's options by removing skills or tools.

**The change is in what the model sees, not in what the model is allowed to do.**

## 3. Scope

### In scope

- Memory read-path return shape (envelope on `memory_search` and `memory_query`).
- Memory write-path return shape (envelope on `memory_append`).
- One new solver skill: `$record-keeping` (model-opt-in reference for what makes a record useful in subsequent iterations).
- Tightening of all 10 solver skills + 3 verifier skills + the `rethlas` entry skill (text rewrite only, no schema or new fields).
- Tightening of all `@app.tool` docstrings in both `solver/mcp/server.py` and `verifier/mcp/server.py`.

### Out of scope

- New write semantics (`update` / `merge` / `delete` / `bulk_write` / `transaction` / write-time dedup). The model can still "update" a record by writing a new one; that decision is the model's.
- New fields injected into records (`attempt` number, `summary`, etc.). Records are agent-owned; we do not own their shape.
- Storage format changes. The JSONL on disk stays exactly as it is. Envelope transformation happens at the MCP boundary.
- Removing any existing skill or tool.
- Shared-module extraction for the two `server.py` files (was option A in earlier discussion, deferred — not the highest-ROI change for the stated goal).
- HTTP-side changes to `search_arxiv_theorems` (was option C, deferred).
- Caching / retry / backoff (those are flow engineering, explicitly excluded by §2).

## 4. Design

### 4.1 Memory read envelope — `memory_search` and `memory_query`

**Per-item shape change only.** Top-level wrappers are preserved as they are today:

- `memory_search` returns `{problem_id, query, channels, limit_per_channel, count, results_by_channel}`.
- `memory_query` returns `{run_id, channel, count, items}`.

`memory_search` per-item:

```json
{
  "kind": "subgoal",
  "score": 1.23,
  "data": { ... original record, verbatim ... }
}
```

`memory_query` per-item:

```json
{
  "kind": "statement_check",
  "data": { ... original record, verbatim ... }
}
```

Differences from current shape:

- `item` is flattened.
- `channel` is hoisted to top level as `kind` (model scans type first, then content).
- `timestamp_utc` is removed (the model rarely uses absolute time, and `meta.json::created_at_utc` is available when it does).
- `record` is renamed to `data` (shorter, more scannable).

### 4.2 Memory write envelope — `memory_append`

Current return:

```json
{
  "status": "ok",
  "channel": "subgoals",
  "path": "/abs/path/to/.rethlas/runs/.../memory/subgoals.jsonl",
  "entry": {
    "timestamp_utc": "...",
    "channel": "subgoals",
    "record": { ... }
  }
}
```

New return:

```json
{
  "kind": "subgoal",
  "written": true,
  "channel_count": 7
}
```

Differences:

- `path` removed (model never reads file paths).
- `entry` echo removed (model just wrote it, getting it back is noise).
- `status: "ok"` replaced by `written: true` (same purpose, shorter name).
- `channel_count` added: count of records in this channel after the write. This is a *hint* the model can use to label the record for later reference (e.g., "this subgoal is `sg-7`"). Model may ignore it.

The write itself is unchanged. The change is purely the return value.

### 4.3 channel → kind mapping

| channel                  | kind                  |
| ------------------------ | --------------------- |
| immediate_conclusions    | `immediate_conclusion`|
| toy_examples             | `toy_example`         |
| counterexamples          | `counterexample`      |
| big_decisions            | `decision`            |
| subgoals                 | `subgoal`             |
| proof_steps              | `proof_step`          |
| failed_paths             | `failed_path`         |
| verification_reports     | `verification_report` |
| branch_states            | `branch_state`        |
| statement_checks         | `statement_check`     |
| reference_checks         | `reference_check`     |
| failed_checks            | `failed_check`        |
| events                   | `event`               |

The `events` channel is auto-appended by the system and rarely consumed by the model. Its return shape is left as-is for now (no envelope). If a future need appears, it can be enveloped in the same way.

### 4.4 New skill: `$record-keeping`

**Location:** `solver/skills/record-keeping/SKILL.md`
**Loaded by:** solver agent only.
**Loaded how:** description-based auto-loading. The model sees the description in the system prompt, decides whether to invoke, and pulls the body only if it does.

**Skill content (skeleton — to be written during implementation):**

- One sentence on the purpose: "Guide for writing solver memory records that maximize reuse in subsequent loop iterations."
- "When to use" trigger: "Before calling `memory_append`, especially on the first attempt, or whenever the previous attempt's records were not useful."
- Per-channel minimal field suggestions (one line each, not exhaustive):
  - `subgoal`: `id`, `claim`, `dependencies`, optional `status`
  - `failed_path`: `what_tried`, `why_failed`
  - `counterexample`: `statement`, `witness`
  - `proof_step`: `step`, `justification`
  - `immediate_conclusion`: `claim`, `source`
  - Other channels: same style
- One short "good record / bad record" pair, ~3 lines each.
- An explicit note: "This skill is a reference. The model decides whether to follow it, partially follow it, or ignore it. There is no validation that records match this shape."

### 4.5 Skill rewrite rules

**Applies to:** all 10 solver skills, all 3 verifier skills, and the `rethlas` entry skill.

**Universal rules:**

1. Total skill length cap: ~150 tokens each (rough — "the model can read it without effort").
2. Required structure (markdown sections in this order):
   ```
   ## When to use
   ## Output
   ## Steps
   ```
3. **Delete:**
   - Restatements of the agent's main prompt (the agent already says it).
   - Multi-line examples; keep at most one line of example, or remove entirely.
   - Meta-prose ("This skill is used to...") — the description field already says this.
   - Cross-skill duplication: if two skills share an instruction, keep it in one and reference it from the other.
4. **Keep:**
   - The "When to use" trigger sentence — this is what makes the model invoke the skill.
   - The differentiating steps (what makes this skill *this* skill, not another).
   - Concrete names of other skills / tools being referenced.

**Known overlap to collapse during implementation:**

- `obtain-immediate-conclusions` and `direct-proving` share the "exploit known structural facts" theme — collapse the shared preamble.
- `construct-counterexamples` and `construct-toy-examples` share "find small instances" — collapse the shared preamble.
- `recursive-proving` can reference `obtain-immediate-conclusions` by name rather than re-stating the procedure.
- `verify-proof` can reference the verifier MCP tool by name rather than describing the verification protocol.

**No structural change** beyond markdown reorganization. No new fields, no new code paths, no new files (other than `record-keeping`).

### 4.6 Tool description template

**Applies to:** all `@app.tool(name=...)` decorated functions in `solver/mcp/server.py` and `verifier/mcp/server.py`.

**Template:**

```
When to call: <one sentence trigger>
Args: <param list, with types>
Returns: <return shape, one or two lines>
Notes: <warnings, edge cases, related tools>
```

Cap: ~80 tokens per tool. No verbose prose.

**Specific applications:**

- `memory_search`: emphasize "BM25-ranked, cross-channel, score-descending; the model can scan multiple channels in one call."
- `memory_append`: emphasize "channel determines `kind`; the `record` shape is whatever the caller passes — `record-keeping` skill has guidance."
- `memory_query`: distinguish from `memory_search` (precise filters / substring vs fuzzy BM25).
- All other tools: rewrite under the template.

## 5. Implementation

### 5.1 File changes

**New files:**

- `solver/skills/record-keeping/SKILL.md`

**Edited files:**

- `solver/mcp/server.py` — new return shapes for `memory_search`, `memory_append`; updated tool docstrings.
- `verifier/mcp/server.py` — new return shapes for `memory_query`; updated tool docstrings.
- `solver/mcp/envelope.py` — **new** module: shared `transform_item(item, channel)` and `transform_append_result(channel, count)` helpers. The two server.py files import from it. (This is the only "shared module" extraction in this spec; it is justified because it removes copy-paste *of the envelope logic itself*, not of arbitrary code.)
- All 10 solver skills under `solver/skills/*/SKILL.md` — text rewrite.
- All 3 verifier skills under `verifier/skills/*/SKILL.md` — text rewrite.
- `skills/rethlas/SKILL.md` — text rewrite.
- `agents/solver.md` — add `$record-keeping` to the `skills:` frontmatter list.
- `agents/verifier.md` — no change (verifier does not get `record-keeping`).

### 5.2 Import path for the shared envelope module

`verifier/mcp/server.py` needs to import `envelope` from `solver/mcp/`. The two `.mcp.json` entries launch each server as `python <path>/server.py` with `cwd` set to the plugin root. In this launch mode, Python puts the *script's directory* at `sys.path[0]` — so `solver/mcp/` is on `sys.path` but its parent (the plugin root, which would let us write `from solver.mcp.envelope import ...`) is **not** by default.

Two options:

- **Add the plugin root to `sys.path` explicitly** at the top of both `server.py` files: `sys.path.insert(0, str(PLUGIN_SOLVER_ROOT.parent))` (or equivalent for the verifier). Then `from solver.mcp.envelope import transform_item, transform_append_result` resolves. This is the preferred option — single source of truth.
- **Duplicate the envelope module** under `verifier/mcp/envelope.py`. ~30 lines of duplication, no cross-package coupling, but the two copies will drift over time.

**Decision: option 1 (explicit sys.path insertion) is the default. Fall back to option 2 only if the import path is fragile in a way that shows up during smoke testing.**

### 5.3 Backward compatibility

The envelope change is technically a breaking change to the MCP return shape. However, all consumers of these tools are model agents within the same plugin, and they will see the new shape on their next call. No versioned migration is needed; no external consumers exist.

The internal `entry` object still has `timestamp_utc` on disk (JSONL is unchanged). The envelope transformation strips it at the MCP boundary only.

## 6. Verification

The change is in *what the model sees*. Verification therefore measures the model's input stream, not the system's output.

### 6.1 Static checks (must pass)

- All 14 skills (10 solver + 3 verifier + the `rethlas` entry skill) have the three required sections.
- All 10 `@app.tool` docstrings match the template.
- `memory_search` and `memory_query` return items with the new shape (kind, score/data, no timestamp_utc, no `item` wrapper).
- `memory_append` returns the new shape (kind, written, channel_count).
- `events` channel is excluded from envelope.

### 6.2 Behavioral checks (run before declaring done)

- **Token count check**: pick one of the example problems (`solver/data/example/example1.md`), run the solver once. Capture the model input lengths (from logs or by re-running with the same context) before and after the change. Expect a measurable drop — target ≥25% reduction on skill + tool-description system prompt text, and ≥20% on memory search results.
- **End-to-end smoke**: run `/rethlas-solve` on `example1.md` (no refs). Confirm `blueprint_verified.md` is produced. If it is not, the rewrite has regressed something — revert and investigate.
- **Manual context read-back**: open the model input (via a debug print or the log if available) and confirm the new shape is what the model sees. No `timestamp_utc` in items, no `entry` echo in write returns, no long-form prose in skills.

### 6.3 Quality check (qualitative)

- Compare two runs of the same example problem, before and after the change.
- Count the number of attempts to reach `verdict: "correct"`. Expectation: ≤ the pre-change count, on average. A regression here means the rewrite is hiding useful information from the model.
- Spot-check 2–3 model responses after the change. Confirm the model is using the new envelope (referring to `kind`, `data`, etc., not the old `channel` / `record` / `entry`).

### 6.4 What we explicitly do not measure

- **Improvement in success rate.** Too noisy for a single change set; this is a long-term property.
- **Reduction in wall-clock time.** Token reduction is a proxy, but the dominant wall-clock is still LLM API latency. Out of scope for this spec.

## 7. Risks and mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| A skill rewrite cuts information the model actually needs. | Medium | Medium (loop quality drop on hard problems) | Smoke test on `example1.md` (§6.2) catches it; revert specific skill if so. |
| `record-keeping` skill is ignored by the model, so loop quality doesn't improve. | Medium | Low (no regression, just no benefit) | Acceptable per §2 — we don't force it. Loop quality still benefits from the read-side envelope (cleaner results). |
| Cross-package import of `envelope` module fails at MCP startup. | Low | High (verifier MCP won't launch) | Fallback to duplicate envelope module (§5.2). |
| Model still references old field names in tool calls (e.g., writes a record with an explicit `timestamp_utc` inside `record`). | Low | None | The shape change is only on the *return* side. Inputs are unchanged. |
| A future contributor adds a new skill / channel and forgets the rewrite rules. | Low | Low | Add a short note in `agents/solver.md` and `docs/port.md` (or a new `docs/context.md`) describing the convention. |

## 8. Open questions

None at design time. The only judgement call left is in implementation: the exact wording of each rewritten skill and the example "good vs bad record" pair in `$record-keeping`. Those are content decisions, not design decisions, and will be drafted then read back for user review before finalizing.
