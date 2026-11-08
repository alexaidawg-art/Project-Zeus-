Project Zeus

A deterministic, graph-first cognitive architecture.

Milestone 01: Connectome Core v0.1

The Connectome Core provides a model-independent foundation for representing, activating, learning, and consolidating relationships between knowledge nodes.

Goals

- Typed, weighted graph storage
- Bounded activation propagation
- Reinforcement and decay
- Relationship consolidation
- Persistent JSON storage
- Structured event logging
- Deterministic proposal validation
- Automated test coverage

Architecture

The core is organized into independent components:

Component| Responsibility
"Connectome"| Manages nodes and relationships
"Node" and "Edge"| Define typed knowledge structures
"GraphStore"| Defines the graph persistence interface
"NetworkXStore"| Implements graph storage using NetworkX and JSON
"ActivationEngine"| Performs bounded spreading activation
"LearningEngine"| Handles reinforcement and relationship decay
"ConsolidationEngine"| Strengthens qualifying relationships
"EventLog"| Records ordered system events
"ProposalValidator"| Validates proposed graph changes without applying them
"Config"| Centralizes configurable system parameters

Core design principles

1. Graph-first: Knowledge is represented through nodes and typed relationships.
2. Deterministic: Identical inputs and configurations should produce reproducible results.
3. Bounded activation: Activation propagation is constrained by configured limits.
4. Model-independent: The core does not require an LLM or external AI service.
5. Validation before execution: Proposed changes must pass validation before another component applies them.
6. Separation of responsibilities: Storage, learning, activation, and validation remain distinct components.

Installation

Requirements:

- Python 3.12+
- Git

Clone the repository and install the development dependencies:

git clone https://github.com/alexaidawg-art/Project-Zeus-.git
cd Project-Zeus-
pip install -e ".[dev]"

Running tests

Run the automated test suite:

pytest

Run tests with coverage:

pytest --cov=zeus --cov-report=term-missing --cov-fail-under=90

Run code quality checks:

ruff check .
mypy src/zeus

All required checks must pass before changes are submitted.

Persistence

The persistence layer uses a versioned JSON representation of the graph.

"NetworkXStore" provides:

- Graph serialization and restoration
- Persistence format version validation
- Invalid data rejection
- Atomic file replacement during saves
- Protection against partially written save files

The "GraphStore" protocol keeps the Connectome independent of its concrete storage implementation.

Proposal validation

"ProposalValidator" supports three operation types:

- "create_node"
- "create_edge"
- "update_edge_weight"

Proposals are checked for required fields, supported operations, valid data, existing relationships, duplicate nodes and edges, and configured weight limits.

Unexpected fields are rejected.

Important: Validation does not mutate the Connectome. It determines whether a proposal is acceptable. Applying an approved proposal is a separate responsibility.

Development Rules

- Python 3.12+
- Model-independent core
- No LLM dependency in the core
- Tests must pass before changes are proposed
- One milestone at a time
- Changes must remain within approved scope
- No unapproved external integrations

Agent Protocol

Agents must inspect project instructions before working.

Only approved tasks may be executed.

Changes must be tested and submitted through pull requests.

Agents must not expand milestone scope without approval.

Milestone 01 Scope Boundaries

Milestone 01 focuses exclusively on the deterministic Connectome Core.

The following are outside the scope of v0.1:

- LLM integration
- Autonomous agent execution
- Shopify integration
- External API dependencies
- User interfaces and dashboards
- Cloud orchestration

These may be considered in future milestones after the core is reviewed and approved.

Project Status

Current milestone: Connectome Core v0.1

Latest reported CI results:

- 227 tests passed
- 99.08% total test coverage
- Ruff checks passed
- Mypy checks passed
- GitHub Actions checks green

Final milestone completion remains subject to architecture review, documentation review, and pull request approval.