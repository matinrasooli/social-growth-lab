from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.core import User
from app.models.content import InstagramInsight, ContentCalendarItem
from app.models.experiments import Experiment, CompetitorNote
from app.models.simulation import SimulationRun

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    insights_count = db.query(InstagramInsight).count()
    calendar_count = db.query(ContentCalendarItem).count()
    experiments_count = db.query(Experiment).count()
    competitor_notes_count = db.query(CompetitorNote).count()
    simulation_runs_count = db.query(SimulationRun).count()

    return {
        "insights_uploaded": insights_count,
        "calendar_items_planned": calendar_count,
        "experiments_tracked": experiments_count,
        "competitor_notes": competitor_notes_count,
        "simulation_runs": simulation_runs_count,
        "getting_started": insights_count == 0,
    }
