# Agent Workflow Guidance state

This repository is the durable coordination state for
[Agent Workflow Guidance](https://github.com/martin-beck/agent-workflow-guidance).
It is bound to the product repository and uses the vendored Agent Workflow
Coordinator release recorded in `coordinator.vendor.json`.

Use `tools/handoffctl` for claims, updates, transitions, snapshots, and
reconciliation. Do not edit generated views directly. Task records contain
public-safe plans only; private oracle packets and transcripts do not belong in
this repository.
