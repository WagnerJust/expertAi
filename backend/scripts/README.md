# Scripts Directory

This directory contains utility scripts for database management, debugging, and development tasks.

## Scripts Overview

### Database Management
- **`db_manager.py`** - Main database management utility for PostgreSQL operations
  - Create and initialize database schema
  - Reset database (drop and recreate)
  - Show database status and connection info
  - Usage: `python db_manager.py [init|reset|status|drop]`

- **`migrate_to_postgres.py`** - Database migration script from SQLite to PostgreSQL
  - Initializes PostgreSQL schema using SQLAlchemy models
  - Waits for PostgreSQL service to be ready
  - Creates database if it doesn't exist
  - Usage: Run during container startup or manually for setup

- **`migrate_database.py`** - **DEPRECATED** Legacy SQLite migration script
  - No longer used - PostgreSQL handles schema automatically
  - Kept for reference only

### Development & Debugging
- **`debug_startup.py`** - Debug script to identify app startup issues
  - Tests imports of all major components
  - Validates configuration and connections
  - Helps identify where startup process hangs
  - Usage: `python debug_startup.py`

- **`mock_llm_service.py`** - Mock LLM service for testing
  - Flask-based mock service that mimics Ollama API
  - Provides `/api/generate` endpoint for testing RAG pipeline
  - Returns realistic mock responses for development
  - Usage: `python mock_llm_service.py` (runs on port 11435)

### PDF Management
- **`fix_pdf_paths.py`** - Utility to fix PDF file paths in database
  - Updates database records with correct file paths
  - Useful after moving PDF files or changing directory structure
  - Usage: `python fix_pdf_paths.py`

## Usage Instructions

### Database Initialization
```bash
# Initialize PostgreSQL schema
python scripts/db_manager.py init

# Check database status
python scripts/db_manager.py status

# Reset database (with confirmation)
python scripts/db_manager.py reset
```

### Development Testing
```bash
# Start mock LLM service for testing
python scripts/mock_llm_service.py

# Debug startup issues
python scripts/debug_startup.py

# Fix PDF paths if needed
python scripts/fix_pdf_paths.py
```

## Docker Integration

These scripts are designed to work within the Docker environment:
- Database scripts use PostgreSQL connection from Docker Compose
- Mock LLM service can substitute for Ollama during development
- Migration scripts run automatically during container startup

## Dependencies

All scripts use the main application dependencies from `requirements.txt`:
- SQLAlchemy for database operations
- psycopg2 for PostgreSQL connectivity
- Flask for mock services
- httpx for HTTP client operations

## Environment Variables

Scripts respect the same environment variables as the main application:
- `DB_URL` - PostgreSQL connection string
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` - Database credentials
- `LLM_SERVICE_URL` - LLM service endpoint for testing
