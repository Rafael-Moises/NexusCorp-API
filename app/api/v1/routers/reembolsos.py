from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user, exigir_perfil, verificar_acesso
from app.models.db_models import Departamento, Usuario, Reembolso, Historico
from app.schemas.schemas import Login, UsuarioCreate, UsuarioOut, DepartamentoCreate, ReembolsoCreate, ReembolsoUpdate, ReembolsoOut, DecisaoInput
from app.core.security import hash_password, verify_password, create_token
from app.services.historico import registrar_historico

router = APIRouter(tags=['Reembolsos'])

@router.post("/reembolsos", response_model=ReembolsoOut, status_code=201)
def criar_reembolso(
    dados: ReembolsoCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user)
):
    exigir_perfil(user, "COLABORADOR")

    if dados.data_despesa > date.today():
        raise HTTPException(status_code=400, detail="Data futura não permitida")

    duplicado = db.query(Reembolso).filter(
        Reembolso.solicitante_id == user.id,
        Reembolso.comprovante_ref == dados.comprovante_ref
    ).first()

    if duplicado:
        raise HTTPException(status_code=409, detail="Comprovante já utilizado")

    novo = Reembolso(
        solicitante_id=user.id,
        categoria=dados.categoria,
        valor=dados.valor,
        data_despesa=dados.data_despesa,
        justificativa=dados.justificativa,
        comprovante_ref=dados.comprovante_ref,
        situacao="RASCUNHO"
    )

    db.add(novo)
    db.commit()
    db.refresh(novo)

    registrar_historico(db, novo, user, "CADASTRO", "CRIADO")
    db.commit()

    return novo

@router.get("/reembolsos", response_model=list[ReembolsoOut])
def listar_reembolsos(
    situacao: Optional[str] = None,
    categoria: Optional[str] = None,
    departamento_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user)
):
    query = db.query(Reembolso)

    if user.perfil == "COLABORADOR":
        query = query.filter(Reembolso.solicitante_id == user.id)

    elif user.perfil == "GESTOR":
        query = query.join(
            Usuario,
            Reembolso.solicitante_id == Usuario.id
        ).filter(Usuario.departamento_id == user.departamento_id)

        if departamento_id and departamento_id != user.departamento_id:
            raise HTTPException(status_code=403, detail="Departamento não autorizado")

    if departamento_id and user.perfil == "FINANCEIRO":
        query = query.join(
            Usuario,
            Reembolso.solicitante_id == Usuario.id
        ).filter(Usuario.departamento_id == departamento_id)

    if situacao:
        query = query.filter(Reembolso.situacao == situacao)

    if categoria:
        query = query.filter(Reembolso.categoria == categoria)

    return query.order_by(Reembolso.id.desc()).all()

@router.get("/reembolsos/{reembolso_id}", response_model=ReembolsoOut)
def consultar_reembolso(
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

    return reembolso

@router.put("/reembolsos/{reembolso_id}", response_model=ReembolsoOut)
def atualizar_reembolso(
    reembolso_id: int,
    dados: ReembolsoUpdate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user)
):
    exigir_perfil(user, "COLABORADOR")

    reembolso = db.query(Reembolso).filter(
        Reembolso.id == reembolso_id,
        Reembolso.solicitante_id == user.id
    ).first()

    if not reembolso:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")

    if reembolso.situacao != "RASCUNHO":
        raise HTTPException(status_code=409, detail="Somente rascunhos podem ser alterados")

    alteracoes = dados.model_dump(exclude_unset=True)

    nova_data = alteracoes.get("data_despesa", reembolso.data_despesa)
    if nova_data and nova_data > date.today():
        raise HTTPException(status_code=400, detail="Data futura não permitida")

    nova_ref = alteracoes.get("comprovante_ref")
    if nova_ref and db.query(Reembolso).filter(
        Reembolso.solicitante_id == user.id,
        Reembolso.comprovante_ref == nova_ref,
        Reembolso.id != reembolso.id
    ).first():
        raise HTTPException(status_code=409, detail="Comprovante já utilizado")

    for campo, valor in alteracoes.items():
        setattr(reembolso, campo, valor)

    db.commit()
    db.refresh(reembolso)
    return reembolso

@router.delete("/reembolsos/{reembolso_id}")
def excluir_reembolso(
    reembolso_id: int,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user)
):
    exigir_perfil(user, "COLABORADOR")

    reembolso = db.query(Reembolso).filter(
        Reembolso.id == reembolso_id,
        Reembolso.solicitante_id == user.id
    ).first()

    if not reembolso:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")

    if reembolso.situacao != "RASCUNHO":
        raise HTTPException(status_code=409, detail="Somente rascunhos podem ser excluídos")

    db.query(Historico).filter(
        Historico.reembolso_id == reembolso.id
    ).delete()

    db.delete(reembolso)
    db.commit()
    return {"mensagem": "Solicitação excluída"}

