# Base Entity
def promptEntity(prompt) -> dict:
    return {
        "id": str(prompt["_id"]),
        "team_id": prompt["team_id"],
        "prompt": prompt["prompt"]
    }

def promptResponseEntity(prompt) -> dict:
    return {
        "id": str(prompt["_id"]),
        "team_id": str(prompt["team_id"]),
        "prompt": prompt["prompt"]
    }