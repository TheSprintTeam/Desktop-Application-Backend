# Base for a User Entity
def userEntity(user) -> dict:
    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "password": user["password"],
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "created_at": user["created_at"],
        "updated_at": user["updated_at"],
        "verified": user["verified"]
        #"user_name": user["user_name"],
        #"ip_address": user["ip_address"],
        #"user_password": user["user_password"]
    }

# User Entity for Google (they have no password)
def userEntityGoogle(user) -> dict:
    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "created_at": user["created_at"],
        "updated_at": user["updated_at"],
        "verified": user["verified"]
        #"user_name": user["user_name"],
        #"ip_address": user["ip_address"],
        #"user_password": user["user_password"]
    }

# User Response Entity should return no password
def userResponseEntity(user) -> dict:
    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "created_at": user["created_at"],
        "updated_at": user["updated_at"],
        "verified": user["verified"]
        #"user_name": user["user_name"],
        #"ip_address": user["ip_address"],
        #"user_password": user["user_password"]
    }


def embeddedUserResponse(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "photo": user["photo"]
    }

def userListEntity(users) -> list:
    return [userEntity(user) for user in users]
