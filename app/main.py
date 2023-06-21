from fastapi import FastAPI

from .routers import users, auth

# uvicorn app.main:app --reload
app = FastAPI()


app.include_router(users.router)
app.include_router(auth.router)

# can make routers in the main, or use routers in the router folder
@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}