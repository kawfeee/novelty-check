# Deploy Novelty Score API to Render

Complete guide to deploy your API on Render and use it in your MERN project.

---

## 🚀 Step 1: Prepare Your Repository

### 1.1 Push to GitHub

```powershell
# Initialize git (if not already done)
cd C:\Users\kaifa\OneDrive\Desktop\work\novelty-check
git init
git add .
git commit -m "Initial commit - Novelty Score API"

# Create a new repository on GitHub (https://github.com/new)
# Then push your code
git remote add origin https://github.com/YOUR_USERNAME/novelty-check.git
git branch -M main
git push -u origin main
```

### 1.2 Verify Files

Ensure these files exist:
- ✅ `backend/requirements.txt`
- ✅ `backend/main.py`
- ✅ `render.yaml` (created)
- ✅ `.gitignore` (created)

---

## 🗄️ Step 2: Set Up PostgreSQL Database on Render

### 2.1 Create PostgreSQL Database

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `novelty-db`
   - **Database**: `novelty_db`
   - **User**: `novelty_user` (auto-generated)
   - **Region**: Same as your API (e.g., Oregon)
   - **Plan**: **Free** (or Starter for production)
4. Click **"Create Database"**

### 2.2 Install pgvector Extension

1. After database is created, go to **"Info"** tab
2. Copy the **PSQL Command** (looks like: `PGPASSWORD=xxx psql -h xxx.render.com -U novelty_user novelty_db`)
3. Run in your local terminal:

```powershell
# Use the PSQL command from Render
PGPASSWORD=your_password psql -h your-host.render.com -U novelty_user novelty_db

# Then run in psql:
CREATE EXTENSION IF NOT EXISTS vector;
\q
```

**Alternative**: Use Render's Shell feature:
- Go to database → **"Shell"** tab
- Run: `CREATE EXTENSION IF NOT EXISTS vector;`

### 2.3 Run Migrations

```powershell
# Set environment variable with your Render database URL
$env:PGPASSWORD='your_render_db_password'

# Run migrations
psql -h your-host.render.com -U novelty_user -d novelty_db -f backend/migrations/001_init.sql
psql -h your-host.render.com -U novelty_user -d novelty_db -f backend/migrations/002_refactor_for_api.sql
```

### 2.4 Copy Database URL

1. In Render Dashboard → Your Database → **"Info"** tab
2. Copy **"Internal Database URL"** (starts with `postgresql://`)
3. Save it for Step 3

---

## 🌐 Step 3: Deploy API on Render

### 3.1 Create Web Service

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository:
   - Click **"Connect account"** if needed
   - Select **"novelty-check"** repository

### 3.2 Configure Web Service

**Basic Settings:**
- **Name**: `novelty-score-api`
- **Region**: Same as database (e.g., Oregon)
- **Branch**: `main` (or `master`)
- **Root Directory**: Leave blank
- **Environment**: **Python 3**
- **Build Command**: 
  ```bash
  pip install -r backend/requirements.txt
  ```
- **Start Command**: 
  ```bash
  cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
  ```

**Plan:**
- Select **Free** (good for testing) or **Starter** ($7/month for production)

### 3.3 Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**

Add these variables:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | `postgresql://novelty_user:PASSWORD@HOST/novelty_db` (from Step 2.4) |
| `PYTHON_VERSION` | `3.11.0` |
| `EMBEDDING_MODEL` | `all-mpnet-base-v2` |

**Important**: Use the **Internal Database URL** from Render for faster connections.

### 3.4 Deploy

1. Click **"Create Web Service"**
2. Wait 5-10 minutes for first deployment (downloads ML model ~420MB)
3. Monitor logs in **"Logs"** tab

### 3.5 Verify Deployment

Once deployed, your API will be at:
```
https://novelty-score-api.onrender.com
```

Test endpoints:
- Health: `https://novelty-score-api.onrender.com/health`
- Docs: `https://novelty-score-api.onrender.com/docs`
- Root: `https://novelty-score-api.onrender.com/`

---

## 🔧 Step 4: Update API for Production

### 4.1 Update CORS for Your MERN Frontend

Edit `backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "http://localhost:5173",  # Vite dev server
        "https://your-frontend-app.vercel.app",  # Your deployed frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Push changes:
```powershell
git add .
git commit -m "Update CORS for production"
git push
```

Render will auto-deploy.

### 4.2 Update Port Configuration

Edit `backend/main.py` - change the last line:

```python
if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
```

---

## 🌐 Step 5: Use API in Your MERN Project

### 5.1 Frontend Integration (React)

Create an API client file: `src/services/noveltyApi.js`

```javascript
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://novelty-score-api.onrender.com';

export const checkNovelty = async (applicationNumber, extractedText) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/novelty-check`, {
      application_number: applicationNumber,
      extracted_text: extractedText
    });
    return response.data;
  } catch (error) {
    console.error('Error checking novelty:', error);
    throw error;
  }
};

export const getHealth = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/health`);
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};
```

### 5.2 Environment Variables (React)

Create `.env` in your React project root:

```env
REACT_APP_API_URL=https://novelty-score-api.onrender.com
```

For Vite projects, use:
```env
VITE_API_URL=https://novelty-score-api.onrender.com
```

### 5.3 Usage Example (React Component)

```javascript
import React, { useState } from 'react';
import { checkNovelty } from './services/noveltyApi';

