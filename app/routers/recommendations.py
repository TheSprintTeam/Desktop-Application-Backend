from fastapi import Body, APIRouter, HTTPException, status
import requests
import json

router = APIRouter(
    prefix="/teams/ml",
    tags=["teams"],
    responses={404: {"description": "Not found"}},
)

# API Endpoint for getting the recommendations from rec eng
@router.post("/send-recommendations")
async def send_recommendations(payload: dict):
    try:
        response = requests.post("https://sprint-391123-vtxnqdaumq-uc.a.run.app/", json=payload)
        return response.json()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get the recommendation from the engine.",
        )