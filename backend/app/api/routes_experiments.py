from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.api.compliance_helper import enforce_compliance
from app.models.core import User
from app.models.experiments import Experiment, ExperimentResult
from app.schemas.misc import ExperimentCreate, ExperimentResultCreate

router = APIRouter(prefix="/experiments", tags=["experiments"])


@router.post("")
def create_experiment(payload: ExperimentCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    enforce_compliance(db, "/experiments", user.id, payload.hypothesis, payload.expected_metric_improvement)
    exp = Experiment(
        account_id=payload.account_id, variable=payload.variable,
        hypothesis=payload.hypothesis, expected_metric_improvement=payload.expected_metric_improvement,
    )
    db.add(exp)
    db.commit()
    db.refresh(exp)
    return exp


@router.post("/results")
def add_experiment_result(payload: ExperimentResultCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    exp = db.query(Experiment).get(payload.experiment_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
    result = ExperimentResult(
        experiment_id=payload.experiment_id, actual_results=payload.actual_results,
        winner_or_loser=payload.winner_or_loser, lesson_learned=payload.lesson_learned,
        next_recommended_test=payload.next_recommended_test,
    )
    exp.status = "complete"
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


@router.get("")
def list_experiments(account_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    query = db.query(Experiment)
    if account_id is not None:
        query = query.filter(Experiment.account_id == account_id)
    return query.order_by(Experiment.created_at.desc()).all()
