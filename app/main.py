from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import google_auth, users, teams, machine_learning

# uvicorn app.main:app --reload
app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(google_auth.router)
app.include_router(teams.router)
app.include_router(machine_learning.router)

# can make routers in the main, or use routers in the router folder
@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}