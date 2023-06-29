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

technologies_collection = db["technologies"]


# insert function (insert one doc)
def insert_data(collection_name, doc):
    collection = db[collection_name]
    try:
        result = collection.insert_one(doc)
        return result
    except Exception as e:
        return e
    
# find one function (for one doc)
def find_one_data(collection_name, query):
    collection = db[collection_name]
    return collection.find_one(query)

# find function (for all docs)
def find_data(collection_name, query):
    collection = db[collection_name]
    try:
        cursor = collection.find(query)
        return cursor
    except Exception as e:
        return e

# delete function (delete one doc)
def delete_data(collection_name, query):
    collection = db[collection_name]
    try:
        result = collection.delete_one(query)
        return result
    except Exception as e:
        return e
    
# update function (update one doc)
def update_data(collection_name, query, new_values):
    collection = db[collection_name]
    try:
        result = collection.update_one(query, new_values)
        return result
    except Exception as e:
        return e