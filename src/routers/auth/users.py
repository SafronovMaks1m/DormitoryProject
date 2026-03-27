from fastapi import APIRouter

from .login import router as login_router
from .password import router as password_router
from .register import router as register_router
from .sessions import router as sessions_router

router = APIRouter(prefix="/users", tags=["users"])

router.include_router(register_router)
router.include_router(login_router)
router.include_router(password_router)
router.include_router(sessions_router)