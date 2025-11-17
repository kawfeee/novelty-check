# Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### 1. Database Setup (2 minutes)

```powershell
# Create database
psql -U postgres -c "CREATE DATABASE novelty_db;"

# Enable pgvector and run migrations
psql -U postgres -d novelty_db -c "CREATE EXTENSION vector;"
psql -U postgres -d novelty_db -f backend/migrations/001_init.sql
```

### 2. Backend Setup (1 minute)

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Edit .env with your database credentials
```

### 3. Frontend Setup (1 minute)

```powershell
cd ..\frontend
npm install
Copy-Item .env.example .env
```

### 4. Run the Application (1 minute)

**Terminal 1 - Backend
cd backend
.\venv\Scripts\Activate.ps1
python main.py
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

### 5. Access the Application

- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs

## 📝 First Steps

1. **Ingest a Proposal**
   - Go to "Ingest Proposal" page
   - Upload a PDF or DOCX file
   - Click "Ingest Proposal"

2. **Check Novelty**
   - Go to "Check Novelty" page
   - Either paste text or upload a file
   - Click "Check Novelty"
   - View your novelty score and similar proposals

## 🔧 Troubleshooting

### Database Connection Error
```powershell
# Check PostgreSQL is running
Get-Service postgresql*

# If not running, start it
Start-Service postgresql-x64-15  # Adjust version number
```

### Port Already in Use
```powershell
# Backend (port 8000)
netstat -ano | findstr :8000

# Frontend (port 5173)
netstat -ano | findstr :5173

# Kill process if needed
taskkill /PID <PID> /F
```

### Module Not Found Errors
```powershell
# Backend
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

## 📚 Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [API documentation](http://localhost:8000/docs) for endpoint details
- Review [database migrations](backend/migrations/README.md) for schema details
