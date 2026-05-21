<div align="center">
  <img src="docs/cover.png" alt="SpecPlane" width="100%">
  <p><strong>Reviewable product contracts before implementation begins.</strong></p>
  <p>
    <a href="#why-specplane">Why</a> ·
    <a href="#workflow">Workflow</a> ·
    <a href="#quick-start">Quick start</a> ·
    <a href="#verification">Verification</a> ·
    <a href="#project-boundaries">Boundaries</a>
  </p>
  <p>
    <img alt="Status: planning and scaffold toolkit" src="https://img.shields.io/badge/status-planning_%2B_scaffold_toolkit-64748b">
    <img alt="Python 3.11 or newer" src="https://img.shields.io/badge/python-3.11%2B-3776AB">
    <img alt="Output: contracts, skeleton, backlog" src="https://img.shields.io/badge/output-contracts_%C2%B7_skeleton_%C2%B7_backlog-1559f6">
    <img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-16a34a">
  </p>
</div>

SpecPlane is a contract toolkit for moving from product requirements to a reviewable implementation skeleton. It validates a structured PRD and engineering contract files, then generates placeholder paths and a CSV backlog that retain references to the source decisions.

Use SpecPlane when requirements, API, data, security, test, interface, and scaffold decisions need to be checked together before implementation begins. It generates structure and traceability—not a finished application.

## Why SpecPlane

Planning documents often look complete in isolation while disagreeing at their boundaries. A feature identifier changes in the PRD but not the test matrix. An API operation has no data owner. A role appears in a flow but not in the authorization matrix. Generated scaffolding then gives the appearance of progress while losing the decisions that shaped it.

SpecPlane treats the planning set as one contract surface. The PRD provides the product boundary. Feature and flow records describe behavior. API, data, authentication, billing, security, test, UI, and scaffold templates capture engineering decisions in reviewable files. Validators catch structural drift before generation, and source markers carry those decisions into the skeleton and backlog.

It helps teams:

- review cross-discipline contracts before opening implementation work;
- generate a consistent repository skeleton from an approved manifest;
- retain requirement references near generated files;
- produce backlog rows with acceptance criteria and edge cases already attached.

## What is included

| Area | Contents |
| --- | --- |
| Product requirements | JSON schema, minimal example, and authoring template |
| Feature and flow specs | Feature, state, role, edge-case, and interaction contracts |
| Engineering contracts | API, data, authentication, billing, security, testing, and UI records |
| Scaffold manifest | Declares the application, package, database, and test paths to generate |
| Validators | Check PRD shape, contract fields, identifiers, names, and source markers |
| Traceability check | Looks for specification references near generated implementation files |
| Backlog generator | Produces CSV work items with acceptance criteria, edge cases, and tasks |
| Starter templates | Minimal OpenAPI, SQL, TypeScript, and component-tree forms |

The specification directories are meant to be reviewed as one system. A change to a feature identifier, for example, should remain visible in the API, data, tests, and generated backlog.

## Implemented capabilities

### Contract set

- PRD schema, minimal fixture, and authoring template.
- Feature, user-flow, state-flow, role, edge-case, API, data, authentication, billing, security, test, and UI templates.
- Application connector and connection-manifest templates.
- Technology, module-registry, and quality-gate manifests.

### Validation

- JSON Schema validation for the structured PRD.
- Repository-wide contract checks for required fields, identifiers, and expected files.
- Documentation naming checks for predictable review surfaces.
- Traceability checks for source markers in generated TypeScript, JavaScript, and SQL files.

### Generation

- Manifest-driven application, package, database, and test skeleton creation.
- Existing-file preservation on repeated scaffold runs.
- CSV backlog generation with acceptance criteria, edge cases, and implementation tasks.
- Minimal OpenAPI, SQL, adapter-interface, and component-tree starter forms.

## Workflow

