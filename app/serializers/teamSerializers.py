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
        "invites": [str(i) for i in team["invites"]],
        "members": [str(i) for i in team["members"]],
        "technologies": [str(i) for i in team["technologies"]]
    }