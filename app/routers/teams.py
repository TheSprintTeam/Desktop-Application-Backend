from typing import Annotated
from bson import ObjectId

from ..dependencies.database import insert_data, find_one_data
from fastapi import APIRouter, Depends, HTTPException, status
from ..dependencies.security import get_current_user, is_user_in_team
from ..models.team import TeamBase
from ..models.user import UserBase
from ..serializers.teamSerializers import teamResponseEntity

router = APIRouter(
    prefix="/teams",
    tags=["teams"],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Not found"}},
)

# API Endpoint for Creating a Team (POST)
@router.post("/create-team")
async def create_team(form_data: TeamBase, current_user: Annotated[UserBase, Depends(get_current_user)]):
    user_id = current_user["id"]

    # Take Form Data and Create the Team
    form_data.team_lead = ObjectId(user_id)
    result = insert_data("teams", form_data.dict())
    if result is Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not insert team into database",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    team_result = teamResponseEntity(find_one_data("teams", {"_id": result.inserted_id}))
    return {"team": team_result}

# API Endpoint for Getting a Team Document (GET)
@router.get("/{team_id}")
async def get_team_details(team_id: str, team_document: Annotated[TeamBase, Depends(is_user_in_team)]):
    return team_document

# API Endpoint for Getting Technologies within a Team (GET)
@router.get("/{team_id}/technologies")
async def get_technologies(team_id: str, team_document: Annotated[UserBase, Depends(is_user_in_team)]):
    return team_document["technologies"]

# API Endpoint for Getting All Members within a Team (GET)
@router.get("/{team_id}/members")
async def get_team_members(team_id: str, team_document: Annotated[UserBase, Depends(is_user_in_team)]):
    return team_document["members"]

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


# API Endpoint for Deleting a Team Member (PUT Request, updating the team)
@router.delete("{team_id}/{user_id}")
async def team_delete_user():
    
"""