from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user, exigir_perfil, verificar_acesso
from app.models.db_models import Departamento, Usuario, Reembolso, Historico
from app.schemas.schemas import Login, UsuarioCreate, UsuarioOut, DepartamentoCreate, ReembolsoCreate, ReembolsoUpdate, ReembolsoOut, DecisaoInput
from app.core.security import hash_password, verify_password, create_token
from app.services.historico import registrar_historico

router = APIRouter(tags=['Autenticação'])

@router.post("/auth/login")
def login(dados: Login, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.email == dados.email).first()

    if not user or not verify_password(dados.senha, user.senha_hash):
        raise HTTPException(
            status_code=401,
            detail="E-mail ou senha incorretos"
        )

    return {
        "access_token": create_token(user.id),
        "token_type": "bearer"
    }

@router.get("/usuarios/me", response_model=UsuarioOut)
@router.get("/me", response_model=UsuarioOut)
def meu_usuario(user: Usuario = Depends(get_current_user)):
    return user
