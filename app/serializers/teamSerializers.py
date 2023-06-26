# Base Entity
def teamEntity(team) -> dict:
    return {
        "id": str(team["_id"]),
        "name": team["name"],
        "description": team["description"],
        "team_lead": str(team["team_lead"]),
        "invites": team["invites"],
        "members": str(team["members"]),
        "technologies": str(team["technologies"])
    }

def teamResponseEntity(team) -> dict:
    return {
        "id": str(team["_id"]),
        "name": team["name"],
        "description": team["description"],
        "team_lead": str(team["team_lead"]),
    }