function NoveltyChecker() {
  const [appNumber, setAppNumber] = useState('');
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const data = await checkNovelty(appNumber, text);
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to check novelty');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="novelty-checker">
      <h2>Novelty Score Checker</h2>
      
      <form onSubmit={handleSubmit}>
        <div>
          <label>Application Number:</label>
          <input
            type="text"
            value={appNumber}
            onChange={(e) => setAppNumber(e.target.value)}
            placeholder="APP-2024-001"
            required
          />
        </div>
        
        <div>
          <label>Proposal Text:</label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Enter your proposal text..."
            rows="10"
            required
          />
        </div>
        
        <button type="submit" disabled={loading}>
          {loading ? 'Analyzing...' : 'Check Novelty'}
        </button>
      </form>
      
      {error && (
        <div className="error">
          <p>Error: {error}</p>
        </div>
      )}
      
      {result && (
        <div className="result">
          <h3>Results</h3>
          <p><strong>Application:</strong> {result.application_number}</p>
          <p><strong>Novelty Score:</strong> {result.novelty_score.toFixed(2)}%</p>
          <p><strong>Total Proposals Checked:</strong> {result.total_proposals_checked}</p>
          
          {result.similar_proposals.length > 0 && (
            <div>
              <h4>Similar Proposals:</h4>
              <ul>
                {result.similar_proposals.map((p, idx) => (
                  <li key={idx}>
                    {p.application_number} - {p.similarity_percentage.toFixed(2)}% similar
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default NoveltyChecker;
```

### 5.4 Node.js/Express Backend Integration

If using Node.js backend in your MERN stack:

```javascript
const axios = require('axios');

const NOVELTY_API_URL = process.env.NOVELTY_API_URL || 'https://novelty-score-api.onrender.com';

// Route in your Express app
app.post('/api/check-novelty', async (req, res) => {
  try {
    const { applicationNumber, extractedText } = req.body;
    
    const response = await axios.post(`${NOVELTY_API_URL}/api/novelty-check`, {
      application_number: applicationNumber,
      extracted_text: extractedText
    });
    
    res.json(response.data);
  } catch (error) {
    console.error('Novelty check error:', error);
    res.status(500).json({ 
      error: 'Failed to check novelty',
      details: error.response?.data 
    });
  }
});
```

---

## ⚠️ Important Notes

### Free Tier Limitations

**Render Free Tier:**
- ✅ 750 hours/month (enough for one service)
- ⚠️ Spins down after 15 minutes of inactivity
- ⚠️ First request after spin-down takes ~30-60 seconds (cold start + model loading)
- ✅ 512MB RAM (sufficient for this API)

**PostgreSQL Free Tier:**
- ✅ 1GB storage
- ✅ 100 connections
- ⚠️ Expires after 90 days (need to upgrade or migrate)

### Handling Cold Starts

Add this to your React app to warm up the API:

```javascript
// src/hooks/useApiWarmup.js
import { useEffect } from 'react';
import { getHealth } from '../services/noveltyApi';

export const useApiWarmup = () => {
  useEffect(() => {
    // Ping API on app load to wake it up
    getHealth().catch(err => console.log('Warmup ping failed:', err));
  }, []);
};

// Use in App.js
function App() {
  useApiWarmup();
  // ... rest of your app
}
```

### Performance Optimization

1. **Show Loading State**: First request after cold start takes 30-60 seconds
2. **Cache Results**: Store recent checks in frontend state/localStorage
3. **Batch Requests**: If checking multiple proposals, consider queuing
4. **Upgrade Plan**: For production, use Starter plan ($7/month) - no cold starts

---

## 🔒 Security Checklist

- [ ] Update CORS to only allow your frontend domain
- [ ] Use environment variables for all sensitive data
- [ ] Enable HTTPS (automatic on Render)
- [ ] Consider adding API key authentication for production
- [ ] Set rate limiting if needed
- [ ] Monitor usage in Render dashboard

---

## 🧪 Testing Your Deployed API

### cURL Test

```bash
curl -X POST "https://novelty-score-api.onrender.com/api/novelty-check" \
  -H "Content-Type: application/json" \
  -d '{
    "application_number": "APP-2024-TEST",
    "extracted_text": "This is a test proposal for quantum computing applications in drug discovery using advanced machine learning techniques and molecular simulation optimization."
  }'
```

### Postman Test

1. Create new POST request
2. URL: `https://novelty-score-api.onrender.com/api/novelty-check`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON):
```json
{
  "application_number": "APP-2024-TEST",
  "extracted_text": "Your proposal text here..."
}
```

---

## 📊 Monitoring

**Render Dashboard:**
- Monitor CPU/Memory usage
- View logs in real-time
- Check deployment status
- Track API requests

**Database Dashboard:**
- Monitor database size
- Check connection count
- View query performance

---

## 🚨 Troubleshooting

### Issue: API returns 503 after cold start
**Solution**: Wait 30-60 seconds for model loading. Consider upgrading to Starter plan.

### Issue: Database connection failed
**Solution**: Verify DATABASE_URL is correct (use Internal URL, not External).

### Issue: CORS errors from frontend
**Solution**: Add your frontend URL to `allow_origins` in `main.py`.

### Issue: Model download fails
**Solution**: Render Free tier has 512MB RAM limit. Model is ~420MB - should fit, but close.

### Issue: 90-day database expiry warning
**Solution**: Upgrade to Starter plan ($7/month) or migrate to another database provider.

---

## 🎯 Your API URL

After deployment, your API will be available at:

```
https://novelty-score-api.onrender.com
```

Update this in your MERN project's environment variables!

---

**Need Help?**
- Render Docs: https://render.com/docs
- Render Support: https://render.com/support
- Check logs in Render Dashboard → Your Service → Logs
