# Agent Workflow Guidance current coordination state

This file is generated. Read `README.md`, then use `tools/handoffctl snapshot`.
Never edit this file directly.

## In Progress

| Priority | Task | Summary | Next action | Owner |
| --- | --- | --- | --- | --- |
| P0 | [AR-0037](tasks/AR-0037.md): Discussion packet and specification review | Specify context-rich user discussions and formally reviewable decision specifications. | Release AR-0037 after merged PR and Coordinator reconciliation; select the next dependency-ready AR. | codex-ar0037-discussion-packet-20260917 |

## Planned

| Priority | Task | Summary | Next action | Owner |
| --- | --- | --- | --- | --- |
| P0 | [AR-0038](tasks/AR-0038.md): Post-discussion reconciliation and reopen loop | Reconcile user guidance into versioned plans, designs, specifications, and ARs. | Specify post-discussion incorporation, contradiction detection, repeated discussion, and before/after artifact reconciliation. | - |
| P0 | [AR-0040](tasks/AR-0040.md): Reusable discussion TUI architecture and navigation | Create the reusable two-pane discussion TUI in the AWG product. | Specify and implement the reusable AWG discussion TUI with two synchronized panes and explicit interaction-point navigation. | - |
| P0 | [AR-0041](tasks/AR-0041.md): Batched discussion packet TUI | Batch discussion points without coupling their decisions or querying the user unnecessarily. | Add batched discussion sessions, per-point proposals, implication helpers, and user-authored solution evaluation. | - |
| P0 | [AR-0042](tasks/AR-0042.md): Discussion persistence and future-point capture | Make discussion persistence, safe exit, re-ask, and future-request mapping lossless. | Persist every proposed and selected solution on safe exit, support optional re-ask, and map free-text future discussion requests to ARs. | - |
| P1 | [AR-0039](tasks/AR-0039.md): End-to-end oracle workflow example | Validate the cross-project oracle workflow with an end-to-end example. | Build a complete synthetic example from literature intake through planning review, discussion, specification review, reconciliation, and implementation handoff. | - |
| P1 | [AR-0043](tasks/AR-0043.md): Discussion TUI cross-project integration | Integrate the reusable TUI with Coordinator events and AWQ quality gates. | Wire the TUI session contract to Coordinator and AWQ and validate agent/user initiation through a complete synthetic workflow. | - |
| P1 | [AR-0044](tasks/AR-0044.md): AWG-owned cross-project TUI test harness | Keep cross-project TUI integration tests and hostile traces in the AWG project. | Implement the AWG-owned cross-project test harness and synthetic traces for Coordinator and AWQ TUI contracts. | - |

## Done

