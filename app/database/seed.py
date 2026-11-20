from app.database.database import SessionLocal
from app.models.db_models import Departamento, Usuario
from app.core.security import hash_password

def inicializar_dados():
    db = SessionLocal()
    try:
        if db.query(Usuario).count() == 0:
            comercial = Departamento(nome="Comercial")
            tecnologia = Departamento(nome="Tecnologia")
            db.add_all([comercial, tecnologia])
            db.commit()
            db.refresh(comercial)
            db.refresh(tecnologia)

            usuarios = [
                Usuario(
                    nome="Ana Colaboradora",
                    email="ana@nexuscorp.com",
                    senha_hash=hash_password("Nexus@123"),
                    perfil="COLABORADOR",
                    departamento_id=comercial.id
                ),
                Usuario(
                    nome="Bruno Colaborador",
                    email="bruno@nexuscorp.com",
                    senha_hash=hash_password("Nexus@123"),
                    perfil="COLABORADOR",
                    departamento_id=tecnologia.id
                ),
                Usuario(
                    nome="Patricia Gestora",
                    email="patricia@nexuscorp.com",
                    senha_hash=hash_password("Nexus@123"),
                    perfil="GESTOR",
                    departamento_id=comercial.id
                ),
                Usuario(
                    nome="Carlos Gestor",
                    email="carlos@nexuscorp.com",
                    senha_hash=hash_password("Nexus@123"),
                    perfil="GESTOR",
                    departamento_id=tecnologia.id
                ),
                Usuario(
                    nome="Financeiro NexusCorp",
                    email="financeiro@nexuscorp.com",
                    senha_hash=hash_password("Nexus@123"),
                    perfil="FINANCEIRO",
                    departamento_id=None
                )
            ]

            db.add_all(usuarios)
            db.commit()
    finally:
        db.close()
