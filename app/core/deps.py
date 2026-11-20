
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.database.database import SessionLocal
from app.core.config import JWT_SECRET_KEY, JWT_ALGORITHM
from app.models.db_models import Usuario, Reembolso


bearer = HTTPBearer(auto_error=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db)
):
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Token ausente, inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )

        user_id = int(payload.get("sub"))

    except (JWTError, ValueError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Token inválido ou expirado"
        )

    user = db.query(Usuario).filter(
        Usuario.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Usuário não encontrado"
        )

    return user


def exigir_perfil(user: Usuario, *perfis):
    if user.perfil not in perfis:
        raise HTTPException(
            status_code=403,
            detail="Você não possui permissão para esta operação"
        )


def verificar_acesso(reembolso: Reembolso, user: Usuario):
    if user.perfil == "FINANCEIRO":
        return

    if reembolso.solicitante_id != user.id:
        raise HTTPException(
            status_code=404,
            detail="Solicitação não encontrada"
        )
