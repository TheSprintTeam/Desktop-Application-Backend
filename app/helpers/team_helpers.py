from ..dependencies.database import find_data
from ..serializers.teamSerializers import teamResponseEntity

# helper function to get all of a user's teams
def get_all_user_teams(user_id):
    users_teams = []

    result_team_lead = find_data("teams",
        {"$or": [
            {"team_lead": user_id},
            {"members": user_id}
        ]})
    if result_team_lead is not Exception:
        for team in result_team_lead:
            users_teams.append(teamResponseEntity(team))

    if users_teams is not None:
        return users_teams
    return None