1. Start from [the PRD template](specs/prd/PRD_TEMPLATE.md) and define the product boundary.
2. Add feature and engineering contracts for the flows being planned.
3. Validate the PRD and the repository contract set.
4. Generate the declared skeleton into a new output directory.
5. Check source references and create the issue backlog.
6. Replace placeholders through normal implementation and review.

The scaffold generator preserves existing files. It writes only paths declared by the scaffold manifest, which makes repeated runs safer during early planning.

## Quick start

SpecPlane requires Python 3.11 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python scripts/validate_prd.py \
  --prd specs/prd/EXAMPLE_MINIMAL_PRD.json \
  --schema specs/prd/PRD_SCHEMA.json
python scripts/validate_contracts.py
```

Generate the synthetic example skeleton and backlog:

```bash
python scripts/scaffold_from_prd.py \
  --prd specs/prd/EXAMPLE_MINIMAL_PRD.json \
  --out generated/skeleton
python scripts/check_spec_traceability.py --root generated/skeleton
python scripts/generate_issue_backlog.py --out generated/backlog.csv
```

The backlog carries acceptance criteria, edge cases, and tasks drawn from the API, data, test, and scaffold contracts. The traceability checker looks for source markers near the start of JavaScript, TypeScript, and SQL files under `apps/`, `packages/`, `database/`, and `tests/`.

## Practical usage

Use the minimal PRD as a contract test before adapting the templates to a real product. Run validation after every identifier or boundary change; generation should follow an approved contract set, not serve as a substitute for review.

Generate into a disposable or clearly isolated directory first. The scaffold command preserves existing files, which makes repeated runs safer, but it does not merge business logic or decide how a placeholder should be implemented. Review the generated path list and backlog before moving either into an active application repository.

The templates are intentionally small. Extend them when a decision must be shared across product and engineering; avoid adding fields that no validator, reviewer, or generator consumes.

## Verification

```bash
python -m unittest discover -s tests -v
```

Tests cover schema and contract validation, naming rules, scaffolding, preservation of existing files, traceability checks, and backlog output.

## Repository map

| Path | Responsibility |
| --- | --- |
| `specs/prd` | PRD template, schema, and minimal fixture |
| `specs/features`, `specs/flows`, `specs/state` | Product behavior and state contracts |
| `specs/api`, `specs/data`, `specs/auth`, `specs/billing` | Service and persistence boundaries |
| `specs/security`, `specs/roles`, `specs/tests`, `specs/ui` | Authorization, verification, and interface contracts |
| `specs/scaffold` | Declared file, module, and scaffold plans |
| `manifests/` | Technology, module, and quality-gate records |
| `templates/` | Minimal OpenAPI, SQL, TypeScript, and component-tree forms |
| `scripts/` | Validators, scaffold generator, traceability check, and backlog generator |
| `applications/_templates` | Connector and application-connection manifests |

## Project boundaries

SpecPlane is complete as a planning and scaffold toolkit. Generated files contain placeholders and small data-object interfaces; authentication, billing, business rules, interface behavior, and deployment remain implementation work.

Validation establishes shape, required fields, identifiers, and reference markers. It does not prove that every source reference resolves or that the contracts describe the correct product. Install the declared dependencies before using the generators; dependency-free smoke checks do not provide full YAML or JSON Schema validation.

Generated skeletons are not production applications. They do not include implemented authentication, authorization, billing, migrations, business rules, interface behavior, observability, deployment, or security review. Those decisions remain owned by the target product and should be verified against the approved contracts.

Security and contribution guidance are in [SECURITY.md](SECURITY.md) and [CONTRIBUTING.md](CONTRIBUTING.md).

## Contributing, security, and license

Contract changes should update the affected example, validator, and tests in the same pull request. Keep generated fixtures free of real customer requirements, credentials, infrastructure addresses, or proprietary schemas.

Report unsafe path generation, overwrite behavior, validator bypasses, or sensitive-data exposure through GitHub's private security-advisory channel.

SpecPlane is available under the [MIT License](LICENSE).
