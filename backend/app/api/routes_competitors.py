from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.api.compliance_helper import enforce_compliance
from app.models.core import User
from app.models.experiments import CompetitorNote
from app.schemas.misc import CompetitorNoteCreate
from app.services.strategy import analyze_competitor_notes

router = APIRouter(prefix="/competitors", tags=["competitors"])


@router.post("/notes")
def create_note(payload: CompetitorNoteCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    enforce_compliance(
        db, "/competitors/notes", user.id,
        payload.competitor_name, payload.profile_reference, payload.notes, payload.offer,
    )
    note = CompetitorNote(**payload.model_dump())
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.get("/summary")
def summary(account_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    query = db.query(CompetitorNote)
    if account_id is not None:
        query = query.filter(CompetitorNote.account_id == account_id)
    notes = query.all()
    if not notes:
        return {"message": "No competitor notes yet. Add manual observations to get pattern analysis."}
    notes_payload = [
        {
            "competitor_name": n.competitor_name, "content_type": n.content_type, "hook": n.hook,
            "topic": n.topic, "offer": n.offer, "visual_style": n.visual_style,
            "estimated_engagement": n.estimated_engagement, "why_it_worked": n.why_it_worked,
        }
        for n in notes
    ]
    return analyze_competitor_notes(notes_payload)
