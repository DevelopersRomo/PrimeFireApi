# PrimeFire API

REST API built with FastAPI for managing employees, licenses and software assets of PrimeFire Corp.

## 🚀 Features

- **FastAPI**: Modern and fast framework for REST APIs
- **SQL Server**: Relational database
- **SQLModel**: ORM that combines SQLAlchemy and Pydantic for data models
- **Pydantic**: Automatic data validation integrated
- **CORS**: Support for requests from frontend (localhost:4200)
- **Azure AD Authentication**: OAuth2 with PKCE for secure endpoint access
- **Microsoft 365 Sync**: Bidirectional synchronization with Microsoft Graph API for employee data

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- SQL Server installed and configured
- ODBC Driver 17 for SQL Server installed

### 1. Clone the repository

```bash
git clone <https://github.com/DevelopersRomo/PrimeFireApi>
cd PrimeFireApi
```

### 2. Create virtual environment

**Windows:**

_CMD/PowerShell:_

```cmd
python -m venv venv
venv\Scripts\activate
```

_PowerShell (alternativa):_

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

**Linux/Mac:**

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

**Main dependencies:**

- `fastapi`: Modern web framework
- `sqlmodel`: ORM that combines SQLAlchemy and Pydantic
- `uvicorn`: ASGI server for FastAPI
- `fastapi-azure-auth`: Azure AD OAuth2 authentication
- `requests`: HTTP library for token validation

### Update dependencies

To update all dependencies to their latest versions and regenerate `requirements.txt`:


```bash
pip list --outdated
pip install -U -r requirements.txt

or 
pip install --upgrade fastapi uvicorn pydantic pydantic-core pydantic-settings python-dotenv sqlalchemy sqlmodel httpx pytest pytest-asyncio pyodbc cryptography pyjwt starlette typing-extensions fastapi-azure-auth requests python-multipart
pip freeze | Select-String -Pattern "^(fastapi|uvicorn|pydantic|pydantic-core|pydantic-settings|python-dotenv|sqlalchemy|sqlmodel|httpx|pytest|pytest-asyncio|pyodbc|cryptography|pyjwt|starlette|typing-extensions|fastapi-azure-auth|requests|python-multipart)==" | Out-File -FilePath requirements.txt -Encoding utf8
```

This will upgrade the packages and update the `requirements.txt` file with the new versions.

### 4. Configure database

Copy the `.env` file and configure it with your SQL Server credentials:

```bash
cp .env .env.local
```

Edit the `.env` file with your data:

```env
DB_SERVER=localhost\SQLEXPRESS
DB_DATABASE=PrimeFireCorp
DB_USERNAME=sa
DB_PASSWORD=your_password_here
DB_DRIVER=ODBC Driver 17 for SQL Server
DB_ECHO=False
```

**Note**: The `.env` file is included in `.gitignore` for security.

### 5. Run the application

## 🏃‍♂️ Execution

### Development

```bash
# Igual que produccion: 3 workers
uvicorn main:app --port 8000 --workers 3
```

> **Nota:** `--reload` NO es compatible con `--workers` (uvicorn lo ignora y
> levanta 1 solo proceso). Si necesitas hot-reload mientras desarrollas:
>
> ```bash
> uvicorn main:app --reload
> ```
>
> Con 3 workers ten en cuenta:
> - El cache de `/employees` es por-proceso: va firmado por tenant, se valida
>   con un marker de DB (altas/bajas) y tiene TTL de 5 min.
> - Los schedulers (sync de empleados, recurrencia de tickets) corren en UN
>   solo worker gracias a un file-lock (`primefire_api_schedulers.lock` en temp).

The API will be available at: `http://localhost:8000`
The API URL swagger http://localhost:8000/docs

### Production

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 3
```

### Run Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_licenses.py
pytest tests/test_employees.py

# Run with coverage
pytest --cov=.
```

See `tests/README.md` for detailed testing information.

## 🔧 Linting & Formatting

Commands for code formatting and linting:

**Windows:**

```cmd
ruff format .; ruff check . --fix --unsafe-fixes; codespell --check-filenames --count; mypy .
```

**Mac/Linux:**

```bash
ruff format . && ruff check . --fix && codespell --check-filenames --count && mypy .
```

### Individual commands:

```bash
# Format code
ruff format .

# Lint and fix
ruff check . --fix --unsafe-fixes

# Check spelling in filenames
codespell --check-filenames --count

# Type checking
mypy .
```

## 📝 Development Notes

