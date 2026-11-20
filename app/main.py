from fastapi import FastAPI
from app.database.database import Base, engine
from app.database.seed import inicializar_dados
from app.models import db_models  # registra todas as entidades no metadata
from app.api.v1.api import api_router

app = FastAPI(
    title="NexusCorp | Sistema de Gestão de Reembolsos",
    description="API REST para gestão de reembolsos corporativos, com perfis COLABORADOR, GESTOR e FINANCEIRO, autenticação JWT, aprovação por departamento e histórico de auditoria.",
    version="2.0.0",
    openapi_tags=[
        {"name":"Geral","description":"Informações gerais."},
        {"name":"Autenticação","description":"Login e identificação."},
        {"name":"Usuários","description":"Gestão de usuários."},
        {"name":"Departamentos","description":"Departamentos corporativos."},
        {"name":"Reembolsos","description":"Cadastro e fluxo de aprovação."},
        {"name":"Histórico","description":"Auditoria das decisões."}
    ]
)

Base.metadata.create_all(bind=engine)
inicializar_dados()
app.include_router(api_router)
