Project Zeus: M02 Technical Specification

Milestone: Agent and Task Execution Core
Version: 0.2
Status: Proposed for approval
Dependency: Connectome Core v0.1

1. Objective

Create a deterministic task execution framework that allows Zeus agents to receive tasks, validate them, request approval, execute authorized operations, and record their results.

The framework must remain independent of any specific LLM provider.

2. Core components

Task

Represents one unit of work.

Required fields:

- task_id
- task_type
- description
- status
- priority
- created_at
- assigned_agent
- input_data
- result
- error
- retry_count

TaskStatus

Supported lifecycle states:

- PENDING
- VALIDATING
- AWAITING_APPROVAL
- APPROVED
- RUNNING
- COMPLETED
- FAILED
- REJECTED

Invalid state transitions must be rejected.

Agent

Represents an execution identity with defined responsibilities.

Initial agent identities:

- Zeus: development and system tasks.
- Merchant: future commerce-related tasks.

Agent definitions must not grant unrestricted permissions.

TaskQueue

Responsible for:

- Accepting validated tasks.
- Maintaining task order.
- Retrieving eligible tasks.
- Preventing duplicate execution.
- Tracking task status.

ApprovalManager

Responsible for:

- Determining whether approval is required.
- Recording approval or rejection.
- Preventing execution before authorization.
- Recording who or what authorized the operation.

TaskExecutor

Responsible for:

- Executing approved task handlers.
- Enforcing execution limits.
- Capturing results and failures.
- Updating task status.
- Recording execution events.

3. Execution lifecycle

1. Task is submitted.
2. Task structure is validated.
3. Agent responsibility and permissions are checked.
4. Approval requirements are evaluated.
5. Task waits for approval when required.
6. Approved task enters the queue.
7. Executor runs the registered task handler.
8. Result or error is recorded.
9. Task reaches a terminal state.
10. Events are available for inspection.

4. Execution boundaries

- Only registered task handlers may execute.
- No arbitrary model-generated code execution.
- No unrestricted shell execution.
- No direct external API writes.
- Retry counts must be bounded.
- Execution time must be bounded.
- Failed tasks must not silently report success.
- Duplicate task execution must be prevented within the executor's defined scope.
- Rejected tasks must never execute.

5. Event logging

The existing EventLog should record relevant lifecycle events:

- task_created
- task_validated
- task_rejected
- task_approval_requested
- task_approved
- task_rejected_by_approval
- task_started
- task_completed
- task_failed

Events should include relevant task and agent identifiers.

6. Testing requirements

Tests must cover:

- Task creation and validation.
- Valid and invalid state transitions.
- Agent assignment.
- Permission enforcement.
- Approval and rejection.
- Queue ordering.
- Duplicate execution prevention.
- Successful execution.
- Handler failures.
- Retry limits.
- Execution time limits.
- Event logging.
- Existing v0.1 regression tests.

7. Architecture constraints

- Preserve the existing Connectome Core.
- Do not introduce an LLM dependency.
- Do not introduce Shopify integration.
- Do not introduce cloud orchestration.
- Do not introduce a dashboard.
- Use deterministic mock task handlers.
- Keep task execution separate from reasoning and proposal generation.

8. Acceptance criteria

M02 is complete when:

1. Tasks can be created and validated.
2. Tasks can be assigned to authorized agents.
3. Tasks follow an enforced lifecycle.
4. Approval requirements are enforced.
5. Only approved tasks reach execution.
6. Registered handlers execute within configured limits.
7. Results and failures are recorded.
8. Task events are inspectable.
9. Automated tests cover all critical paths.
10. Ruff, mypy, and pytest pass.
11. Coverage remains at least 90%.
12. Existing v0.1 functionality remains intact.

9. Implementation policy

M02 will be implemented incrementally.

Each component must be specified, tested, and reviewed before introducing the next dependent component.

No M03 LLM functionality begins until M02 is complete and approved.

---

End of M02 Technical Specification