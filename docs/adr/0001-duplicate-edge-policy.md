ADR 0001: Duplicate Edge Policy

- Status: Accepted
- Date: 2026-11-08
- Project: Project Zeus
- Milestone: Connectome Core v0.1

Context

The Zeus Connectome represents knowledge through typed, weighted, directed relationships between nodes.

A relationship is identified by its source node and target node.

Allowing duplicate relationships without a defined policy could introduce ambiguity into activation propagation, reinforcement, decay, consolidation, and persistence.

For example, creating the same relationship multiple times could produce conflicting weights or inconsistent learning behavior.

Decision

The Connectome will reject duplicate directed relationships.

A relationship between the same source and target nodes may only be created once.

Existing relationships must be modified through explicit weight-update operations.

The following rules apply:

1. Duplicate source-target relationships are rejected.
2. Existing relationship weights are not silently overwritten.
3. Weight changes must use an explicit update operation.
4. Learning operations must not create duplicate relationships.
5. Proposal validation must reject duplicate relationships before execution.
6. The same policy applies consistently across graph operations.

Rationale

Explicit rejection preserves deterministic behavior and prevents accidental changes to existing knowledge.

It also keeps graph creation separate from relationship modification.

This makes learning and activation behavior easier to test, audit, and reproduce.

Consequences

Positive

- Prevents accidental duplicate relationships.
- Avoids ambiguous weight-merging behavior.
- Preserves predictable graph structure.
- Makes relationship updates explicit.
- Simplifies deterministic testing.

Trade-offs

- Repeated relationship observations cannot create separate edges.
- Future implementations may need a dedicated aggregation policy if multiple observations must contribute to one relationship.
- Callers must explicitly update an existing relationship when its weight should change.

Implementation

This decision is enforced by:

- "Connectome.add_edge()"
- "LearningEngine"
- "ProposalValidator"
- Connectome and proposal tests

Future Considerations

If future milestones require merging repeated observations, a separate, explicitly defined aggregation strategy must be proposed and tested.

Possible strategies include weighted averaging, bounded accumulation, or evidence-based reinforcement.

No automatic merge behavior is introduced in v0.1.