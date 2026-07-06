from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.core import User, UploadedFile as UploadedFileModel
from app.models.content import InstagramInsight
from app.schemas.misc import InsightsImportManual, AnalyticsFilter
from app.parsers.insights import parse_csv, parse_json, parse_pasted_text
from app.services.analytics import get_performance_summary
from app.services.strategy import generate_strategy_recommendations

router = APIRouter(tags=["insights"])


def _persist_records(db: Session, records, account_id: int | None, source_file: str | None):
    for rec in records:
        db.add(InstagramInsight(account_id=account_id, source_file=source_file, **rec.model_dump()))
    db.commit()


@router.post("/insights/import")
async def import_insights(
    file: UploadFile | None = File(None),
    pasted_text: str | None = Form(None),
    account_id: int | None = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if file is not None:
        contents = await file.read()
        if file.filename and file.filename.lower().endswith(".csv"):
            records = parse_csv(contents)
        elif file.filename and file.filename.lower().endswith(".json"):
            records = parse_json(contents)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type for insights import. Use .csv or .json.")
        _persist_records(db, records, account_id, file.filename)
        return {"imported": len(records)}

    if pasted_text:
        record = parse_pasted_text(pasted_text)
        _persist_records(db, [record], account_id, "pasted_text")
        return {"imported": 1}

    raise HTTPException(status_code=400, detail="Provide either a file or pasted_text.")


@router.post("/insights/import-manual")
def import_insights_manual(payload: InsightsImportManual, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _persist_records(db, payload.records, payload.account_id, "manual_form")
    return {"imported": len(payload.records)}


@router.get("/insights")
def list_insights(account_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    query = db.query(InstagramInsight)
    if account_id is not None:
        query = query.filter(InstagramInsight.account_id == account_id)
    return query.order_by(InstagramInsight.post_date.desc()).limit(500).all()


@router.get("/analytics/performance")
def analytics_performance(
    account_id: int | None = None,
    content_type: str | None = None,
    topic: str | None = None,
    campaign: str | None = None,
    hook_style: str | None = None,
    cta_type: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    filt = AnalyticsFilter(
        account_id=account_id, content_type=content_type, topic=topic,
        campaign=campaign, hook_style=hook_style, cta_type=cta_type,
    )
    summary = get_performance_summary(db, filt)
    if summary.get("count", 0) > 0:
        summary["strategy_recommendations"] = generate_strategy_recommendations(summary)
    return summary
