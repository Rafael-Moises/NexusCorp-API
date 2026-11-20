from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user, exigir_perfil, verificar_acesso
from app.models.db_models import Departamento, Usuario, Reembolso, Historico
from app.schemas.schemas import Login, UsuarioCreate, UsuarioOut, DepartamentoCreate, ReembolsoCreate, ReembolsoUpdate, ReembolsoOut, DecisaoInput
from app.core.security import hash_password, verify_password, create_token
from app.services.historico import registrar_historico

router = APIRouter(tags=['Histórico'])

@router.get("/historico/{reembolso_id}")
def consultar_historico(
    reembolso_id: int,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user)
):
    reembolso = db.query(Reembolso).filter(
        Reembolso.id == reembolso_id
    ).first()

    if not reembolso:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")

    if user.perfil == "COLABORADOR":
        verificar_acesso(reembolso, user)

    elif user.perfil == "GESTOR":
        solicitante = db.query(Usuario).filter(
            Usuario.id == reembolso.solicitante_id
        ).first()

        if not solicitante or solicitante.departamento_id != user.departamento_id:
            raise HTTPException(status_code=404, detail="Solicitação não encontrada")

    registros = db.query(Historico).filter(
        Historico.reembolso_id == reembolso_id
    ).order_by(Historico.id.asc()).all()

    return [
        {
            "id": h.id,
            "reembolso_id": h.reembolso_id,
            "responsavel_id": h.responsavel_id,
            "etapa": h.etapa,
            "decisao": h.decisao,
            "data_decisao": h.data_decisao,
            "observacao": h.observacao
        }
        for h in registros
    ]
