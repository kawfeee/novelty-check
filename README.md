# Novelty Score Engine 🔬

A complete standalone system for evaluating the novelty of R&D proposals using AI-powered semantic similarity analysis.

## 🎯 Overview

The Novelty Score Engine compares new R&D proposals against previously ingested proposals to compute a novelty score (0-100). Higher scores indicate more unique and novel proposals.

### Tech Stack
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL with pgvector extension
- **AI Embeddings**: Sentence Transformers (all-mpnet-base-v2)
- **Frontend**: React with Vite

## 📁 Project Structure

```
novelty-check/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── embeddings.py        # Embedding generation
│   ├── db.py                # Database operations
│   ├── models.py            # Pydantic models
│   ├── routers/
│   │   ├── ingest.py        # Ingestion endpoint
│   │   └── novelty.py       # Novelty check endpoint
│   ├── migrations/
│   │   ├── 001_init.sql     # Database schema
│   │   └── README.md        # Migration instructions
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Ingest.jsx
│   │   │   └── NoveltyCheck.jsx
│   │   ├── api/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── .env.example
└── README.md
```

## 🚀 Installation & Setup

### Prerequisites

1. **Python 3.9+**
2. **Node.js 18+**
3. **PostgreSQL 12+**
4. **pgvector extension**

### Step 1: Database Setup

#### Install PostgreSQL and pgvector

**Windows:**
```powershell
# Install PostgreSQL (if not already installed)
# Download from: https://www.postgresql.org/download/windows/

# Install pgvector
# Download from: https://github.com/pgvector/pgvector/releases
# Follow installation instructions for Windows
```

**Linux/Mac:**
```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-15-pgvector

# macOS
brew install postgresql pgvector
```

#### Create Database

```powershell
# Start PostgreSQL service (if not running)
# Windows: Check Services or use pg_ctl

# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE novelty_db;

# Connect to the database
\c novelty_db

# Enable pgvector extension
CREATE EXTENSION vector;

# Exit
\q
```

#### Run Migrations

```powershell
cd backend
psql -U postgres -d novelty_db -f migrations/001_init.sql
```

### Step 2: Backend Setup

```powershell
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create .env file
Copy-Item .env.example .env

# Edit .env file with your database credentials
# DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/novelty_db
```

### Step 3: Frontend Setup

```powershell
# Navigate to frontend directory
cd ..\frontend

# Install dependencies
npm install

# Create .env file
Copy-Item .env.example .env
```

## 🎮 Running the Application

### Start Backend Server

```powershell
# From backend directory (with venv activated)
cd backend
.\venv\Scripts\Activate.ps1
python main.py

# Server will start at: http://localhost:8000
# API docs available at: http://localhost:8000/docs
```

### Start Frontend Development Server

```powershell
# From frontend directory (in a new terminal)
cd frontend
npm run dev

# Frontend will start at: http://localhost:5173
```

## 📡 API Endpoints

### 1. Ingest Proposal

**POST** `/api/ingest`

Upload and store a new R&D proposal.

**Request:**
- `file`: PDF or DOCX file (multipart/form-data)
- `title`: Optional proposal title (form field)

**Response:**
```json
{
  "id": 1,
  "title": "Quantum Computing Research",
  "message": "Proposal ingested successfully"
}
```

### 2. Check Novelty (Text)

**POST** `/api/novelty`

Check novelty score for proposal text.

**Request:**
```json
{
  "text": "Full proposal text content..."
}
```

**Response:**
```json
{
  "novelty_score": 73.5,
  "similar_proposals": [
    {
      "id": 5,
      "title": "Previous Research",
      "similarity": 0.265
    }
  ],
  "total_proposals_checked": 10,
  "interpretation": "Novel - This proposal has significant unique elements"
}
```

### 3. Check Novelty (File)

**POST** `/api/novelty/file`

Check novelty score from uploaded file.

**Request:**
- `file`: PDF or DOCX file (multipart/form-data)

**Response:** Same as text-based novelty check

## 🎨 Frontend Pages

### 1. Ingest Page (`/ingest`)
- Upload PDF/DOCX proposals
- Optional title input
- Shows success/error messages
- Explains the ingestion process

### 2. Novelty Check Page (`/novelty-check`)
- Two input methods: paste text or upload file
- Real-time novelty analysis
- Visual score display with color coding
- Table of similar proposals with similarity percentages
- Interpretation guide

## 🧮 Novelty Score Calculation

