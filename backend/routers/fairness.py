from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from database import get_db
from models import Match, Resume, Job, User, FairnessMetrics
from auth import get_current_user, get_current_recruiter
from datetime import datetime

router = APIRouter()

@router.get("/dashboard")
async def get_fairness_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get fairness metrics dashboard showing multilingual equity
    """
    # Get all matches with resume language and scores
    query = db.query(
        Resume.language,
        func.avg(Match.ats_score).label('avg_ats_score'),
        func.count(Match.id).label('total_resumes')
    ).join(
        Match, Resume.id == Match.resume_id
    ).group_by(
        Resume.language
    ).all()
    
    metrics = []
    for lang, avg_score, total in query:
        # Count shortlisted separately
        shortlisted_query = db.query(Match).join(
            Resume, Match.resume_id == Resume.id
        ).filter(
            Resume.language == lang,
            Match.ats_score >= 0.7
        ).count()
        
        shortlisted = shortlisted_query
        shortlist_rate = (shortlisted / total) if total > 0 else 0.0
        
        metrics.append({
            "language_code": lang or "unknown",
            "average_ats_score": float(avg_score) if avg_score else 0.0,
            "total_resumes": total,
            "shortlisted_count": shortlisted,
            "shortlist_rate": shortlist_rate
        })
    
    # Calculate overall statistics
    overall_query = db.query(
        func.avg(Match.ats_score).label('overall_avg'),
        func.count(Match.id).label('overall_total')
    ).first()
    
    overall_avg = float(overall_query.overall_avg) if overall_query.overall_avg else 0.0
    overall_total = overall_query.overall_total
    
    # Check for statistical parity (from paper #5)
    # Compare shortlist rates across languages
    if metrics:
        shortlist_rates = [m["shortlist_rate"] for m in metrics]
        max_rate = max(shortlist_rates)
        min_rate = min(shortlist_rates)
        rate_disparity = max_rate - min_rate
        
        # Flag if disparity is significant (> 20%)
        disparity_flag = rate_disparity > 0.2
    else:
        rate_disparity = 0.0
        disparity_flag = False
    
    return {
        "by_language": metrics,
        "overall": {
            "average_ats_score": overall_avg,
            "total_resumes": overall_total
        },
        "equity_analysis": {
            "rate_disparity": rate_disparity,
            "disparity_flag": disparity_flag,
            "interpretation": (
                "Significant disparity detected across languages. Review for potential bias."
                if disparity_flag else
                "No significant disparity detected across languages."
            )
        }
    }

@router.post("/record-metrics")
async def record_fairness_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Record current fairness metrics to database for historical tracking
    """
    # Get current metrics
    dashboard = await get_fairness_dashboard(current_user, db)
    
    # Record each language's metrics
    for lang_metric in dashboard["by_language"]:
        db_metric = FairnessMetrics(
            language_code=lang_metric["language_code"],
            average_ats_score=lang_metric["average_ats_score"],
            total_resumes=lang_metric["total_resumes"],
            shortlisted_count=lang_metric["shortlisted_count"],
            shortlist_rate=lang_metric["shortlist_rate"]
        )
        db.add(db_metric)
    
    db.commit()
    
    return {"message": "Fairness metrics recorded successfully"}

@router.get("/history")
async def get_fairness_history(
    limit: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get historical fairness metrics
    """
    metrics = db.query(FairnessMetrics).order_by(
        FairnessMetrics.recorded_at.desc()
    ).limit(limit).all()
    
    return [
        {
            "language_code": m.language_code,
            "average_ats_score": m.average_ats_score,
            "total_resumes": m.total_resumes,
            "shortlisted_count": m.shortlisted_count,
            "shortlist_rate": m.shortlist_rate,
            "recorded_at": m.recorded_at
        }
        for m in metrics
    ]
