import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.core import User
from app.models.simulation import SimulationRun
from app.schemas.misc import SimulationRunRequest
from app.simulation.entities import generate_post
from app.simulation.engine import run_simulation

router = APIRouter(prefix="/simulation", tags=["simulation"])

VALID_STRUCTURES = {
    "random", "small_world", "influencer_hub", "niche_cluster",
    "dense_local_community", "sparse_network", "multi_community",
}


@router.post("/run")
def run(payload: SimulationRunRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if payload.network_structure not in VALID_STRUCTURES:
        raise HTTPException(status_code=400, detail=f"network_structure must be one of {sorted(VALID_STRUCTURES)}")
    if payload.num_users > 5000:
        raise HTTPException(status_code=400, detail="num_users capped at 5000 for local simulation performance")

    post = generate_post(
        topic=payload.topic, hook_strength=payload.hook_strength, visual_quality=payload.visual_quality,
        emotional_intensity=payload.emotional_intensity, usefulness=payload.usefulness, novelty=payload.novelty,
        controversy=payload.controversy, clarity=payload.clarity, cta_strength=payload.cta_strength,
        creator_trust=payload.creator_trust, posting_hour=payload.posting_hour,
    )
    results = run_simulation(
        network_structure=payload.network_structure, num_users=payload.num_users,
        num_ticks=payload.num_ticks, post=post,
    )

    run_record = SimulationRun(
        account_id=payload.account_id, name=payload.name, network_structure=payload.network_structure,
        num_users=payload.num_users, config_json=json.dumps(payload.model_dump()), results_json=json.dumps(results),
    )
    db.add(run_record)
    db.commit()
    db.refresh(run_record)

    return {"run_id": run_record.id, **results}


@router.get("/runs")
def list_runs(account_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    query = db.query(SimulationRun)
    if account_id is not None:
        query = query.filter(SimulationRun.account_id == account_id)
    runs = query.order_by(SimulationRun.created_at.desc()).all()
    return [
        {"id": r.id, "name": r.name, "network_structure": r.network_structure, "num_users": r.num_users,
         "created_at": r.created_at.isoformat()}
        for r in runs
    ]


@router.get("/runs/{run_id}")
def get_run(run_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    run_record = db.query(SimulationRun).get(run_id)
    if not run_record:
        raise HTTPException(status_code=404, detail="Simulation run not found")
    return {
        "id": run_record.id, "name": run_record.name, "network_structure": run_record.network_structure,
        "num_users": run_record.num_users, "config": json.loads(run_record.config_json),
        "results": json.loads(run_record.results_json), "created_at": run_record.created_at.isoformat(),
    }
