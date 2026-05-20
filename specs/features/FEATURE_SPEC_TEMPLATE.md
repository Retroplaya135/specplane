# Feature Spec Template

## Feature identity

- Feature ID: `FEAT-000`
- Feature name: one outcome that can be implemented and tested
- Linked PRD requirements: `prd:acceptanceCriteria.AC-000`, `prd:userFlows.flow_id`
- Owner module: one module from `manifests/module_registry.yaml`
- Risk level: low | medium | high | critical
- Source refs: IDs for the requirements and contracts used by this feature

## User story

Describe who needs the capability and what they should be able to do.

## Scope

### In scope

- Explicit capabilities authorized for this feature.

### Out of scope

- Capabilities excluded from this feature.

## Acceptance criteria

- AC-001: measurable behavior and required test tier
- AC-002: measurable behavior and required test tier

## Data model impact

- Tables: exact table/entity IDs
- Columns: exact field names if schema changes are authorized
- Relationships: exact relationship IDs
- RLS impact: required policy IDs and RLS test IDs

## API impact

- Endpoints: exact endpoint IDs
- Request schemas: exact schema IDs
- Response schemas: exact schema IDs
- Error cases: explicit status/code list

## UI impact

- Routes: exact route IDs
- Components: exact component IDs
- Loading states: required component/state IDs
- Empty states: required component/state IDs
- Error states: required component/state IDs
- Unauthorized states: required component/state IDs

## Security impact

- Auth required: public | optional | required | service
- Permissions: exact permission IDs
- Audit events: exact event IDs or explicit `none`
- Sensitive data: classification IDs

## Billing/entitlement impact

- Plan requirements: entitlement IDs or explicit `none`
- Quotas: quota IDs or explicit `none`
- Usage events: usage event IDs or explicit `none`

## Tests required

- Unit: exact test IDs
- Integration: exact test IDs
- E2E: exact test IDs
- Security: exact test IDs

## Edge cases

- Edge-case IDs from `specs/edge_cases/EDGE_CASE_REGISTER.yaml`.

## Files allowed for implementation

- Exact file globs authorized for this feature.

## Files forbidden for implementation

- Exact file globs forbidden for this feature.

## Deferred cases

- Explicitly deferred cases with owner, reason, and target milestone.