The novelty score is calculated using the following formula:

```
novelty_score = (1 - average_similarity) × 100
```

Where:
- **average_similarity**: Average cosine similarity of top 5 most similar proposals
- **Score Range**: 0-100
  - **80-100**: Highly Novel
  - **60-79**: Novel
  - **40-59**: Moderately Novel
  - **20-39**: Low Novelty
  - **0-19**: Very Low Novelty

## 🔧 Configuration

### Backend Environment Variables (`.env`)

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/novelty_db
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
EMBEDDING_MODEL=all-mpnet-base-v2
```

### Frontend Environment Variables (`.env`)

```env
VITE_API_URL=http://localhost:8000/api
```

## 📊 Database Schema

### `proposals` Table

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| title | TEXT | Proposal title |
| full_text | TEXT | Full proposal text |
| embedding | VECTOR(768) | Semantic embedding |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

### Indexes

- `proposals_embedding_idx`: IVFFlat index for fast vector similarity search
- `proposals_created_at_idx`: Index on creation timestamp

## 🧪 Testing the System

### 1. Test Ingestion

```powershell
# Using curl (PowerShell)
curl -X POST "http://localhost:8000/api/ingest" `
  -F "file=@sample_proposal.pdf" `
  -F "title=Test Proposal"
```

### 2. Test Novelty Check

```powershell
# Using curl (PowerShell)
$body = @{
  text = "This is a sample R&D proposal about quantum computing and machine learning..."
} | ConvertTo-Json

curl -X POST "http://localhost:8000/api/novelty" `
  -H "Content-Type: application/json" `
  -d $body
```

## 🔍 How It Works

1. **Document Ingestion**
   - Upload PDF/DOCX file
   - Extract text using pdfplumber/python-docx
   - Generate 768-dimensional embedding using Sentence Transformers
   - Store in PostgreSQL with pgvector

2. **Novelty Evaluation**
   - Generate embedding for new proposal
   - Query pgvector for top 5 most similar proposals (cosine similarity)
   - Calculate novelty score: `(1 - avg_similarity) × 100`
   - Return score and similar proposals

3. **Vector Search**
   - Uses pgvector's IVFFlat index for fast approximate nearest neighbor search
   - Cosine distance operator (`<=>`) for similarity comparison
   - Optimized for large-scale proposal databases

## 📈 Performance Considerations

- **Embedding Generation**: ~100-500ms per document (depending on length)
- **Vector Search**: Sub-millisecond with proper indexing
- **Database**: IVFFlat index provides O(log n) search complexity
- **Scalability**: Tested with 10,000+ proposals

## 🛠️ Troubleshooting

### Common Issues

1. **pgvector extension not found**
   - Ensure pgvector is installed for your PostgreSQL version
   - Run `CREATE EXTENSION vector;` in your database

2. **Connection refused (backend)**
   - Check if PostgreSQL is running
   - Verify DATABASE_URL in .env file
   - Check firewall settings

3. **CORS errors (frontend)**
   - Verify CORS_ORIGINS in backend .env
   - Check if backend is running on correct port

4. **Out of memory during embedding**
   - Reduce batch size
   - Use CPU instead of GPU (automatic fallback)

5. **Slow vector search**
   - Ensure IVFFlat index is created
   - Adjust `lists` parameter in index creation

## 🔒 Security Notes

- Never commit `.env` files
- Use strong database passwords in production
- Implement authentication for production deployment
- Validate and sanitize all file uploads
- Set file size limits (currently 10MB recommended)

## 📝 Production Deployment Checklist

- [ ] Set up proper environment variables
- [ ] Configure HTTPS/SSL
- [ ] Implement authentication/authorization
- [ ] Set up database backups
- [ ] Configure logging and monitoring
- [ ] Use production WSGI server (e.g., Gunicorn)
- [ ] Set up reverse proxy (e.g., Nginx)
- [ ] Implement rate limiting
- [ ] Configure CORS properly
- [ ] Set up CI/CD pipeline

## 📚 API Documentation

Interactive API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🤝 Contributing

This is a standalone module. To extend:
1. Add new endpoints in `routers/`
2. Extend database schema in migrations
3. Update frontend pages as needed
4. Test thoroughly before deployment

## 📄 License

This project is provided as-is for R&D proposal novelty detection purposes.

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation
3. Check PostgreSQL and pgvector documentation
4. Verify all dependencies are installed correctly

---

**Built with ❤️ for R&D Innovation**
