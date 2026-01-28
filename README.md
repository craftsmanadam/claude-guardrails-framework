# claude-guardrails-framework

A composable framework for generating organization-wide `CLAUDE.md` guardrails from profiles, targets, and packs.

## Why
Teams need consistent, auditable developer guardrails. This repo defines:
- **Profiles**: strict / moderate / permissive baselines.
- **Targets**: domain or stack-specific rules (base, python, node, docs, sql, etc.).
- **Packs**: focused rule bundles (security, privacy, compliance, performance, style, etc.).

You can compose these into a single global `CLAUDE.md` for a team, e.g. `strict + python + microservice + security + privacy`.

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
- **Targets** add stack-specific rules (python, node, docs, sql, etc.).
- **Packs** add cross-cutting concerns (security, privacy, compliance, performance, style).
- Output order: **profile → targets → packs → team overrides**.

## Quick start
```
poetry install
poetry run python scripts/compose.py examples/strict-python-microservice.yml out/CLAUDE.md
```

## Opinionated extras to consider
- **Risk tiering**: production vs. sandbox; higher tiers enforce stricter defaults.
- **Data classification**: PII/PHI/PCI flags that toggle privacy & compliance packs.
- **Change control**: rule versioning + lockfiles for reproducible guardrails.
- **Exception process**: scoped, time-boxed waivers with justification.
- **Tooling policy**: allow/deny list for external tools and network access.

## Files
- `templates/claude.md.tmpl` is a simple Markdown output template.
- `scripts/compose.py` composes YAML inputs into a single `CLAUDE.md`.

## Notes
This is an initializer scaffold. Extend the taxonomy, add targets/packs, and tailor wording to your org.
