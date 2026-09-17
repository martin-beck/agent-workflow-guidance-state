# Cross-project oracle workflow integration plan

This plan turns a software-engineering project request into a coordinated
Coordinator/AWG/AWQ lifecycle. It is planning evidence only; implementation
begins through the ARs below and remains subject to each repository's normal
review and quality gates.

## Ownership and sequence

| Phase | AWG decision semantics | Coordinator state authority | AWQ quality authority |
| --- | --- | --- | --- |
| Intake | AR-0035/0036 define the mandatory gate and review packet | AR-0022 records the gate and blocks continuation | AR-0058 checks its typed evidence |
| Discussion | AR-0037 presents alternatives, confidence, implications, specs, and added solutions | AR-0022/0024 bind packet and user disposition to task revision | AR-0058 checks context, privacy, and formal evidence |
| Reconciliation | AR-0038 updates plan/design/specs/ARs and reopens ambiguity | AR-0023/0024 preserve before/after versions and pause work | AR-0059/0060 reject stale or unresolved continuation |
| Implementation handoff | AR-0039 proves the complete synthetic trace | AR-0025 owns task transition and evidence references | AR-0061 checks the cross-project trace |

The local dependency chains are:

```text
AWG:        AR-0035 -> {AR-0036, AR-0037} -> AR-0038 -> AR-0039
Coordinator: AR-0022 -> AR-0023 -> AR-0024 -> AR-0025
AWQ:        AR-0058 -> AR-0059 -> AR-0060 -> AR-0061
```

The cross-project implementation order is AWG AR-0035, Coordinator AR-0022,
and AWQ AR-0058 first; then the planning/discussion contracts; then
reconciliation/reopen enforcement; finally the end-to-end trace. Each project
may implement its own AR only after its local dependencies and the referenced
cross-project contract revisions are available.

## Required user-interaction points

1. **Initial planning/design review:** after literature intake, detailed task
   decomposition, dependency graph, work plan, AR structure, and concise design
   document exist. The user receives context and implications and must approve,
   reject, or request changes.
2. **Explicit requested discussion:** every user-designated subsystem,
   interaction, or conceptual decision creates a typed discussion gate. The
   agent presents ranked alternatives, confidence by dimension, pros/cons,
   evidence gaps, downstream effects, reversibility, and formal-check limits.
3. **Specification review:** every design/conceptual option has a formally
   checked specification. The agent explains its important predicates,
   assumptions, scope, limitations, and downstream implications before the
   user reviews it.
4. **Post-discussion reconciliation:** the agent records before/after versions
   of the work plan, design, specifications, dependencies, and ARs. Contradictory
   or incomplete guidance reopens only the affected points and requires another
   discussion before continuation.

The final user decision is separate from agent analysis, implementation, test,
and quality evidence. A user-added solution is evaluated with the same schema
as existing candidates before selection. Private transcripts and prompts are
never copied into public state.

## Discussion TUI integration

The reusable discussion TUI lives in the AWG product and is used for both
agent-initiated and user-initiated discussions. Its work is decomposed as:

```text
AWG:        AR-0040 -> {AR-0041, AR-0042} -> AR-0043 -> AR-0044
Coordinator: AR-0026 -> AR-0027 -> AR-0028 -> AR-0029
AWQ:        AR-0062 -> AR-0063 -> AR-0064 -> AR-0065
```

The left pane switches live between the current work plan and concise design
document. It follows the active point's document anchor, scrolls there, and
highlights its phrases/key words. The right pane is a list or tree of points;
unresolved points remain highlighted. Each point retains independent candidate
solutions, implication helper evidence, user selection or rejection, and a
user-authored proposal that is evaluated before selection.

Batching happens before opening the TUI and includes only independent points;
each point still has its own identity and disposition. Safe exit atomically
persists all proposals and responses, unresolved/re-ask markers, and a final
free-text request. That request is explicitly mapped to an existing or new AR
and appears in future discussion planning. Coordinator binds sessions and
recovery to task revisions; AWQ checks rendering, persistence, privacy, and
integration contracts; AWG owns the UI, decision semantics, and the
cross-project composition test harness. AR-0044 consumes the public contracts
from Coordinator AR-0029 and AWQ AR-0065 without importing their implementation
internals.

## Formal and quality invariants

- Missing interaction, stale artifact, missing formal result, or unresolved
  contradiction is fail-closed.
- Coordinator owns task identity, dependency, lease, revision, and transition.
- AWG owns alternatives, confidence, oracle packet, decision semantics, and
  reusable guidance.
- AWQ owns quality policy, schema/privacy/formal-evidence validation, and
  truthful limitations; it never substitutes for user intent or implementation
  correctness.
- Every change is independently reviewed and passes the applicable repository
  gates before merge or publication.
