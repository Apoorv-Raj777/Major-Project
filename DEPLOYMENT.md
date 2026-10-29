# Deployment Guide

This guide covers deploying the Resume Screening System to free-tier infrastructure.

## Prerequisites

- Accounts on Vercel, Render (or Railway), and Supabase
- Git repository with your code

## Database Setup (Supabase)

1. **Create Supabase Project**
   - Go to [supabase.com](https://supabase.com)
   - Create a new project
   - Wait for the database to be ready

2. **Get Connection String**
   - Go to Project Settings → Database
   - Copy the connection string (URI format)
   - Format: `postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres`

3. **Set Environment Variables**
   - Save the connection string for Render deployment

## Backend Deployment (Render)

### Option 1: Using Render Dashboard

1. **Create New Web Service**
   - Go to Render Dashboard
   - Click "New +" → "Web Service"
   - Connect your Git repository
   - Select the `backend` folder as root directory

2. **Configure Build & Runtime**
   - **Build Command**: `pip install -r requirements.txt && python -m spacy download en_core_web_sm && python -m spacy download xx_ent_wiki_sm`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Runtime**: Python 3.11

3. **Set Environment Variables**
   ```
   DATABASE_URL=your-supabase-connection-string
   SECRET_KEY=generate-with-openssl-rand-hex-32
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

4. **Deploy**
   - Click "Deploy Web Service"
   - Wait for build to complete
   - Copy the backend URL (e.g., `https://resume-screening-backend.onrender.com`)

### Option 2: Using render.yaml

1. Push the `render.yaml` file to your repository
2. Connect your repository to Render
3. Render will automatically detect and use the configuration

## Frontend Deployment (Vercel)

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Deploy Frontend**
   ```bash
   cd frontend
   vercel
   ```
   - Follow the prompts
   - Set environment variable: `VITE_API_URL=https://your-backend-url.onrender.com`

3. **Or Use Vercel Dashboard**
   - Go to [vercel.com](https://vercel.com)
   - Import your repository
   - Select the `frontend` folder as root directory
   - Add environment variable: `VITE_API_URL`
   - Deploy

## Alternative: Railway Deployment

Railway is another free-tier option that's simpler for full-stack apps:

1. **Create Railway Project**
   ```bash
   npm install -g railway
   railway login
   railway init
   ```

2. **Add Services**
   ```bash
   # Add PostgreSQL
   railway add postgresql
   
   # Add backend
   railway add --service-name backend
   
   # Add frontend (as static site)
   railway add --service-name frontend
   ```

3. **Configure Environment Variables**
   ```bash
   railway variables set DATABASE_URL=$POSTGRES_URL
   railway variables set SECRET_KEY=your-secret-key
   ```

4. **Deploy**
   ```bash
   railway up
   railway deploy
   ```

## Post-Deployment Setup

### 1. Initialize Database Tables

The FastAPI app will auto-create tables on first startup, but you can also run:

```bash
# SSH into your Render service
# Or use the Render shell
python -c "from database import engine, Base; Base.metadata.create_all(bind=engine)"
```

### 2. Download ML Models (if not in Docker)

If not using Docker, models need to be downloaded:

```bash
# On the backend server
python -m spacy download en_core_web_sm
python -m spacy download xx_ent_wiki_sm
mkdir models
cd models
wget https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin
```

### 3. Configure Ollama (Optional)

For LLM-assisted feedback, you need Ollama running:

- **Local development**: Run `ollama serve` locally
- **Production**: Consider using a separate service or alternative free LLM API

### 4. Update Frontend API URL

Ensure the frontend points to the correct backend URL:

```javascript
// frontend/src/api.js or update in individual components
const API_URL = import.meta.env.VITE_API_URL || 'https://your-backend.onrender.com'
```

## Testing the Deployment

1. **Health Check**
   - Backend: `https://your-backend.onrender.com/health`
   - Should return: `{"status": "healthy"}`

2. **API Documentation**
   - Backend: `https://your-backend.onrender.com/docs`
   - Test endpoints via Swagger UI

3. **Frontend**
   - Visit your Vercel URL
   - Try registering and logging in
   - Test resume upload and job creation

## Troubleshooting

### Backend Issues

**Build fails on spaCy download:**
- Use the Docker deployment instead
- Or pre-download models and commit to repo (not recommended)

**Database connection errors:**
- Verify DATABASE_URL is correct
- Check Supabase project status
- Ensure IP whitelisting is configured (if needed)

### Frontend Issues

**CORS errors:**
- Update backend CORS middleware to include your Vercel domain
- Check `main.py` CORS configuration

**API calls failing:**
- Verify VITE_API_URL is set correctly
- Check browser console for errors
- Ensure backend is running

### Free Tier Limitations

**Render:**
- 750 hours/month free
- Services spin down after 15 min inactivity
- Cold starts may take 30-60 seconds

**Supabase:**
- 500MB database free
- 1GB bandwidth free
- May need to upgrade for production use

**Vercel:**
- Unlimited deployments for hobby plan
- 100GB bandwidth free
- Functions have execution time limits

## Production Considerations

For a production deployment, consider:

1. **Upgrade to paid tiers** for better performance and reliability
2. **Add monitoring** (Sentry for errors, LogRocket for user sessions)
3. **Implement rate limiting** on API endpoints
4. **Add CDN** for static assets
5. **Use managed ML services** instead of local models
6. **Implement proper backup strategy** for database
7. **Add SSL certificates** (usually provided by platforms)
8. **Configure proper logging** and log aggregation

## Local Development with Production Database

To test locally against production database:

```bash
# Set DATABASE_URL to Supabase connection string
export DATABASE_URL="postgresql://postgres:[password]@db.[ref].supabase.co:5432/postgres"

# Run backend locally
cd backend
uvicorn main:app --reload
```

## Cost Summary (Free Tiers)

- **Supabase**: Free (500MB DB, 1GB bandwidth)
- **Render**: Free (750 hours/month)
- **Vercel**: Free (unlimited deployments, 100GB bandwidth)
- **Total**: $0/month for MVP/demo purposes
