from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user, exigir_perfil, verificar_acesso
from app.models.db_models import Departamento, Usuario, Reembolso, Historico
from app.schemas.schemas import Login, UsuarioCreate, UsuarioOut, DepartamentoCreate, ReembolsoCreate, ReembolsoUpdate, ReembolsoOut, DecisaoInput
from app.core.security import hash_password, verify_password, create_token
from app.services.historico import registrar_historico

router = APIRouter(tags=['Usuários'])

@router.post("/usuarios", response_model=UsuarioOut, status_code=201)
def criar_usuario(
    dados: UsuarioCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user)
):
    exigir_perfil(user, "FINANCEIRO")

    if db.query(Usuario).filter(Usuario.email == dados.email).first():
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")

    if dados.perfil != "FINANCEIRO":
        if not dados.departamento_id or not db.query(Departamento).filter(
            Departamento.id == dados.departamento_id
        ).first():
            raise HTTPException(status_code=400, detail="Departamento inválido")

    novo = Usuario(
        nome=dados.nome,
        email=dados.email,
        senha_hash=hash_password(dados.senha),
        perfil=dados.perfil,
        departamento_id=dados.departamento_id
    )

    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo

@router.get("/usuarios", response_model=list[UsuarioOut])
def listar_usuarios(
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user)
):
    exigir_perfil(user, "FINANCEIRO")
    return db.query(Usuario).all()