| Priority | Task | Summary | Next action | Owner |
| --- | --- | --- | --- | --- |
| P0 | [AR-0001](tasks/AR-0001.md): AWG protocol and boundary review | Establish the oracle-guidance protocol and its authority boundaries. | Review the AWG protocol and identify the smallest executable reference implementation. | - |
| P0 | [AR-0002](tasks/AR-0002.md): Offline contract validation | Add a deterministic contract checker for AWG records. | Release AR-0002 after merged PR and successful protected checks. | - |
| P0 | [AR-0021](tasks/AR-0021.md): Formal specification checker | Make AWG specifications machine-validatable and autonomously checkable. | Release AR-0021 after merged PR and successful protected checks. | - |
| P0 | [AR-0022](tasks/AR-0022.md): Bootstrap AR topology formalization | Close the bootstrap gap for the first AR tasks of every AWG project. | Release AR-0022 after the topology checker commit and live verification are published. | - |
| P0 | [AR-0023](tasks/AR-0023.md): AWG formal-gate enforcement | Enforce the formal gate at both oracle and implementation boundaries. | Release AR-0023 after merged formal-gate PR and protected checks. | - |
| P0 | [AR-0027](tasks/AR-0027.md): Conceptual AR authoring gate | Enforce specification-first authoring for every future conceptual AR. | Make the formal-specification reference and passed-check evidence mandatory when authoring or opening a conceptual AR. | - |
| P0 | [AR-0028](tasks/AR-0028.md): Self-hosting AWG evolution workflow | Make Agent Workflow Guidance self-hosting and govern its own evolution. | Apply the AWG workflow to AWG's own future design, implementation, quality, and coordination changes after the initial formal gates are complete. | - |
| P0 | [AR-0029](tasks/AR-0029.md): Pinned AWQ CI enforcement bootstrap | Make Agent Workflow Quality a required gate for AWG evolution. | Release AR-0029 after the successful hosted AWQ and contracts runs and verified branch protection. | - |
| P0 | [AR-0030](tasks/AR-0030.md): Specification-gated AR promotion | Enforce the formal specification gate in Coordinator promotion. | Release AR-0030 after merged product formal-gate specification and state adapter verification. | - |
| P0 | [AR-0035](tasks/AR-0035.md): Canonical oracle interaction lifecycle | Define the cross-project oracle interaction lifecycle and mandatory AR gate taxonomy. | Release AR-0035 after merged PR and Coordinator reconciliation; then select the next dependency-ready AR. | - |
| P0 | [AR-0036](tasks/AR-0036.md): Initial project planning and design review gate | Require user review after project decomposition and before autonomous implementation. | Release AR-0036 after merged PR and Coordinator reconciliation; select the next dependency-ready AR. | - |
| P1 | [AR-0003](tasks/AR-0003.md): Coordinator and AWQ integration | Define the first Coordinator and AWQ integration adapters. | Release AR-0003 after merged product binding specification and state checker verification. | - |
| P1 | [AR-0004](tasks/AR-0004.md): Human-guidance evaluation plan | Evaluate uncertainty, expected regret, batching, and guidance reuse. | Turn the literature review into testable guidance-gate hypotheses and a small evaluation plan. | - |
| P1 | [AR-0005](tasks/AR-0005.md): Clarification and expected-regret gate | Model when an agent should clarify instead of acting. | Translate clarification-question and expected-regret literature into an AWG gate and fixtures. | - |
| P1 | [AR-0006](tasks/AR-0006.md): Uncertainty-aware assistance and calibration | Transfer uncertainty-aware assistance into software-task guidance. | Define separate calibration measures for applicability, outcome, and downstream-impact confidence. | - |
| P1 | [AR-0007](tasks/AR-0007.md): Mixed initiative and feedback | Model human feedback as a durable interaction loop. | Specify correction, confirmation, and resume semantics for mixed-initiative oracle interaction. | - |
| P1 | [AR-0008](tasks/AR-0008.md): Delegation, control, and bounded authority | Prevent approval records from laundering uncertainty or accountability. | Define bounded delegation, user control, and authority-scope measures for AWG decisions. | - |
| P1 | [AR-0009](tasks/AR-0009.md): Public project comparison matrix | Survey public agent workflow projects without creating runtime dependencies. | Build a public-project comparison matrix with exact revisions, licenses, HITL semantics, and integration boundaries. | - |
| P1 | [AR-0015](tasks/AR-0015.md): Planner executor reviewer separation | Test the recommendation-versus-verification boundary. | Specify a planner/executor/reviewer evaluation that keeps oracle intent, execution, and verification separate. | - |
| P1 | [AR-0016](tasks/AR-0016.md): Confidence calibration dimensions | Answer research question 1 on multidimensional confidence. | Design calibration experiments for applicability, outcome, and downstream-impact confidence. | - |
| P1 | [AR-0017](tasks/AR-0017.md): Oracle packet batching | Answer research question 2 on batching strategy. | Measure oracle workload and hidden coupling across independent and batched decision packets. | - |
| P1 | [AR-0018](tasks/AR-0018.md): Reusable guidance lifecycle | Answer research question 3 on guidance staleness and over-generalization. | Define expiry, scope matching, counterexamples, and review triggers for reusable guidance. | - |
| P1 | [AR-0019](tasks/AR-0019.md): Anti-rubber-stamp safeguards | Answer research question 4 on oracle decision quality. | Define signals for omitted alternatives, framing bias, and human rubber-stamp decisions. | - |
| P1 | [AR-0020](tasks/AR-0020.md): Intervention evidence and future autonomy | Answer research question 5 on predictive intervention evidence. | Identify intervention evidence that predicts safe autonomy on later dependent tasks. | - |
| P1 | [AR-0024](tasks/AR-0024.md): Coordinator formal-evidence binding | Prevent stale or unverified conceptual decisions from entering coordinated work. | Release AR-0024 after merged evidence-binding specification and checker verification. | - |
| P1 | [AR-0025](tasks/AR-0025.md): Existing AR formal-spec migration | Migrate the existing AWG literature and project ARs to the formal-decision rule. | Superseded by the bounded AR-0031 through AR-0034 migration chain. | - |
| P1 | [AR-0026](tasks/AR-0026.md): AWQ formal-spec quality profile | Make formal-specification compliance an offline quality contract. | Add AWQ requirements and evidence classification for formal specifications and autonomous checks. | - |
| P1 | [AR-0031](tasks/AR-0031.md): Formal-spec migration batch one | Migrate the first formal-decision AR batch. | Migrate AR-0001 through AR-0005 with explicit specification and formal-check references. | - |
| P1 | [AR-0032](tasks/AR-0032.md): Formal-spec migration batch two | Migrate the second formal-decision AR batch. | Migrate AR-0006 through AR-0010 with explicit specification and formal-check references. | - |
| P1 | [AR-0033](tasks/AR-0033.md): Formal-spec migration batch three | Migrate the third formal-decision AR batch. | Migrate AR-0011 through AR-0015 with explicit specification and formal-check references. | - |
| P1 | [AR-0034](tasks/AR-0034.md): Formal-spec migration batch four | Migrate the fourth formal-decision AR batch. | Migrate AR-0016 through AR-0020 with explicit specification and formal-check references. | - |
| P2 | [AR-0010](tasks/AR-0010.md): LangGraph comparison adapter | Evaluate LangGraph as a pause/resume host for AWG packets. | Prototype an AWG-to-LangGraph interrupt/checkpoint mapping in an isolated synthetic example. | - |
| P2 | [AR-0011](tasks/AR-0011.md): AutoGen and Microsoft Agent Framework comparison | Evaluate multi-agent feedback and migration implications. | Compare AutoGen human feedback with Microsoft Agent Framework's supported successor path. | - |
| P2 | [AR-0012](tasks/AR-0012.md): OpenHands integration study | Evaluate AWG in a general software-agent host. | Map AWG decision gates onto OpenHands software-agent planning, tool execution, review, and resume points. | - |
| P2 | [AR-0013](tasks/AR-0013.md): SWE-agent evaluation study | Study software-engineering agent outcomes with oracle guidance. | Evaluate AWG intervention points against SWE-agent tasks and benchmark evidence without conflating scores with governance. | - |
| P2 | [AR-0014](tasks/AR-0014.md): Oracle-guided assistance transfer study | Transfer human-guidance concepts without importing action-level assumptions. | Compare oracle-guided reinforcement-learning assistance with AWG's deliberative software decisions. | - |
