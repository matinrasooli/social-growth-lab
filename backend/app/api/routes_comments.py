from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.api.compliance_helper import enforce_compliance
from app.models.core import User
from app.models.experiments import Comment, ReplyDraft
from app.schemas.misc import CommentClassifyRequest, ReplyDraftRequest
from app.services.comments import classify_comments, draft_replies

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("/classify")
def classify(payload: CommentClassifyRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    enforce_compliance(db, "/comments/classify", user.id, *payload.texts)
    results = classify_comments(payload.texts)
    for r in results:
        db.add(Comment(account_id=payload.account_id, raw_text=r["text"], classification=r["classification"]))
    db.commit()
    return results


@router.post("/reply-draft")
def reply_draft(payload: ReplyDraftRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """
    Always returns DRAFT-ONLY replies. Nothing in this codebase sends a message
    to Instagram; sending would require an approved official API integration
    plus explicit per-message human confirmation, which does not exist here.
    """
    enforce_compliance(db, "/comments/reply-draft", user.id, payload.comment_text)
    drafts = draft_replies(payload.comment_text, payload.classification, payload.tones)

    comment = Comment(account_id=payload.account_id, raw_text=payload.comment_text, classification=payload.classification)
    db.add(comment)
    db.flush()
    for d in drafts:
        db.add(ReplyDraft(comment_id=comment.id, tone=d["tone"], draft_text=d["text"], approved=False, sent=False))
    db.commit()
    return {"drafts": drafts, "note": "Draft only. Review and send manually; auto-send is intentionally not implemented."}
