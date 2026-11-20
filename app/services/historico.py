from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.models.db_models import Historico, Reembolso, Usuario

def registrar_historico(
    db: Session,
    reembolso: Reembolso,
    user: Usuario,
    etapa: str,
    decisao: str,
    observacao: Optional[str] = None
):
    registro = Historico(
        reembolso_id=reembolso.id,
        responsavel_id=user.id,
        etapa=etapa,
        decisao=decisao,
        observacao=observacao,
        data_decisao=datetime.now(timezone.utc)
    )
    db.add(registro)
