from fastapi import FastAPI

from .routers import google_auth, users, teams, machine_learning

# uvicorn app.main:app --reload
app = FastAPI()


app.include_router(users.router)
app.include_router(google_auth.router)
app.include_router(teams.router)
app.include_router(machine_learning.router)

# can make routers in the main, or use routers in the router folder
@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}