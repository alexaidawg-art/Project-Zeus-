Project Zeus: v0.2 Development Roadmap

Project: Project Zeus
Roadmap version: 0.2
Approval date: 2026-11-08
Status: Approved roadmap, implementation not yet started

1. Vision

Evolve Project Zeus from a deterministic cognitive core into a controlled, multi-agent system capable of planning tasks, using replaceable AI reasoning providers, presenting work through a mobile-friendly interface, assisting with content creation, and interacting with approved external services.

The Connectome Core remains the foundation.

2. Architectural principles

All v0.2 milestones must preserve these principles:

1. Connectome first: The v0.1 core remains the knowledge and relationship foundation.
2. Separation of reasoning and execution: AI may interpret, plan, and propose. Deterministic code validates and executes.
3. Human approval: Sensitive, external, destructive, or publishing actions require explicit authorization.
4. Replaceable intelligence: No single LLM provider may become a mandatory architectural dependency.
5. Observable behavior: Tasks, decisions, proposals, approvals, failures, and results must be logged.
6. Bounded execution: Agents need limits on retries, execution time, permissions, and resource consumption.
7. Mobile-first operation: The system must be manageable from a phone.
8. Cost control: Preserve the $0/month operating-budget target where practical. No paid service or usage-based API may be enabled without explicit approval.
9. Incremental development: Each milestone must be specified, implemented, tested, reviewed, and approved before the next begins.

3. Milestone sequence

M02: Agent and Task Execution Core

Goal: Give Zeus the ability to represent, manage, and execute controlled tasks.

Deliverables:

- Task data model and lifecycle.
- Task queue and status management.
- Agent identity and responsibility definitions.
- Deterministic task executor.
- Task validation and permission checks.
- Human approval gates.
- Execution results and failure records.
- Event logging integrated with the existing core.
- Mock tasks for deterministic testing.

Acceptance criteria:

- Tasks can be created, validated, queued, executed, and completed.
- Tasks support clear states, including pending, approved, running, completed, failed, and rejected.
- Unauthorized tasks cannot execute.
- Failed tasks produce inspectable error records.
- Execution limits prevent uncontrolled loops.
- Tests cover normal execution, invalid tasks, rejection, failure, and recovery.
- Existing v0.1 tests remain green.
- Coverage remains at or above 90%.

Out of scope: LLM integration, Shopify actions, dashboards, and autonomous external operations.

M03: Replaceable LLM Interface

Goal: Allow agents to use language models without coupling the Zeus core to one provider.

Deliverables:

- Provider-independent model interface.
- Standard request and response structures.
- Provider adapter contract.
- Mock provider for deterministic testing.
- Structured output handling.
- Proposal generation compatible with "ProposalValidator".
- Error, timeout, and unavailable-provider handling.
- Explicit model and usage configuration.

Acceptance criteria:

- The agent layer can switch providers without modifying the Connectome Core.
- Model responses are treated as untrusted proposals.
- Invalid or malformed responses are rejected.
- Model output cannot directly mutate the Connectome.
- Mock-provider tests run without network access.
- API credentials are never committed to GitHub.
- Any real provider connection requires separate cost and credential approval.

Out of scope: Unbounded model calls, unrestricted autonomous execution, and mandatory paid inference.

M04: Mobile-Friendly Zeus Dashboard

Goal: Provide a simple phone-accessible control center.

Deliverables:

- Mobile-friendly "index.html" interface.
- Agent status display.
- Task queue and task details.
- Execution history.
- Approval and rejection controls.
- System activity and error visibility.
- Basic configuration display.

Acceptance criteria:

- Interface works on a mobile browser.
- User can inspect tasks and their statuses.
- User can approve or reject eligible proposals.
- User can inspect execution results and failures.
- The dashboard cannot bypass backend validation or permission checks.
- No credentials or privileged API keys are exposed to the browser.

Out of scope: Complex analytics, public user accounts, and unnecessary visual features.

M05: Content Studio

Goal: Add a controlled creative workspace for generating and managing content.

Deliverables:

- Content task definitions.
- Draft generation workflow.
- Content review and revision.
- Asset and draft organization.
- Approval before publication.
- Content status tracking.

Acceptance criteria:

- Content can be requested, drafted, reviewed, and approved.
- Drafts remain separate from published content.
- Publishing is not automatic.
- Content tasks use the same task and approval infrastructure.
- Content activity is recorded.

Out of scope: Unapproved publishing, unrestricted social account access, and paid content services without approval.

M06: Shopify Merchant Integration

Goal: Give the Merchant agent controlled access to the existing Shopify store.

Target store: "https://luigis-gadgets.myshopify.com/"

Deliverables:

- Secure Shopify authentication.
- Read-only product access initially.
- Read-only content and theme access where supported and needed.
- Product and store information retrieval.
- Merchant task workflows.
- Explicit approval gates for write operations.
- Auditable action and result records.

Acceptance criteria:

- Credentials are stored securely outside the repository.
- Initial access uses only necessary read scopes.
- The Merchant agent can inspect approved store information.
- Write operations remain disabled until separately authorized.
- Approved write actions are validated and logged.
- Failed API requests do not silently produce success states.

Out of scope: Unapproved product changes, orders, payments, customer-data access, and automatic publishing.

M07: Cloud Scheduling and Background Operations

Goal: Allow approved work to run in the cloud without requiring the phone app to remain open.

Deliverables:

- Scheduled task execution.
- Background job runner.
- Task persistence and recovery.
- Execution monitoring.
- Morning activity reports.
- Pending approval summaries.
- Failure notifications or reports.
- Resource and execution limits.

Acceptance criteria:

- Approved scheduled tasks execute independently of the phone session.
- Jobs can be inspected after execution.
- Interrupted jobs are handled safely.
- Reports distinguish completed, failed, and awaiting-approval tasks.
- Sensitive actions still require approval.
- Scheduling respects the $0/month budget target unless separately approved.

Out of scope: Unlimited background compute, uncontrolled recurring jobs, and unapproved paid infrastructure.

4. Dependency order

The intended implementation sequence is:

1. M02 establishes task execution and approval.
2. M03 adds replaceable AI reasoning.
3. M04 provides the mobile control interface.
4. M05 adds content workflows.
5. M06 connects the Merchant agent to Shopify.
6. M07 adds scheduled cloud execution and reporting.

A milestone may be adjusted only after its dependencies and impact are reviewed.

5. Global quality gates

Every milestone must:

- Have a written implementation specification.
- Define acceptance criteria before coding.
- Include automated tests.
- Pass Ruff and mypy.
- Maintain at least 90% test coverage.
- Preserve existing functionality.
- Document architectural decisions.
- Avoid introducing unapproved dependencies.
- Receive review and explicit approval before moving forward.

6. Permanent safety and execution rules

- Models do not directly execute arbitrary code.
- Proposals must pass deterministic validation.
- External writes require explicit authorization.
- Secrets must never be stored in source control.
- Agents must operate within defined permissions.
- Task execution must be bounded and auditable.
- No milestone may silently expand its own scope.

7. First implementation target

M02: Agent and Task Execution Core

The first M02 deliverable will be a written technical specification defining task states, task structure, agent responsibilities, execution boundaries, approval rules, event logging, and test requirements.

No M02 implementation begins until that specification is reviewed.

---

Project Zeus v0.2: ROADMAP APPROVED
Next milestone: M02, Agent and Task Execution Core