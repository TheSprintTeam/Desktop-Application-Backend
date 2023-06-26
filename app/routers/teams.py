from typing import Annotated
from bson import ObjectId

from ..dependencies.database import teams_collection, insert_data, find_data
from fastapi import APIRouter, Response, Depends, HTTPException, status
from .users import read_users_me
from ..dependencies.security import get_current_user
from ..models.team import TeamBase
from ..serializers.teamSerializers import teamResponseEntity


router = APIRouter(
    prefix="/teams",
    tags=["teams"],
    #dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)

# API Endpoint for Creating a Team (POST)
@router.post("create_team")
async def create_team(form_data: Annotated[TeamBase, Depends(get_current_user)]):
    user = read_users_me()

    # Take Form Data and Create the Team
    form_data.team_lead = ObjectId(user["id"])
    result = insert_data("teams", form_data.dict())
    if result is Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not insert team into database",
            headers={"WWW-Authenticate": "Bearer"},
        )
    team_result = teamResponseEntity(find_data("teams", "_id", result.inserted_id))
    return {"team": team_result}


"""
# API Endpoint for Joining a Team
@router.put("{team_id}/join")
async def team_invite_user():


# API Endpoint for Inviting a Team Member (PUT Request, updating the team)
@router.put("{team_id}/invite")
async def team_invite_user():



# API Endpoint for Deleting a Team (POST)
@router.delete("delete_team")
async def delete_team():


# API Endpoint for Getting All Members of a Team (GET)
@router.get("{team_id}/members")
async def get_team_members():


# API Endpoint for Deleting a Team Member (PUT Request, updating the team)
@router.delete("{team_id}/{user_id}")
async def team_delete_user():
    
"""