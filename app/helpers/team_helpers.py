from ..dependencies.database import find_data
from ..serializers.teamSerializers import teamListResponseEntity

# helper function to get all of a user's teams
def get_all_user_teams(user_id):
    result_teams = find_data("teams",
        {"$or": [
            {"team_lead": user_id},
            {"members": { "$elemMatch": {"user_id": user_id } } }
        ]})
    if result_teams is not Exception:
        return teamListResponseEntity(result_teams)
    return None