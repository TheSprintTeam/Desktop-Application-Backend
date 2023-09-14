from fastapi import APIRouter, Depends, HTTPException, status, Request
from pymongo import MongoClient
from bson import ObjectId
from typing import Annotated, List

from ..dependencies.database import insert_data, find_one_data
from ..dependencies.security import get_current_user, is_user_in_team, user_has_perms
from ..models.team import TeamBase
from ..serializers.mlSerializers import promptResponseEntity

import json
import requests
from ..models.helper import PyObjectId

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from ..config import MONGODB_URL
import certifi


client = MongoClient(MONGODB_URL, server_api=ServerApi('1'), tlsCAFile=certifi.where())
db = client["sprint"]

router = APIRouter(
    prefix="/teams/ml",
    tags=["teams"],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Not found"}},
)

# Declare any duplicate dependencies going to be used
UserInTeamsDep = Annotated[TeamBase, Depends(is_user_in_team)]


# Function to get the recommendation from the "machine-learning" collection on MongoDB
def get_recommendation_from_db(team_id: ObjectId):
    collection = db["machine-learning"]
    recommendation_doc = collection.find_one({"team_id": team_id})
    return recommendation_doc


# Function to store the recommendation in MongoDB and update the "teams" collection
def store_recommendation_to_mongodb(team_id: PyObjectId, recommendations: List[str]):
    # Get the team's technology from the "teams" collection
    team_technology = db["teams"].find_one({"_id": team_id})["technologies"]

    # Update the technologies field with the recommendations
    db["teams"].update_one(
        {"_id": team_id},
        {"$push": {"technologies": {"$each": recommendations}}},
    )
    # Store the updated recommendation list in the machine-learning collection
    db["machine-learning"].update_one(
        {"_id": team_id},
        {"$set": {"recommendation": recommendations}},
    )

    return {"message": "Recommendation saved successfully"}


# API Endpoint for storing the prompt
@router.post("/{team_id}/prompt")
async def store_prompt(team_id: str, prompt: str, team_doc: Annotated[TeamBase, Depends(user_has_perms)]):
    # check if team already has a prompt stored to it
    check = find_one_data("machine-learning", {"team_id": ObjectId(team_id)})
    if check is not None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Your team already entered in a prompt.",
        )

    #  take the form data and store it to the team id
    result = insert_data("machine-learning", {"team_id": ObjectId(team_id), "prompt": prompt})
    if result is Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Prompt could not be stored in the database.",
        )

    return {"The prompt was successfully stored to the team."}


# API Endpoint for getting the prompt
@router.get("/{team_id}/prompt")
async def get_prompt(team_id: str):
    # check in the database based on the team id to get the prompt
    result = find_one_data("machine-learning", {"team_id": ObjectId(team_id)})
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not find a prompt stored to the team.",
        )
    return promptResponseEntity(result)


# API Endpoint to store the recommendation
@router.post("/{team_id}/recommendation")
async def store_team_recommendation(team_id: str, request: Request, team_doc: UserInTeamsDep):
    recommendation = await request.json()

    # Send the recommendation to the recommendation engine on Cloud Run
    cloud_run_url = "https://sprint-391123-vtxnqdaumq-uc.a.run.app"
    response = requests.post(f"{cloud_run_url}/predict", json=recommendation)

    if response.status_code == 200:
        recommendation_response = response.json()
        # Receive the recommendations portion in the JSON file
        recommendations = recommendation_response.get("recommendations")

        # Convert team_id from string to ObjectId
        team_id_obj = ObjectId(team_id)

        # Get the recommendation from the machine-learning collection
        recommendation_doc = get_recommendation_from_db(team_id_obj)

        if recommendation_doc:
            # Extract the recommendation from the machine-learning collection
            recommendation_list = recommendation_doc.get("recommendation", [])

            # Append the new recommendation to the list
            recommendation_list.extend(recommendations)  # Use extend to add all recommendations

            # Store the updated recommendation list in the machine-learning collection
            collection = db["machine-learning"]
            collection.update_one(
                {"_id": team_id_obj},
                {"$set": {"recommendation": recommendation_list}},
            )

            # Update the teams collection with the new recommendation under the technologies
            team_technology = team_doc.technologies
            team_technology.extend(recommendations)  # Use extend to add all recommendations
            collection = db["teams"]
            collection.update_one(
                {"_id": team_id_obj},
                {"$set": {"technologies": team_technology}},
            )

            return {"message": "Recommendation saved successfully"}

        else:
            # Create a new document with the recommendation for the team in the "machine-learning" collection
            store_recommendation_to_mongodb(team_id_obj, recommendations)

            return {"message": "Recommendation saved successfully"}

    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get the recommendation from the engine.",
        )

# API Endpoint to get the recommendation
# API Endpoint to get the recommendation
@router.get("/{team_id}/recommendation")
async def get_team_recommendation(team_id: str):
    # Convert team_id from string to ObjectId
    team_id_obj = ObjectId(team_id)

    # Get the recommendation from the machine-learning collection
    recommendation_doc = get_recommendation_from_db(team_id_obj)

    if recommendation_doc:
        # Extract the recommendation from the machine-learning collection
        recommendation_list = recommendation_doc.get("recommendation", [])

        return {"recommendation": recommendation_list}

    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No recommendation found for the given team_id.",
        )

## form data stored in ml collection for use later
@router.post("/formSubmission")
async def formSubmission(payload : dict):
    # store all form data
    result = insert_data("machine-learning", json.dumps(payload))
    if result is Exception:
        print(result)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="data could not be stored in the database.",
        )
    else: return {"The data was successfully stored"}
    
