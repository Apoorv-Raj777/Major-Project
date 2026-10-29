# AI-Powered Multilingual Resume Screening System

A full-stack, production-quality resume screening system with multilingual semantic matching, LinkedIn-based behavioural profiling, and transparent ATS scoring.

## Features

- **Multilingual Support**: Detects and processes resumes in English, Spanish, German, and more
- **Semantic Matching**: Uses sentence-transformers for meaning-based resume-JD matching
- **Behavioural Profiling**: Big Five personality inference from LinkedIn profiles (with consent)
- **Skill Verification**: Cross-checks resume claims against LinkedIn exports
- **Transparent Scoring**: Composite ATS score with semantic, skill, and experience components
- **HR Feedback**: AI-assisted feedback generation using local Ollama LLM
- **Fairness Dashboard**: Tracks multilingual equity metrics

## Tech Stack

### Backend
- Python 3.11 + FastAPI
- PostgreSQL (via docker-compose or Supabase)
- spaCy (NER + parsing)
- sentence-transformers (multilingual embeddings)
- fasttext (language detection)
- argos-translate (offline translation)
- transformers (personality inference)
- Ollama (local LLM for feedback)

### Frontend
- React + Vite
- Tailwind CSS
- Recharts (data visualization)
- Lucide React (icons)

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development without Docker)
- Node.js 18+ (for frontend)

### Using Docker Compose (Recommended)

1. Clone the repository
2. Run:
```bash
docker-compose up --build
```

This will start:
- PostgreSQL database
- FastAPI backend (port 8000)
- Ollama service (port 11434)

3. In a separate terminal, start the frontend:
```bash
cd frontend
npm install
npm run dev
```

4. Access the application:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Local Development (Without Docker)

1. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Download spaCy models
python -m spacy download en_core_web_sm
python -m spacy download xx_ent_wiki_sm

# Download fasttext model
mkdir models
cd models
wget https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin
cd ..

# Set up PostgreSQL (use local or Supabase)
# Update DATABASE_URL in .env

# Run backend
uvicorn main:app --reload
```

2. **Frontend Setup**
```bash
cd frontend
npm install
npm run dev
```

3. **Ollama Setup**
```bash
# Install Ollama from https://ollama.ai
# Pull the model
ollama pull llama3.2:3b
# or
ollama pull phi3:mini

# Start Ollama service
ollama serve
```

## Project Structure

```
├── backend/
│   ├── main.py              # FastAPI application entry point
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── auth.py              # Authentication utilities
│   ├── routers/             # API route handlers
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── jobs.py          # Job CRUD
│   │   ├── resumes.py       # Resume upload & parsing
│   │   ├── matches.py       # ATS scoring
│   │   ├── feedback.py      # HR feedback
│   │   ├── behaviour.py     # LinkedIn & personality
│   │   └── verification.py  # Skill/timeline verification
│   └── services/            # Business logic
│       ├── parsing_service.py        # Resume/JD parsing
│       ├── translation_service.py    # Language detection & translation
│       ├── embedding_service.py      # Semantic embeddings
│       ├── matching_service.py       # ATS scoring
│       ├── personality_service.py   # Big Five inference
│       ├── verification_service.py   # Resume-LinkedIn verification
│       └── llm_service.py            # Ollama integration
├── frontend/
│   ├── src/
│   │   ├── components/      # Reusable components
│   │   ├── contexts/        # React contexts (Auth)
│   │   ├── pages/           # Page components
│   │   │   ├── recruiter/   # Recruiter portal
│   │   │   └── applicant/   # Applicant portal
│   │   ├── App.jsx          # Main app component
│   │   └── main.jsx         # Entry point
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml
└── README.md
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user

### Jobs (Recruiter)
- `POST /api/jobs` - Create job posting
- `GET /api/jobs` - List jobs
- `GET /api/jobs/{id}` - Get job details
- `PUT /api/jobs/{id}` - Update job
- `DELETE /api/jobs/{id}` - Delete job

### Resumes (Applicant)
- `POST /api/resumes/upload` - Upload resume
- `GET /api/resumes` - List user's resumes
- `GET /api/resumes/{id}` - Get resume details

### Matches
- `POST /api/matches/{job_id}/{resume_id}` - Create match
- `GET /api/matches/job/{job_id}` - Get matches for job (recruiter)
- `GET /api/matches/resume/{resume_id}` - Get matches for resume (applicant)

### Behaviour
- `POST /api/behaviour/upload-linkedin` - Upload LinkedIn profile
- `GET /api/behaviour/my-profile` - Get LinkedIn profile
- `GET /api/behaviour/my-personality` - Get personality scores

### Verification
- `POST /api/verification/verify/{match_id}` - Verify resume against LinkedIn

### Feedback
- `POST /api/feedback` - Create feedback
- `GET /api/feedback/job/{job_id}` - Get feedback for job
- `GET /api/feedback/resume/{resume_id}` - Get feedback for resume
- `POST /api/feedback/generate-suggestion/{match_id}` - Generate AI suggestion

## Configuration

### Environment Variables (backend/.env)
```
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Deployment

### Frontend (Vercel)
1. Connect repository to Vercel
2. Set build command: `npm run build`
3. Set output directory: `dist`

### Backend (Render/Railway)
1. Connect repository
2. Set environment variables
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Database (Supabase)
1. Create Supabase project
2. Get connection string
3. Update DATABASE_URL in environment

## License

This project uses only free, open-source, or free-tier tools as specified in the requirements.

## Notes

- All models run locally or on free-tier infrastructure
- No paid APIs are used
- LinkedIn integration uses user-provided PDF exports (no scraping)
- Personality inference requires explicit user consent
- All scoring is transparent and explainable
