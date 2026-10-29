from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import engine, Base
from routers import auth, jobs, resumes, matches, feedback, behaviour, verification, fairness

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup on shutdown
    pass

app = FastAPI(
    title="Resume Screening System API",
    description="AI-powered multilingual resume screening with behavioural profiling",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(resumes.router, prefix="/api/resumes", tags=["resumes"])
app.include_router(matches.router, prefix="/api/matches", tags=["matches"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["feedback"])
app.include_router(behaviour.router, prefix="/api/behaviour", tags=["behaviour"])
app.include_router(verification.router, prefix="/api/verification", tags=["verification"])
app.include_router(fairness.router, prefix="/api/fairness", tags=["fairness"])

@app.get("/")
async def root():
    return {"message": "Resume Screening System API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
