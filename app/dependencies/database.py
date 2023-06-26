from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from ..config import MONGODB_URL

# Create a new client and connect to the server
client = MongoClient(MONGODB_URL, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print("Could not successfully connect to MongoDB: ", e)

# Select the database
db = client["sprint"]

# different collections
users_collection = db["users"]
users_collection.create_index("email", unique = True)

teams_collection = db["teams"]


# insert function
def insert_data(collection_name, doc):
    collection = db[collection_name]
    try:
        result = collection.insert_one(doc)
        return result
    except Exception as e:
        return e
    
# find function
def find_data(collection_name, field, doc):
    collection = db[collection_name]
    try:
        result = collection.find_one({field: doc})
        return result
    except Exception as e:
        return e
    
# delete function
def delete_data(collection_name, field, doc):
    collection = db[collection_name]
    try:
        collection.delete_one({field: doc})
    except Exception as e:
        return e