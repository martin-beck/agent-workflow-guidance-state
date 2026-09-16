# Agent Workflow Guidance state

This repository is the durable coordination state for
[Agent Workflow Guidance](https://github.com/martin-beck/agent-workflow-guidance).
It is bound to the product repository and uses the vendored Agent Workflow
Coordinator release recorded in `coordinator.vendor.json`.

Use `tools/handoffctl` for claims, updates, transitions, snapshots, and
reconciliation. Do not edit generated views directly. Task records contain
public-safe plans only; private oracle packets and transcripts do not belong in
this repository.

For design or conceptual ARs, use `tools/promote_awg.py` as the promotion
preflight. It verifies the task's specification reference, exact digest,
passed formal-check result, and task-revision binding before delegating the
planned-to-open mutation to `handoffctl`. Operational ARs still require a
bounded specification and formal-check evidence. Direct `handoffctl promote`
is reserved for tasks that have already passed the project promotion policy;
the project-owned adapter does not replace Coordinator authority.
