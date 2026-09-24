from django.core.exceptions import ValidationError

from .models import AIAnalysis


def serialize_ai_analysis(analysis):
    if not isinstance(analysis, AIAnalysis):
        raise ValidationError("A valid AI analysis is required.")

    return {
        "id": analysis.id,
        "screening_id": analysis.screening_id,
        "summary": analysis.summary,
        "risk_level": analysis.risk_level,
        "recommended_action": analysis.recommended_action,
        "explanation": analysis.explanation,
        "provider": analysis.provider,
        "model_name": analysis.model_name,
        "confidence": (
            float(analysis.confidence) if analysis.confidence is not None else None
        ),
        "status": analysis.status,
        "error_message": analysis.error_message,
        "created_at": analysis.created_at.isoformat(),
        "updated_at": analysis.updated_at.isoformat(),
    }


def serialize_ai_analyses(analyses):
    return [serialize_ai_analysis(analysis) for analysis in analyses]
