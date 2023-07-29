from typing import Annotated
from bson import ObjectId

from fastapi import APIRouter, Depends, HTTPException, status

from ..dependencies.database import insert_data, find_one_data
from ..dependencies.security import get_current_user, is_user_in_team, user_has_perms
from ..models.team import TeamBase
from ..serializers.mlSerializers import promptResponseEntity

router = APIRouter(
    prefix="/teams/ml",
    tags=["teams"],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Not found"}},
)

# Declare any duplicate dependencies going to be used
UserInTeamsDep = Annotated[TeamBase, Depends(is_user_in_team)]


# API Endpoint for storing the prompt
@router.post("/{team_id}/prompt")
async def store_prompt(team_id: str, prompt: str, team_doc: Annotated[TeamBase, Depends(user_has_perms)]):
    # check if team already has a prompt stored to it
    check = find_one_data("machine-learning", {"team_id": ObjectId(team_id)})
    if check is not None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Your team already entered in a prompt.",
        )

    # we take the form data and store it to the team id
    result = insert_data("machine-learning", {"team_id": ObjectId(team_id), "prompt": prompt})
    if result is Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Prompt could not be stored in the database.",
        )
    
    return {"The prompt was successfully stored to the team."}

# API Endpoint for getting the prompt
@router.get("/{team_id}/prompt")
async def get_prompt(team_id: str):
    # check in the database based on the team id to get the prompt
    result = find_one_data("machine-learning", {"team_id": ObjectId(team_id)})
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not find a prompt stored to the team.",
        )
    return promptResponseEntity(result)

# API Endpoint to store the recommendation
@router.post("/teams/{team_id}/recommendation")
async def store_team_recommendation(team_id: str, request:Request):
    recommendation = await request.json()
    #need to store recommendation for the team from the database

    #Convert recommendation into a json format
    recommendation_json = json.dumps(recommendation)

# API Endpoint to get the recommendation
@router.get("/teams/{team_id}/recommendation")
async def get_team_recommendation(team_id: str):
    #need to get recommendation for the team from the database

    recommendation = json.loads(recommendation_json)
    recommendation = {"message": "Sprint believes you should do this:"}
    return recommendation
