---
name: synthesize-verification-report
description: Aggregate all detected errors and gaps into the final verification report, apply strict accept/reject logic, and produce repair hints when rejected.
---

# Synthesize Verification Report

## When to use

When all statement_checks and reference_checks have completed.

## Output

`verification_report` with `summary`, `critical_errors`, `gaps`.

## Steps

1. Collect all critical errors and gaps from statement_checks and reference_checks.
2. Build verification_report with summary, critical_errors, gaps.
3. Set verdict: `correct` iff both critical_errors and gaps are empty; otherwise `wrong`.
4. If wrong, produce non-empty repair_hints.
5. Validate output via `validate_verification_output` MCP tool.
6. Persist via `write_verification_output` MCP tool.
