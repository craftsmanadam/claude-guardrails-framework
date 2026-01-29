# claude-guardrails-framework

A composable framework for generating organization-wide `CLAUDE.md` guardrails from profiles, targets, and packs.

## Why
Teams need consistent, auditable developer guardrails. This repo defines:
- **Profiles**: strict / moderate / permissive baselines.
- **Targets**: domain or stack-specific rules (base, python, node, docs, sql, opentofu, etc.), including default analysis and testing tools.
- **Packs**: focused rule bundles (security, privacy, compliance, performance, style, etc.).

You can compose these into a single global `CLAUDE.md` for a team, e.g. `strict + python + microservice + security + privacy`.


## Outputs
- Generated `CLAUDE.md` files are intended to be installed as global guardrails or committed to repos as needed.
- Example (global install):
  - `cp out/CLAUDE.md ~/.config/claude/CLAUDE.md`
- Example (repo install):
  - `cp out/CLAUDE.md ./CLAUDE.md`

## Lifecycle overview
Our goal is to ensure our tools behave professionally. We can move quickly and discard cheap experiments, but when we decide to keep a project it should meet our standards. We assume the lifecycle below.

```
┌──────────────────────────────────────────────────┐
│              Project Initialization              │
└──────────────────────┬───────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────┐
│              Active Work Cycle                   │
│                                                  │
│                      ┌──────────────────────┐    │
│                      ▼                      │    │
│     ┌────────────────────────────────────┐  │    │
│     |        Understand problem          |  │    │
│     └────────────────┬───────────────────┘  │    │
│                      ▼                      │    │
│     ┌────────────────────────────────────┐  │    │
│     |         TDD Development            |  │    │
│     └────────────────┬───────────────────┘  │    │
│                      ▼                      │    │
│     ┌────────────────────────────────────┐  │    │
│     |           Analyze Code             |  │    │
│     └────────────────┬───────────────────┘  │    │
│                      ▼                      │    │
│     ┌────────────────────────────────────┐  │    │
│     |         Analyze Security           |  │    │
│     └────────────────┬───────────────────┘  │    │
│                      ▼                      │    │
│     ┌────────────────────────────────────┐  │    │
│     |        Execute Unit Tests          |  │    │
│     └────────────────┬───────────────────┘  │    │
│                      ▼                      │    │
│     ┌────────────────────────────────────┐  │    │
│     |     Compose Artifact (Build)       |  │    │
│     └────────────────┬───────────────────┘  │    │
│                      ▼                      │    │
│     ┌────────────────────────────────────┐  │    │
│     |     Execute Acceptance Tests       |  │    │
│     └────────────────┬───────────────────┘  │    │
│                      ▼                      │    │
│     ┌────────────────────────────────────┐  │    │
│     |     Run Security Scan (Trivy)      |  │    │
│     └────────────────┬───────────────────┘  │    │
│                      ▼                      │    │
│     ┌────────────────────────────────────┐  │    │
│     |              Commit                |  │    │
│     └────────────────┬───────────────────┘  │    │
│                      └──────────────────────┘    │
│                                                  │
└──────────────────────┬───────────────────────────┘
                       │ 
                       ▼ 
┌──────────────────────────────────────────────────┐
│                    Maintenance                   │
└──────────────────────────────────────────────────┘
```

## Structure
```
profiles/   # baseline strictness
 targets/   # stack or domain rules
 packs/     # focused rule bundles
 templates/ # output templates
 scripts/   # composer
 examples/  # example compositions
```

## Composition model
- **Profile** sets the baseline behavior and default safety posture.
- **Targets** add stack-specific rules (python, node, docs, sql, opentofu, etc.) and declare default analysis/testing tools.
- **Packs** add cross-cutting concerns (security, privacy, compliance, performance, style).
- Output order: **profile → targets → packs → team overrides**.
- Rules may also be conditional with `when`, for example:
  - `when: { targets: [python, microservice] }`
  - `when: { packs: [analysis] }`
  - `when: { profiles: [strict, moderate] }`
- Rules may be excluded with `exclude_when`, for example:
  - `exclude_when: { targets: [sql] }`

## Quick start
```
poetry install
poetry run python scripts/compose.py examples/strict-python-microservice.yml out/CLAUDE.md
```

## How to compose
Minimal composition file:
```
name: strict-python-microservice
profile: strict
targets:
  - base
  - python
  - microservice
packs:
  - security
  - privacy
  - compliance
  - performance
  - style
```

Permissive with analysis enabled:
```
name: permissive-python-analysis
profile: permissive
targets:
  - base
  - python
packs:
  - analysis
```

## Example compositions
- `examples/strict-python-microservice.yml`
- `examples/moderate-node.yml`
- `examples/moderate-sql.yml`
- `examples/permissive-python-analysis.yml`

## Opinionated extras to consider
- **Risk tiering**: production vs. sandbox; higher tiers enforce stricter defaults.
- **Data classification**: PII/PHI/PCI flags that toggle privacy & compliance packs.
- **Change control**: rule versioning + lockfiles for reproducible guardrails.
- **Exception process**: scoped, time-boxed waivers with justification.
- **Tooling policy**: allow/deny list for external tools and network access.

## Engineering principles (strict + moderate)
- Single Responsibility Principle (SRP)
- DRY (Do Not Repeat Yourself)
- Separation of concerns
- Encapsulation
- High cohesion / low coupling
- Explicit over implicit
- Testability as a first-class concern

## Additional principles (strict only)
- Fail fast
- Composition over inheritance

## Language defaults
- **Python**: prefer Poetry for dependency management, pydantic for data validation, and pydantic-settings for configuration.

## Files
- `templates/claude.md.tmpl` is a simple Markdown output template.
- `templates/Makefile.scaffold` is the legacy generic Makefile scaffold.
- `templates/Makefile.scaffold.app` is the application Makefile scaffold.
- `templates/Makefile.scaffold.infra` is the infrastructure Makefile scaffold (may include no-op targets).
- These Makefile scaffolds are examples of intent for humans; they are not auto-applied.
- `templates/pyproject.python.ruff.snippet.toml` provides opinionated ruff defaults for Python and is a copy/paste reference (not auto-applied).
- `scripts/compose.py` composes YAML inputs into a single `CLAUDE.md`.
## Notes
This is an initializer scaffold. Extend the taxonomy, add targets/packs, and tailor wording to your org.
