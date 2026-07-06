import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.api.compliance_helper import enforce_compliance
from app.models.core import User
from app.models.content import ContentItem, ContentScore, HookAsset, CaptionAsset, CTAAsset, ContentCalendarItem
from app.schemas.content import (
    ContentScoreRequest, ContentScoreResponse,
    HookGenerateRequest, HookResult,
    CaptionGenerateRequest, CaptionResult,
    CTAGenerateRequest, CTAResult,
    CalendarGenerateRequest, CalendarItemOut,
)
from app.services.scoring import score_content
from app.services.generation import generate_hooks, generate_captions, generate_ctas, generate_calendar

router = APIRouter(tags=["content"])


@router.post("/content/score", response_model=ContentScoreResponse)
def score(payload: ContentScoreRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    enforce_compliance(
        db, "/content/score", user.id,
        payload.content_idea, payload.hook, payload.caption, payload.cta, payload.thumbnail_description,
    )
    result = score_content(payload)

    content_item = ContentItem(
        account_id=payload.account_id, content_type=payload.content_type, topic=payload.niche,
        idea=payload.content_idea, hook=payload.hook, caption=payload.caption, cta=payload.cta,
        thumbnail_description=payload.thumbnail_description,
    )
    db.add(content_item)
    db.flush()
    db.add(ContentScore(
        content_item_id=content_item.id,
        overall_score=result.overall_score, hook_score=result.hook_score, clarity_score=result.clarity_score,
        novelty_score=result.novelty_score, audience_fit_score=result.audience_fit_score,
        emotional_pull_score=result.emotional_pull_score, usefulness_score=result.usefulness_score,
        shareability_score=result.shareability_score, saveability_score=result.saveability_score,
        trust_score=result.trust_score, cta_score=result.cta_score, retention_risk=result.retention_risk,
        suggestions=json.dumps(result.improvement_suggestions), method=result.method,
    ))
    db.commit()
    return result


@router.post("/content/hooks", response_model=list[HookResult])
def hooks(payload: HookGenerateRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    enforce_compliance(db, "/content/hooks", user.id, payload.topic, payload.niche, payload.audience)
    results = generate_hooks(payload)
    for r in results:
        db.add(HookAsset(
            account_id=payload.account_id, style=r.style, text=r.text, expected_strength=r.expected_strength,
            rationale=r.rationale, visual_opening=r.visual_opening, matching_caption=r.matching_caption,
            matching_cta=r.matching_cta,
        ))
    db.commit()
    return results


@router.post("/content/captions", response_model=list[CaptionResult])
def captions(payload: CaptionGenerateRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    enforce_compliance(db, "/content/captions", user.id, payload.topic, payload.niche, payload.brand_voice)
    results = generate_captions(payload)
    for r in results:
        db.add(CaptionAsset(account_id=payload.account_id, style=r.style, text=r.text))
    db.commit()
    return results


@router.post("/content/ctas", response_model=list[CTAResult])
def ctas(payload: CTAGenerateRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    enforce_compliance(db, "/content/ctas", user.id, payload.topic, payload.audience_intent)
    results = generate_ctas(payload)
    for r in results:
        db.add(CTAAsset(
            account_id=payload.account_id, text=r.text, funnel_stage=r.funnel_stage,
            content_type=r.content_type, audience_intent=r.audience_intent, topic=payload.topic,
        ))
    db.commit()
    return results


@router.post("/calendar/generate", response_model=list[CalendarItemOut])
def calendar_generate(payload: CalendarGenerateRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    enforce_compliance(
        db, "/calendar/generate", user.id,
        payload.niche, payload.audience, payload.business_goal, payload.product, payload.brand_voice,
    )
    items = generate_calendar(payload)
    for item in items:
        db.add(ContentCalendarItem(
            account_id=payload.account_id, date=item.date, content_type=item.content_type, topic=item.topic,
            hook=item.hook, caption_outline=item.caption_outline, cta=item.cta, asset_needed=item.asset_needed,
            production_difficulty=item.production_difficulty, expected_outcome=item.expected_outcome,
            experiment_tag=item.experiment_tag, status=item.status,
        ))
    db.commit()
    return items


@router.get("/calendar", response_model=list[CalendarItemOut])
def calendar_list(account_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    query = db.query(ContentCalendarItem)
    if account_id is not None:
        query = query.filter(ContentCalendarItem.account_id == account_id)
    return query.order_by(ContentCalendarItem.date).all()
