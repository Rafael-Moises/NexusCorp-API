
from datetime import datetime, timezone

from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime,
    ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship

from app.database.database import Base


class Departamento(Base):
    __tablename__ = "departamentos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), unique=True, nullable=False)


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    senha_hash = Column(String(300), nullable=False)
    perfil = Column(String(30), nullable=False)
    departamento_id = Column(
        Integer,
        ForeignKey("departamentos.id"),
        nullable=True
    )

    departamento = relationship("Departamento")


class Reembolso(Base):
    __tablename__ = "reembolsos"

    __table_args__ = (
        UniqueConstraint(
            "solicitante_id",
            "comprovante_ref",
            name="uq_comprovante_solicitante"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    solicitante_id = Column(
        Integer,
        ForeignKey("usuarios.id"),
        nullable=False
    )
    categoria = Column(String(50), nullable=False)
    valor = Column(Float, nullable=False)
    data_despesa = Column(Date, nullable=False)
    justificativa = Column(String(500), nullable=False)
    comprovante_ref = Column(String(150), nullable=False)
    situacao = Column(String(40), default="RASCUNHO", nullable=False)

    solicitante = relationship(
        "Usuario",
        foreign_keys=[solicitante_id]
    )


class Historico(Base):
    __tablename__ = "historico_analises"

    id = Column(Integer, primary_key=True, index=True)
    reembolso_id = Column(
        Integer,
        ForeignKey("reembolsos.id"),
        nullable=False
    )
    responsavel_id = Column(
        Integer,
        ForeignKey("usuarios.id"),
        nullable=False
    )
    etapa = Column(String(50), nullable=False)
    decisao = Column(String(50), nullable=False)
    data_decisao = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    observacao = Column(String(500), nullable=True)
