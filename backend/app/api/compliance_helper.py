from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.compliance.guardrail import check_request_bundle, ComplianceResult
from app.models.core import ComplianceLog


def enforce_compliance(db: Session, endpoint: str, user_id: int | None, *texts: str | None) -> None:
    """
    Run the compliance guardrail over free-text inputs to an endpoint.
    Logs every check (allowed or not). Raises HTTP 400 with the guardrail's
    explanation + compliant alternative if the request is blocked.
    """
    result: ComplianceResult = check_request_bundle(*texts)

    excerpt = " | ".join(t[:200] for t in texts if t)[:1000]
    log = ComplianceLog(
        user_id=user_id,
        endpoint=endpoint,
        input_excerpt=excerpt,
        allowed=result.allowed,
        category=result.category.value if result.category else None,
        explanation=result.explanation if not result.allowed else "allowed",
    )
    db.add(log)
    db.commit()

    if not result.allowed:
        raise HTTPException(
            status_code=400,
            detail={
                "message": result.explanation,
                "category": result.category.value if result.category else None,
                "compliant_alternative": result.alternative,
            },
        )
