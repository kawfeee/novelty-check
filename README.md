# Novelty Score API

**API-only microservice for R&D proposal novelty detection**

Version: 2.0.0

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL 12+ with pgvector extension
- Virtual environment

### Installation

```powershell
# 1. Navigate to backend directory
cd backend

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment (Windows)
.\venv\Scripts\Activate.ps1

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure environment variables
Copy-Item .env.example .env
# Edit .env with your database credentials
```

### Environment Variables

Create a `.env` file in the backend directory:

```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/novelty_db
HOST=0.0.0.0
PORT=8000
EMBEDDING_MODEL=all-mpnet-base-v2
```

### Database Setup

```powershell
# Run migrations
$env:PGPASSWORD='your_password'
psql -U postgres -d novelty_db -f migrations/001_init.sql
psql -U postgres -d novelty_db -f migrations/002_refactor_for_api.sql
```

### Run the API

```powershell
# Development mode (with auto-reload)
python main.py

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

Interactive docs: `http://localhost:8000/docs`

---

## 📡 API Endpoint

### POST `/api/novelty-check`

Check novelty score for a proposal and store it in the database.

**Request Body:**

```json
{
  "application_number": "APP-2024-001",
  "extracted_text": "This is the full text content of the R&D proposal..."
}
```

**Response:**

```json
{
  "application_number": "APP-2024-001",
  "novelty_score": 82.5,
  "total_proposals_checked": 134,
  "similar_proposals": ["APP-2023-042", "APP-2023-156"]
}
```

**Fields:**
- `application_number` (string): Unique application identifier
- `extracted_text` (string): Full text content (minimum 10 characters)
- `novelty_score` (float): Novelty score from 0-100 (higher = more novel)
- `total_proposals_checked` (int): Total number of proposals in database
- `similar_proposals` (array): List of application numbers for most similar proposals

---

## 💻 Usage Examples

### cURL

```bash
curl -X POST "http://localhost:8000/api/novelty-check" \
  -H "Content-Type: application/json" \
  -d '{
    "application_number": "APP-2024-001",
    "extracted_text": "We propose a novel quantum computing approach using superconducting qubits to solve complex optimization problems in drug discovery and molecular simulation. Our method leverages advanced error correction techniques..."
  }'
```

### Node.js (axios)

```javascript
const axios = require('axios');

async function checkNovelty(applicationNumber, extractedText) {
  try {
    const response = await axios.post('http://localhost:8000/api/novelty-check', {
      application_number: applicationNumber,
      extracted_text: extractedText
    });
    
    console.log('Novelty Score:', response.data.novelty_score);
    console.log('Total Proposals Checked:', response.data.total_proposals_checked);
    console.log('Similar Proposals:', response.data.similar_proposals);
    
    return response.data;
  } catch (error) {
    console.error('Error checking novelty:', error.response?.data || error.message);
    throw error;
  }
}

// Usage
checkNovelty(
  'APP-2024-001',
  'Full proposal text content here...'
).then(result => {
  console.log('Result:', result);
});
```

### Node.js (fetch)

```javascript
async function checkNovelty(applicationNumber, extractedText) {
  const response = await fetch('http://localhost:8000/api/novelty-check', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      application_number: applicationNumber,
      extracted_text: extractedText
    })
  });
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  const data = await response.json();
  return data;
}

// Usage
checkNovelty('APP-2024-001', 'Proposal text...')
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));
```

### Python (requests)

```python
import requests

def check_novelty(application_number: str, extracted_text: str) -> dict:
    url = "http://localhost:8000/api/novelty-check"
    
    payload = {
        "application_number": application_number,
        "extracted_text": extracted_text
    }
    
    response = requests.post(url, json=payload)
    response.raise_for_status()
    
    return response.json()

# Usage
result = check_novelty(
    "APP-2024-001",
    "Full proposal text content here..."
)

print(f"Novelty Score: {result['novelty_score']}")
print(f"Similar Proposals: {result['similar_proposals']}")
```

