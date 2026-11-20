from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user, exigir_perfil, verificar_acesso
from app.models.db_models import Departamento, Usuario, Reembolso, Historico
from app.schemas.schemas import Login, UsuarioCreate, UsuarioOut, DepartamentoCreate, ReembolsoCreate, ReembolsoUpdate, ReembolsoOut, DecisaoInput
from app.core.security import hash_password, verify_password, create_token
from app.services.historico import registrar_historico

router = APIRouter(tags=['Departamentos'])

@router.get("/departamentos")
def listar_departamentos(
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user)
):
    return db.query(Departamento).all()

@router.post("/departamentos", status_code=201)
def criar_departamento(
    dados: DepartamentoCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user)
):
    exigir_perfil(user, "FINANCEIRO")

    departamento = Departamento(nome=dados.nome)
    db.add(departamento)

    try:
        db.commit()
        db.refresh(departamento)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Departamento já existe")

    return departamento
