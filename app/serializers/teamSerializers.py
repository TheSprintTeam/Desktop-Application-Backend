# Base Entity
def teamEntity(team) -> dict:
    return {
        "id": str(team["_id"]),
        "name": team["name"],
        "description": team["description"],
        "team_lead": str(team["team_lead"]),
        "invites": team["invites"],
        "members": team["members"],
        "technologies": team["technologies"]
    }

def teamResponseEntity(team) -> dict:
    return {
        "id": str(team["_id"]),
        "name": team["name"],
        "description": team["description"],
        "team_lead": str(team["team_lead"]),
        "invites": inviteListResponseEntity(team["invites"]),
        "members": memberListResponseEntity(team["members"]),
        "technologies": [str(i) for i in team["technologies"]]
    }

def teamListResponseEntity(teams) -> list:
    return [teamResponseEntity(team) for team in teams]


# entities for the invites, members, and technologies (they are lists which may have objectIds)
def inviteEntity(invite) -> dict:
    print(invite)
    return {
        "email": invite["email"],
        "role": str(invite["role"]),
        "otp_code": invite["otp_code"],
    }

def inviteListResponseEntity(invites) -> list:
    return [inviteEntity(invite) for invite in invites]

def memberEntity(member) -> dict:
    return {
        "user_id": str(member["user_id"]),
        "role": str(member["role"]),
        "email": member["email"]
    }

def memberListResponseEntity(members) -> list:
    return [memberEntity(member) for member in members]