---

## 🔧 How It Works

1. **Input**: Accepts `application_number` and `extracted_text`
2. **Embedding**: Generates 768-dimensional semantic embedding using Sentence Transformers (all-mpnet-base-v2)
3. **Storage**: Stores (or updates) the proposal in PostgreSQL with pgvector
4. **Similarity**: Queries pgvector to find top 5 most similar proposals using cosine distance
5. **Score**: Calculates novelty score: `(1 - average_similarity) × 100`
6. **Response**: Returns novelty score and list of similar application numbers

**Novelty Score Interpretation:**
- **80-100**: Highly Novel
- **60-79**: Novel
- **40-59**: Moderately Novel
- **20-39**: Low Novelty
- **0-19**: Very Low Novelty

---

## 📊 Database Schema

### `proposals` table

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| application_number | TEXT | Unique application identifier |
| extracted_text | TEXT | Full proposal text |
| embedding | VECTOR(768) | Semantic embedding |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

**Indexes:**
- `unique_application_number`: Unique constraint on application_number
- `idx_application_number`: B-tree index for fast lookups
- `proposals_embedding_idx`: IVFFlat index for vector similarity search

---

## 🐳 Docker Deployment (Optional)

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  postgres:
    image: ankane/pgvector
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: novelty_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  api:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/novelty_db
    ports:
      - "8000:8000"
    depends_on:
      - postgres

volumes:
  postgres_data:
```

**Run with Docker:**

```bash
docker-compose up -d
```

---

## 🔒 Production Considerations

1. **Security:**
   - Use environment variables for sensitive data
   - Implement authentication/authorization if needed
   - Configure CORS appropriately
   - Use HTTPS in production

2. **Performance:**
   - The first model load takes ~1-2 minutes (downloads 420MB)
   - Subsequent requests are fast (~100-500ms)
   - Consider using Gunicorn with multiple workers

3. **Scaling:**
   - Database connection pool is configured (min: 2, max: 10)
   - pgvector IVFFlat index provides O(log n) search
   - Can handle 1000+ proposals efficiently

4. **Monitoring:**
   - Check `/health` endpoint for service status
   - Monitor database connection pool
   - Log embedding generation times

---

## 🆘 Troubleshooting

### pgvector not found
```bash
# Ensure pgvector is installed in PostgreSQL
psql -U postgres -d novelty_db -c "CREATE EXTENSION vector;"
```

### Connection refused
```bash
# Check if database is running
pg_isready -h localhost -p 5432

# Verify DATABASE_URL in .env
```

### Model download fails
```bash
# The model will download automatically on first run
# Ensure internet connection and ~500MB free space
```

### Import errors
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

---

## 📝 API Response Codes

- `200 OK`: Successful novelty check
- `400 Bad Request`: Invalid input (missing fields, text too short)
- `500 Internal Server Error`: Server-side error (database, embedding generation)

---

## 🎯 Project Structure

```
novelty-check/
├── backend/
│   ├── main.py              # FastAPI application entry point
│   ├── models.py            # Pydantic models for request/response
│   ├── db.py                # Database operations
│   ├── embeddings.py        # Embedding generation logic
│   ├── routers/
│   │   ├── __init__.py
│   │   └── novelty_check.py # Novelty check endpoint
│   ├── migrations/
│   │   ├── 001_init.sql
│   │   └── 002_refactor_for_api.sql
│   ├── requirements.txt
│   ├── .env.example
│   └── .env
└── README.md
```

---

## 📚 Dependencies

- **FastAPI**: Modern web framework for APIs
- **Uvicorn**: ASGI server
- **asyncpg**: Async PostgreSQL driver
- **sentence-transformers**: AI embeddings (all-mpnet-base-v2 model)
- **python-dotenv**: Environment variable management
- **pydantic**: Data validation

---

**Built with ❤️ for R&D Innovation**