- The project uses SQLModel (SQLAlchemy + Pydantic) with SQL Server
- Models combine database definition and Pydantic validation in a single class
- Database dependencies are handled with SQLModel sessions
- The application includes standard HTTP error handling
- Response schemas inherit directly from SQLModel

## 🤖 AI Development Tools

This project uses **Agent Teams Lite** and **Engram** for enhanced AI-assisted development.

### Agent Teams Lite (SDD Workflow)

[Agent Teams Lite](https://github.com/Gentleman-Programming/agent-teams-lite) implements **Spec-Driven Development (SDD)** - a workflow where a coordinator delegates work to 9 specialized sub-agents.

#### Architecture

| Agent | Function |
|-------|----------|
| Explorer | Investigates the codebase |
| Proposer | Proposes changes |
| Spec Writer | Writes specifications |
| Designer | Designs solutions |
| Task Planner | Plans implementation tasks |
| Implementer | Writes the code |
| Verifier | Validates results |
| Archiver | Archives completed changes |
| Skill Registry | Manages project skills |

#### Commands

```bash
/sdd-init          # Initialize SDD context
/sdd-new <name>   # Start a new feature/change
/sdd-explore <topic>  # Explore ideas in the codebase
/sdd-continue      # Run the next phase
/sdd-apply         # Implement planned tasks
/sdd-verify        # Validate changes
/sdd-archive       # Complete and archive the change
```

#### Usage

1. Open the project in **VS Code** or **Cursor** with Claude Code
2. Type `/sdd-init` to initialize the context
3. Use `/sdd-new <feature-name>` to start a new change
4. Approve between phases as the orchestrator guides you through exploration, specification, design, and implementation

---

### Engram (Persistent Memory)

[Engram](https://github.com/Gentleman-Programming/engram) provides **persistent memory** for AI coding agents using SQLite + FTS5. It works across all your AI coding tools.

#### Features

- **Persistent Memory**: Remembers decisions, patterns, and context between sessions
- **Full-Text Search**: Search through all saved memories
- **Cross-Session**: Works with Claude Code, VS Code, Cursor, OpenCode, and more
- **Zero Dependencies**: Single binary, one SQLite file

#### Available Tools

When Engram is active, you have access to:

| Tool | Description |
|------|-------------|
| `mem_save` | Save a memory with title, content, and tags |
| `mem_search` | Search memories by query |
| `mem_context` | Get relevant context for current task |
| `mem_get_observation` | Retrieve a specific memory |
| `mem_list` | List memories with filters |
| `mem_update` | Update existing memory |
| `mem_delete` | Delete a memory |

#### Usage Example

```python
# Save a decision or pattern for future reference
mem_save(
    title="API Error Handling Pattern",
    content="Always use ProblemDetails for API errors with proper RFC 7807 compliance",
    tags=["api", "error-handling", "best-practices"]
)

# Search for relevant context before implementing
mem_search(query="authentication azure ad oauth")
```

---

### Setup

#### Requirements

- **VS Code** or **Cursor** with Claude Code extension
- **Engram binary** (installed globally)

#### Installation

**1. Engram (if not installed):**

```powershell
# Download from GitHub Releases
curl -L -o engram.zip "https://github.com/Gentleman-Programming/engram/releases/download/v1.10.0/engram_1.10.0_windows_amd64.zip"
Expand-Archive -Force engram.zip -DestinationPath "$env:USERPROFILE\bin"
# Add to PATH or use full path
```

**2. Configure MCP in Claude Code:**

Add to `C:\Users\<you>\.claude\settings.json`:

```json
{
  "mcpServers": {
    "engram": {
      "command": "C:\\Users\\<you>\\bin\\engram.exe",
      "args": ["mcp"]
    }
  }
}
```

**3. Skills are already configured:**

The skills are linked in `.claude/skills/` for Claude Code, `.cursor/skills/` for Cursor, and `.copilot/skills/` for VS Code.

#### Restart Your Editor

After installation, **restart VS Code/Cursor** to activate the MCP server and skills.

---

### Project Structure

```
.claude/                 # Claude Code configuration
  ├── settings.json      # MCP servers & permissions
  └── skills/            # AI agent skills (linked)
    ├── sdd-*            # SDD workflow skills
    └── mem-*            # Memory skills

.skills/                 # Additional project skills
openspec/                # SDD artifacts storage
```

## 🤝 Contributing

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is under the MIT License - see the [LICENSE](LICENSE) file for details.
