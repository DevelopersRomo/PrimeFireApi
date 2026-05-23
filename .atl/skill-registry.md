# Skill Registry

## Project: PrimeFire

Generated: 2026-05-08

## SDD Skills (from ~/.config/opencode/skills/)

| Name | Description | Trigger |
|------|-------------|---------|
| sdd-init | Initialize SDD context, detect stack, bootstrap persistence | `/sdd-init`, `sdd init`, `openspec init` |
| sdd-explore | Explore codebase for a topic | `/sdd-explore <topic>` |
| sdd-propose | Create change proposal | `/sdd-propose <name>` |
| sdd-spec | Write specifications (delta specs) | `/sdd-spec` |
| sdd-design | Design solution with architecture decisions | `/sdd-design` |
| sdd-tasks | Break down change into task checklist | `/sdd-tasks` |
| sdd-apply | Implement tasks from a change | `/sdd-apply` |
| sdd-verify | Validate implementation against specs | `/sdd-verify` |
| sdd-archive | Sync delta specs and archive completed change | `/sdd-archive` |
| sdd-onboard | Guided end-to-end SDD walkthrough | onboarding request |

## Global Skills (from ~/.config/opencode/skills/)

| Name | Description | Trigger |
|------|-------------|---------|
| branch-pr | PR creation workflow (issue-first enforcement) | Creating PR, opening PR |
| cognitive-doc-design | Documentation with reduced cognitive load | Writing guides, READMEs, architecture docs |
| comment-writer | Write warm, direct human comments | Drafting PR/issue/review comments |
| gentle-ai-chained-pr | Split large changes into chained/stacked PRs | PR > 400 lines |
| go-testing | Go testing patterns (Bubbletea TUI) | Writing Go tests |
| issue-creation | Issue creation workflow | Creating GitHub issues |
| judgment-day | Parallel adversarial review protocol | "judgment day", "doble review" |
| skill-creator | Create new AI agent skills | Creating/modifying skills |
| skill-registry | Create/update skill registry | "update skills", "skill registry" |
| work-unit-commits | Structure commits as work units | Implementing changes, splitting PRs |

## Project Skills (from .claude/skills/ and skills/)

| Name | Description | Trigger |
|------|-------------|---------|
| fastapi-templates | Create FastAPI projects production-ready | Scaffolding FastAPI |
| find-skills | Discover and install agent skills | "find a skill" |
| mcp-builder | Build MCP servers | Building MCP servers |
| memory-merger | Merge learned memories | Memory consolidation |
| obsidian-markdown | Create/edit Obsidian Markdown | Obsidian docs |
| python-testing-patterns | Testing strategies with pytest | Writing Python tests |
| self-improving-agent | Self-improving agent patterns | Agent improvement |
| skill-creator | Create new skills | Creating skills |
| skill-creator-prowler | Create AI agent skills | Agent skill creation |
| skill-sync-prowler | Sync skill metadata | Skill synchronization |

## PrimeFireApp Custom Skills (from PrimeFireApp/.claude/skills/)

| Name | Description | Trigger |
|------|-------------|---------|
| primefire-angular-component-generator | Generate Angular standalone components | Creating Angular components |
| primefire-material-design-patterns | Angular Material design patterns | Using Material components |
| primefire-msal-auth-integration | MSAL Angular + Azure AD integration | Auth configuration |
| primefire-service-scaffold | Scaffold Angular services | Creating services |
| primefire-route-guards | Route guards (functional) | Creating guards |
| primefire-interceptor-patterns | HTTP interceptor patterns | Creating interceptors |
| primefire-testing-utilities | Jasmine/Karma test utilities | Writing Angular tests |

## Project Conventions

- `PrimeFireApi/AGENTS.md` — Backend conventions (FastAPI, SQLModel, auth, notifications)
- `PrimeFireApp/AGENTS.md` — Frontend conventions (Angular 18, Material, MSAL, OnPush)
- `PrimeFireApi/.clauderc.json` — References `.cursor/rules/*.mdc`
- `PrimeFireApi/.cursor/` — Custom rules (clean-code, opinionated-python, secure-dev, etc.)

## Project Files

- `PrimeFire/AGENTS.md` — Root project agenda and documentation
- `PrimeFireApi/AGENTS.md` — Backend architecture, conventions, auth, modules
- `PrimeFireApp/AGENTS.md` — Frontend architecture, conventions, pending issues
- `PrimeFireApi/pyproject.toml` — Ruff, mypy, pytest, codespell config
- `PrimeFireApi/openspec/config.yaml` — SDD configuration
- `PrimeFireApp/package.json` — Angular 18.2, MSAL, Material, Jasmine/Karma

## Notes

- Backend: FastAPI 0.135.1 + SQLModel + Azure SQL Server
- Frontend: Angular 18.2 + Angular Material 18.2.14 + MSAL 4.0.1
- Testing: pytest 9.0.2 (asyncio strict, 28 test files) + Jasmine/Karma (32 spec files)
- Linting: Ruff (py312, ~50 rule families, Google docstrings), mypy, codespell, TypeScript strict
- Auth: Azure AD OAuth2 PKCE, JWT Bearer, password grant, contact token
- Architecture: Multi-tenant, lazy-loaded Angular modules, CORS to Azure + localhost
- Strict TDD Mode: enabled (test infrastructure detected)
- Persistence: openspec (file-based)
