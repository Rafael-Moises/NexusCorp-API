from fastapi import APIRouter
from app.api.v1.routers.geral import router as geral_router
from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.usuarios import router as usuarios_router
from app.api.v1.routers.departamentos import router as departamentos_router
from app.api.v1.routers.reembolsos import router as reembolsos_router
from app.api.v1.routers.historico import router as historico_router

api_router = APIRouter()
for router in (geral_router, auth_router, usuarios_router, departamentos_router, reembolsos_router, historico_router):
    api_router.include_router(router)
