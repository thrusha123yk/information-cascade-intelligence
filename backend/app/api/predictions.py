from fastapi import APIRouter, HTTPException
from ..database.repository import get_topic_by_id, get_predictions_for_topic
from ..services.prediction_service import forecast_cascade_growth

router = APIRouter(prefix="/api/predictions", tags=["Growth Prediction"])

@router.get("/{topic_id}")
def get_topic_predictions(topic_id: str):
    top = get_topic_by_id(topic_id)
    if not top:
        raise HTTPException(status_code=404, detail="Topic not found.")
        
    preds = get_predictions_for_topic(topic_id)
    if not preds:
        preds = forecast_cascade_growth(top.get("articles", []), float(top.get("cascade_score", 0)))
        
    return {
        "topic": {
            "id": top["id"],
            "label": top["label"],
            "cascade_score": top.get("cascade_score", 0),
            "current_volume": top.get("article_count", 0)
        },
        "predictions": preds,
        "methodology": {
            "model": "Baseline Time-Decay Volume Forecasting",
            "horizons": ["24 Hours", "48 Hours", "72 Hours"],
            "metric": "Expected Public Journalistic Article Coverage",
            "limitations": "Model relies strictly on public news/RSS volume curves; not indicative of dark social or private messaging propagation."
        }
    }

