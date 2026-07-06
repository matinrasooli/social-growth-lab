from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.compliance.guardrail import check_request
from app.models.core import User, ComplianceLog
from app.schemas.misc import ComplianceCheckRequest

router = APIRouter(prefix="/compliance", tags=["compliance"])


@router.post("/check")
def check(payload: ComplianceCheckRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    result = check_request(payload.text)
    log = ComplianceLog(
        user_id=user.id, endpoint="/compliance/check", input_excerpt=payload.text[:1000],
        allowed=result.allowed, category=result.category.value if result.category else None,
        explanation=result.explanation if not result.allowed else "allowed",
    )
    db.add(log)
    db.commit()
    return {
        "allowed": result.allowed,
        "category": result.category.value if result.category else None,
        "explanation": result.explanation,
        "compliant_alternative": result.alternative,
    }


@router.get("/logs")
def logs(limit: int = 100, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return (
        db.query(ComplianceLog)
        .order_by(ComplianceLog.created_at.desc())
        .limit(limit)
        .all()
    )
