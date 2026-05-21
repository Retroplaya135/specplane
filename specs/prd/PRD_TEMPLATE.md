# PRD Template

Use this outline to draft the requirements, then encode them as JSON using [PRD_SCHEMA.json](PRD_SCHEMA.json). [EXAMPLE_MINIMAL_PRD.json](EXAMPLE_MINIMAL_PRD.json) shows the expected field names and structure.

## 1. Product identity

- Product name:
- One-line description:
- Value to the user:
- Target market:
- Primary user:
- Buyer, if different:
- Problem:
- Solution:
- Success metric:

## 2. Personas

For each persona, record an ID, name, job to be done, pain points, and decision criteria.

## 3. MVP scope

- In scope:
- Out of scope:
- Release criteria:

## 4. User flows

For each flow, record an ID, name, actor, entry point, steps, success state, failure states, and analytics events.

Cover the flows relevant to the product, including:

- Visitor to signup.
- Signup to onboarding.
- Workspace creation.
- Invite member.
- Core product action.
- Billing/upgrade.
- Support request.

## 5. Data objects

For each data object, record an ID, name, owner, fields, relationships, and retention policy. Choose its tenant scope (`global`, `organization`, `workspace`, or `user`) and sensitivity (`public`, `internal`, `confidential`, or `restricted`).

## 6. Roles and permissions

For each role, record an ID, name, scope, and permissions.

## 7. Acceptance criteria

Give each criterion a stable ID, a testable statement, and a test type: `unit`, `integration`, `e2e`, `manual`, or `security`.

## 8. Edge cases

For each edge case, record an ID, category, trigger, expected behavior, and required test.

## 9. Assumptions

List unresolved questions, the assumptions used until they are answered, and who will resolve them.

## 10. Non-goals

List capabilities deliberately excluded from the implementation.
