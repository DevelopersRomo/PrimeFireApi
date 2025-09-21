# PrimeFire API

REST API built with FastAPI for managing employees, licenses and software assets of PrimeFire Corp.

## 🚀 Features

- **FastAPI**: Modern and fast framework for REST APIs
- **SQL Server**: Relational database
- **SQLModel**: ORM that combines SQLAlchemy and Pydantic for data models
- **Pydantic**: Automatic data validation integrated
- **CORS**: Support for requests from frontend (localhost:4200)

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- SQL Server installed and configured
- ODBC Driver 17 for SQL Server installed

### 1. Clone the repository

```bash
git clone <repository-url>
cd PrimeFireApi
```

### 2. Create virtual environment

**Windows:**

*CMD/PowerShell:*
```cmd
python -m venv venv
venv\Scripts\activate
```

*PowerShell (alternativa):*
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
uvicorn main:app --reload
```

The API will be available at: `http://localhost:8000`
The API URL swagger http://localhost:8000/docs

### Production

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
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

## 📝 Development Notes

- The project uses SQLModel (SQLAlchemy + Pydantic) with SQL Server
- Models combine database definition and Pydantic validation in a single class
- Database dependencies are handled with SQLModel sessions
- The application includes standard HTTP error handling
- Response schemas inherit directly from SQLModel

## 🤝 Contributing

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is under the MIT License - see the [LICENSE](LICENSE) file for details.
