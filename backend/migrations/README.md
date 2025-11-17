# Database Setup Instructions

## Prerequisites
- PostgreSQL 12 or higher installed
- pgvector extension

## Step 1: Install pgvector

### On Windows (using scoop or from source):
```powershell
# Using scoop
scoop install pgvector

# OR download from: https://github.com/pgvector/pgvector/releases
# Extract and follow Windows installation instructions
```

### On Linux/Mac:
```bash
# Ubuntu/Debian
sudo apt install postgresql-15-pgvector

# macOS with Homebrew
brew install pgvector
```

## Step 2: Create Database

```sql
-- Connect to PostgreSQL as superuser
psql -U postgres

-- Create database
CREATE DATABASE novelty_db;

-- Connect to the database
\c novelty_db

-- Enable pgvector extension
CREATE EXTENSION vector;
```

## Step 3: Run Migrations

```powershell
# Navigate to backend directory
cd backend

# Run the migration script
psql -U postgres -d novelty_db -f migrations/001_init.sql
```

## Step 4: Verify Installation

```sql
-- Connect to database
psql -U postgres -d novelty_db

-- Check if pgvector is installed
\dx

-- Verify table creation
\dt

-- Check table structure
\d proposals
```

## Connection String Format

```
postgresql://username:password@host:port/database_name

Example:
postgresql://postgres:postgres@localhost:5432/novelty_db
```

## Troubleshooting

### pgvector not found
- Ensure pgvector is installed for your PostgreSQL version
- Check PostgreSQL version: `psql --version`
- Download compatible pgvector version

### Permission denied
- Run migrations as PostgreSQL superuser
- Grant appropriate permissions to application user

### Connection refused
- Verify PostgreSQL service is running
- Check connection parameters in .env file
