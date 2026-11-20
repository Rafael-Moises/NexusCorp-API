from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user, exigir_perfil, verificar_acesso
from app.models.db_models import Departamento, Usuario, Reembolso, Historico
from app.schemas.schemas import Login, UsuarioCreate, UsuarioOut, DepartamentoCreate, ReembolsoCreate, ReembolsoUpdate, ReembolsoOut, DecisaoInput
from app.core.security import hash_password, verify_password, create_token
from app.services.historico import registrar_historico

router = APIRouter(tags=['Geral'])

@router.get("/")
def inicio():
    return {
        "mensagem": "API NexusCorp funcionando",
        "documentacao": "/docs"
    }
