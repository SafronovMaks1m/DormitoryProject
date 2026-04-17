from fastapi import FastAPI
from src.routers.auth import users
from src.routers.websockets import wb_endpoints
from src.routers.violations import vl_endpoints

app = FastAPI(
    title="website of the hostel",
    version="0.1.0"
)

@app.get("/")
async def root():
    return {"message": "Hello on site"}

app.include_router(router=users.router)
app.include_router(router=wb_endpoints.router)
app.include_router(router=vl_endpoints.router)
