from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, debugger, study

router = APIRouter(prefix="/api/v1")

router.include_router(auth.router)
router.include_router(users.router)
router.include_router(debugger.router)
router.include_router(study.router)
