def userEntity(user) -> dict:
    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "password": user["password"],
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "role_id": str(user["role_id"]),
        "created_at": user["created_at"],
        "updated_at": user["updated_at"]
    }

def userEntityGoogle(user) -> dict:
    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        #"role_id": str(user["role_id"]),
        "created_at": user["created_at"],
        "updated_at": user["updated_at"]
    }

def userResponseEntity(user) -> dict:
    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "role_id": str(user["role_id"]),
        "created_at": user["created_at"],
        "updated_at": user["updated_at"]
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
