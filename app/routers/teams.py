from typing import Annotated
from bson import ObjectId

from ..dependencies.database import insert_data, find_one_data, update_data
from fastapi import APIRouter, Depends, HTTPException, status
from ..dependencies.security import get_current_user, is_user_in_team, generate_otp_code
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


# API Endpoint for Inviting a Team Member (PUT Request, updating the team)
@router.put("{team_id}/invite")
async def team_invite_user(team_id: str, form_data: str, team_document: Annotated[UserBase, Depends(is_user_in_team)]):
    # first we generate the 6 digit invite code
    otp_code = generate_otp_code()

    # store the user email and invite code to the teams.invite list
    result = update_data("teams", 
                         {"_id": ObjectId(team_id)},
                         {"$push": {"invites": {form_data: otp_code} } }
                         )
    if result is Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not invite user to the team.",
        )

    # send the email to user with the invite code (use some external service to send email)


# API Endpoint for Joining a Team
@router.put("/join")
async def team_user_join(form_data: str, current_user: Annotated[UserBase, Depends(get_current_user)]):
    user_email = current_user["email"]
    
    # check if the user's email exists in the teams.invite list
    team = teamResponseEntity(find_one_data("teams", {"invites": {user_email: form_data} }))
    if team is Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wrong invite code or code is expired.",
        )
    
    # adding the user to the team
    result_update = update_data("teams",
                                {"_id": ObjectId(team["id"])},
                                {"members": ObjectId(current_user["id"])}
                                )
    """

# API Endpoint for Deleting a Team (POST)
@router.delete("delete_team")
async def delete_team():


# API Endpoint for Deleting a Team Member (PUT Request, updating the team)
@router.delete("{team_id}/{user_id}")
async def team_delete_user():
"""