@router.post("/reembolsos/{reembolso_id}/enviar")
def enviar_reembolso(
    reembolso_id: int,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user)
):
    exigir_perfil(user, "COLABORADOR")

    reembolso = db.query(Reembolso).filter(
        Reembolso.id == reembolso_id,
        Reembolso.solicitante_id == user.id
    ).first()

    if not reembolso:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")

    if reembolso.situacao != "RASCUNHO":
        raise HTTPException(status_code=409, detail="Solicitação não está em rascunho")

    reembolso.situacao = "AGUARDANDO_GESTOR"
    registrar_historico(db, reembolso, user, "ENVIO", "ENVIADA")
    db.commit()

    return {"mensagem": "Solicitação enviada ao gestor", "situacao": reembolso.situacao}

@router.post("/reembolsos/{reembolso_id}/aprovar")
def aprovar_reembolso(
    reembolso_id: int,
    dados: DecisaoInput,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user)
):
    exigir_perfil(user, "GESTOR", "FINANCEIRO")

    reembolso = db.query(Reembolso).filter(
        Reembolso.id == reembolso_id
    ).first()

    if not reembolso:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")

    if reembolso.solicitante_id == user.id:
        raise HTTPException(status_code=403, detail="Não pode aprovar a própria solicitação")

    if user.perfil == "GESTOR":
        solicitante = db.query(Usuario).filter(
            Usuario.id == reembolso.solicitante_id
        ).first()

        if not solicitante or solicitante.departamento_id != user.departamento_id:
            raise HTTPException(status_code=403, detail="Solicitação de outro departamento")

        if reembolso.situacao != "AGUARDANDO_GESTOR":
            raise HTTPException(status_code=409, detail="Etapa de aprovação do gestor inválida")

        reembolso.situacao = "AGUARDANDO_FINANCEIRO"
        etapa = "GESTOR"

    else:
        if reembolso.situacao != "AGUARDANDO_FINANCEIRO":
            raise HTTPException(status_code=409, detail="Aprovação do gestor ainda não realizada")

        reembolso.situacao = "APROVADA"
        etapa = "FINANCEIRO"

    registrar_historico(
        db, reembolso, user, etapa, "APROVADA", dados.observacao
    )
    db.commit()

    return {"mensagem": "Solicitação aprovada", "situacao": reembolso.situacao}

@router.post("/reembolsos/{reembolso_id}/recusar")
def recusar_reembolso(
    reembolso_id: int,
    dados: DecisaoInput,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user)
):
    exigir_perfil(user, "GESTOR", "FINANCEIRO")

    if not dados.observacao or not dados.observacao.strip():
        raise HTTPException(status_code=400, detail="Justificativa da recusa obrigatória")

    reembolso = db.query(Reembolso).filter(
        Reembolso.id == reembolso_id
    ).first()

    if not reembolso:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")

    if reembolso.solicitante_id == user.id:
        raise HTTPException(status_code=403, detail="Não pode recusar a própria solicitação")

    if user.perfil == "GESTOR":
        solicitante = db.query(Usuario).filter(
            Usuario.id == reembolso.solicitante_id
        ).first()

        if not solicitante or solicitante.departamento_id != user.departamento_id:
            raise HTTPException(status_code=403, detail="Solicitação de outro departamento")

        if reembolso.situacao != "AGUARDANDO_GESTOR":
            raise HTTPException(status_code=409, detail="Etapa do gestor inválida")

        etapa = "GESTOR"

    else:
        if reembolso.situacao != "AGUARDANDO_FINANCEIRO":
            raise HTTPException(status_code=409, detail="Etapa financeira inválida")

        etapa = "FINANCEIRO"

    reembolso.situacao = "RECUSADA"
    registrar_historico(
        db, reembolso, user, etapa, "RECUSADA", dados.observacao
    )
    db.commit()

    return {"mensagem": "Solicitação recusada", "situacao": reembolso.situacao}

@router.post("/reembolsos/{reembolso_id}/pagar")
def pagar_reembolso(
    reembolso_id: int,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user)
):
    exigir_perfil(user, "FINANCEIRO")

    reembolso = db.query(Reembolso).filter(
        Reembolso.id == reembolso_id
    ).first()

    if not reembolso:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")

    if reembolso.situacao != "APROVADA":
        raise HTTPException(status_code=409, detail="Solicitação ainda não está aprovada")

    reembolso.situacao = "PAGA"
    registrar_historico(db, reembolso, user, "PAGAMENTO", "PAGA")
    db.commit()

    return {"mensagem": "Pagamento registrado", "situacao": reembolso.situacao}
