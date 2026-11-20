import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database.database import Base
from app.core.deps import get_db
from app.models.db_models import Departamento, Usuario
from app.core.security import hash_password, create_token

@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSession()
    comercial = Departamento(nome="Comercial")
    tecnologia = Departamento(nome="Tecnologia")
    db.add_all([comercial, tecnologia]); db.commit()
    db.refresh(comercial); db.refresh(tecnologia)
    users = [
        Usuario(nome="Ana", email="ana@test.com", senha_hash=hash_password("Senha@123"), perfil="COLABORADOR", departamento_id=comercial.id),
        Usuario(nome="Bruno", email="bruno@test.com", senha_hash=hash_password("Senha@123"), perfil="COLABORADOR", departamento_id=tecnologia.id),
        Usuario(nome="Patricia", email="patricia@test.com", senha_hash=hash_password("Senha@123"), perfil="GESTOR", departamento_id=comercial.id),
        Usuario(nome="Carlos", email="carlos@test.com", senha_hash=hash_password("Senha@123"), perfil="GESTOR", departamento_id=tecnologia.id),
        Usuario(nome="Financeiro", email="fin@test.com", senha_hash=hash_password("Senha@123"), perfil="FINANCEIRO", departamento_id=None),
    ]
    db.add_all(users); db.commit()
    yield db
    db.close(); Base.metadata.drop_all(bind=engine); engine.dispose()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try: yield db_session
        finally: pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def tokens(db_session):
    users = {u.email: u for u in db_session.query(Usuario).all()}
    return {email: {"Authorization": f"Bearer {create_token(user.id)}"} for email, user in users.items()}

@pytest.fixture
def payload():
    from datetime import date
    return {"categoria":"Transporte", "valor":85.5, "data_despesa":date.today().isoformat(), "justificativa":"Deslocamento de trabalho", "comprovante_ref":"REC-001"}
