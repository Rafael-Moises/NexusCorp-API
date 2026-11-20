from datetime import date
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict

class Login(BaseModel):
    email: str
    senha: str

class UsuarioCreate(BaseModel):
    nome: str
    email: str
    senha: str = Field(min_length=6)
    perfil: Literal["COLABORADOR", "GESTOR", "FINANCEIRO"]
    departamento_id: Optional[int] = None

class UsuarioOut(BaseModel):
    id: int
    nome: str
    email: str
    perfil: str
    departamento_id: Optional[int]

    model_config = ConfigDict(from_attributes=True)

class DepartamentoCreate(BaseModel):
    nome: str

class ReembolsoCreate(BaseModel):
    categoria: str
    valor: float = Field(gt=0)
    data_despesa: date
    justificativa: str
    comprovante_ref: str

class ReembolsoUpdate(BaseModel):
    categoria: Optional[str] = None
    valor: Optional[float] = Field(default=None, gt=0)
    data_despesa: Optional[date] = None
    justificativa: Optional[str] = None
    comprovante_ref: Optional[str] = None

class ReembolsoOut(BaseModel):
    id: int
    solicitante_id: int
    categoria: str
    valor: float
    data_despesa: date
    justificativa: str
    comprovante_ref: str
    situacao: str

    model_config = ConfigDict(from_attributes=True)

class DecisaoInput(BaseModel):
    observacao: Optional[str] = None
