from fastapi import FastAPI
from src.routers.auth import users

app = FastAPI(
    title="website of the hostel",
    version="0.1.0"
)

@app.get("/")
async def root():
    return {"message": "Hello on site"}

app.include_router(router=users.router)