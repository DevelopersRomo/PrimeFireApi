# Skill Registry

## Project: PrimeFireApi

Generated: 2026-03-14

## SDD Skills (from ~/.cursor/skills/)

| Name | Description | Trigger |
|------|-------------|---------|
| sdd-init | Initialize SDD context, detect stack | `/sdd-init`, `sdd init` |
| sdd-explore | Explore codebase for a topic | `/sdd-explore <topic>` |
| sdd-propose | Create change proposal | `/sdd-propose <name>` |
| sdd-spec | Write specifications | `/sdd-spec` |
| sdd-design | Design solution | `/sdd-design` |
| sdd-tasks | Plan tasks | `/sdd-tasks` |
| sdd-apply | Implement tasks | `/sdd-apply` |
| sdd-verify | Verify implementation | `/sdd-verify` |
| sdd-archive | Archive completed change | `/sdd-archive` |
| skill-registry | Update skill registry | `/skill-registry` |

## Project Skills (from .claude/skills/)

| Name | Description | Trigger |
|------|-------------|---------|
| find-skills | Discover and install agent skills | "find a skill", "how do I do X" |
| mcp-builder | Build MCP servers | Building MCP servers |
| skill-creator | Create new skills | Creating/modifying skills |
| simplify | Review code for quality | On code changes |

## Project Conventions

- `.cursorrules/clean-code.mdc` - Clean code rules
- `.cursorrules/engineer-to-zero.mdc` - Error handling
- `.cursorrules/opinionated-python.mdc` - Python patterns
- `.cursorrules/performance-standards.mdc` - Performance
- `.cursorrules/secure-dev-python.mdc` - Security
- `.cursorrules/secure-mcp-usage.mdc` - MCP security
- `.cursorrules/secure-sql-usage.mdc` - SQL security
- `.cursorrules/tenacity.mdc` - Retry patterns

## Notes

- This project uses FastAPI + SQLAlchemy with async
- Testing: pytest with asyncio_mode = strict
- Linting: Ruff (py312 target)
- Type checking: mypy