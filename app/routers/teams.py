from requests import post
from typing import Annotated
from bson import ObjectId

from fastapi import APIRouter, Depends, HTTPException, status

from ..helpers.email_helpers import send_email, generate_otp_code
from ..models.team import TeamBase
from ..models.user import UserBase, UserInvite
from ..dependencies.database import insert_data, find_one_data, update_data
from ..dependencies.security import get_current_user, is_user_in_team, user_has_perms
from ..serializers.teamSerializers import teamResponseEntity, teamEntity
from ..serializers.userSerializers import userResponseEntity

router = APIRouter(
    prefix="/teams",
    tags=["teams"],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Not found"}},
)

# Declare any duplicate dependencies going to be used
UserInTeamsDep = Annotated[TeamBase, Depends(is_user_in_team)]


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
async def get_team_details(team_id: str, team_document: UserInTeamsDep):
    return teamResponseEntity(team_document)

# API Endpoint for Getting Technologies within a Team (GET)
@router.get("/{team_id}/technologies")
async def get_technologies(team_id: str, team_document: UserInTeamsDep):
    technology_list = []
    for technology in team_document["technologies"]:
        technology_data = find_one_data("technologies", {"_id": ObjectId(technology["id"])})
        technology_list.append(technology_data)
    return teamResponseEntity(team_document)["technologies"]

# API Endpoint for Getting All Members within a Team (GET)
@router.get("/{team_id}/members")
async def get_team_members(team_id: str, team_document: UserInTeamsDep):
    member_list = []
    for member in team_document["members"]:
        member_data = userResponseEntity(find_one_data("users", {"_id": ObjectId(member["user_id"])}))
        role_data = find_one_data("roles", {"_id": member["role"]})
        member_data["role"] = role_data["role"]
        member_list.append(member_data)
    return member_list


# API Endpoint for Inviting a Team Member (PUT Request, updating the team)
@router.put("{team_id}/invite")
async def team_invite_user(team_id: str, form_data: UserInvite, check: UserInTeamsDep, team_document: Annotated[TeamBase, Depends(user_has_perms)]):
    # first we generate the 6 digit invite code
    otp_code = generate_otp_code()

    # check if user email is already in the team
    invite_in_team = find_one_data("teams", {"members.email": form_data.email})
    if invite_in_team:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User is already in the team.",
        )

    # check if user email already has an invite to the team
    team = find_one_data("teams", {"invites.email": form_data.email})
    if team:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User has already been invited to the team.",
        )

    # send the email to user with the invite code (use some external service to send email)
    send_email(form_data.email, 
               "You have an invite to a Sprint Team", 
               "You have been invited to the " + team_document["name"] + " on Sprint. Join the team with the following code: "
                + otp_code + ". If you do not have an account with us, please create an account and then join the team with the code.")
    
    # store the user email and invite code to the teams.invite list
    result = update_data("teams", 
                         {"_id": ObjectId(team_id)},
                         {"$push": {"invites": {"email": form_data.email, "role": form_data.role_id, "otp_code": otp_code} } }
                         )
    if result is Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not invite user to the team.",
        )

    return "Invite to user was sent successfully"


# API Endpoint for Joining a Team
@router.put("/join")
async def team_user_join(otp_code: str, current_user: Annotated[UserBase, Depends(get_current_user)]):
    user_email = current_user["email"]
    
    # check if the user's email exists in the teams.invite list and otp code is correct
    team = find_one_data("teams", {"$and": [{"invites.email": user_email}, {"invites.otp_code": otp_code}] } )
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wrong invite code or code is expired.",
        )
    team = teamEntity(team)
    
    # get the user invite data (the role that the team lead selected for the user)
    for team_invite in team["invites"]:
        if team_invite["email"] == user_email:
            user_role = team_invite["role"]
            break

    # adding the user to the team in database
    result_update = update_data("teams",
                                {"_id": ObjectId(team["id"])},
                                {"$push": {"members": {"user_id": ObjectId(current_user["id"]), "role": ObjectId(user_role), "email": user_email } } }
                                )
    if result_update is Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not add user to the team.",
        )
    
    # delete the user in the invites in the teams collection database
    delete_invite = update_data("teams", 
                                {"_id": ObjectId(team["id"])},
                                {"$pull": {"invites": {"email": user_email} } } 
                                )
    if delete_invite is Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not delete user's invite in the team.",
        )
    
    return {"Successfully added member to team."}

# API endpoint for installing team-wide
@router.post("/teamInstall/{team_id}")
async def teamInstall(team_id :ObjectId):
    team = await find_one_data("teams", {"_id" : team_id})
    url = 'https://sprint-391123-vtxnqdaumq-uc.a.run.app'

    for memberId in team["members"]:
        payload = {
            "technologies" : team["technologies"],
            "user_id" : memberId
        }
        post(url, json = payload)
    
    return {"Installation finished without errors"}

# API endpoint for installing team-wide
@router.post("{team_id}/userInstall/{user_id}")
async def userInstall(team_id :ObjectId, user_id :ObjectId):
    team = await find_one_data("team", {"_id" : team_id})["members"]
    url = 'https://sprint-391123-vtxnqdaumq-uc.a.run.app'

    payload = {
            "technologies" : team["technologies"],
            "user_id" : user_id
            }
    
    post(url, json = payload)
    
    return {"Installation finished without errors"}
"""

# API Endpoint for Deleting a Team (POST)
@router.delete("delete_team")
async def delete_team():


# API Endpoint for Deleting a Team Member (PUT Request, updating the team)
@router.delete("{team_id}/{user_id}")
async def team_delete_user():
"""