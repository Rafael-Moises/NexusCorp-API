# NexusCorp — Sistema de Gestão de Reembolsos

API REST desenvolvida com Python e FastAPI para registrar, acompanhar, analisar e pagar solicitações de reembolso corporativo.

## Problema e objetivo

A NexusCorp precisa substituir o controle de despesas por planilhas e e-mails por um fluxo auditável, com segregação de acesso por usuário, departamento e perfil.

## Tecnologias

- Python 3.11+
- FastAPI / Uvicorn
- SQLAlchemy
- Pydantic
- SQLite no desenvolvimento; PostgreSQL recomendado em produção
- JWT (Bearer) e hash de senha PBKDF2-HMAC-SHA256 com salt aleatório
- Pytest e TestClient para testes automatizados

## Perfis e fluxo

- **COLABORADOR:** cria, consulta e altera/exclui apenas seus próprios rascunhos; envia solicitações.
- **GESTOR:** analisa solicitações de colaboradores do próprio departamento.
- **FINANCEIRO:** realiza a aprovação final, recusa na etapa financeira e registra pagamento.

Fluxo: `RASCUNHO → AGUARDANDO_GESTOR → AGUARDANDO_FINANCEIRO → APROVADA → PAGA`. A solicitação também pode terminar em `RECUSADA`.

## Estrutura

```text
app/
├── api/v1/routers/   # endpoints por domínio
├── core/             # configuração, segurança e dependências
├── database/         # engine, sessão e dados iniciais
├── models/           # entidades SQLAlchemy
├── schemas/          # contratos Pydantic
├── services/         # serviços de domínio, como auditoria
└── main.py           # composição e inicialização da API
tests/                # suíte automatizada Pytest
docs/                 # matriz, relatório e evidências textuais
```

## Instalação local

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edite `JWT_SECRET_KEY` no `.env` antes de usar fora de ambiente local. Não publique `.env`.

## Banco de dados

O padrão local usa SQLite e cria as tabelas com `Base.metadata.create_all()` na inicialização. O banco `nexuscorp.db` é criado na pasta de execução. Em produção, configure `DATABASE_URL` para PostgreSQL persistente. A aplicação não executa `drop_all()`.

## Executar

```bash
uvicorn app.main:app --reload --port 8001
```

A documentação fica em `http://127.0.0.1:8001/docs`.

## Usuários iniciais de demonstração

Na primeira inicialização de um banco vazio, são provisionados:

| Perfil | E-mail | Senha inicial |
|---|---|---|
| COLABORADOR Comercial | ana@nexuscorp.com | Nexus@123 |
| COLABORADOR Tecnologia | bruno@nexuscorp.com | Nexus@123 |
| GESTOR Comercial | patricia@nexuscorp.com | Nexus@123 |
| GESTOR Tecnologia | carlos@nexuscorp.com | Nexus@123 |
| FINANCEIRO | financeiro@nexuscorp.com | Nexus@123 |

Essas credenciais são exclusivamente para demonstração local. Altere-as e use segredo JWT próprio em produção.

## Endpoints principais

- `POST /auth/login`
- `GET /me` e `GET /usuarios/me`
- `GET/POST /usuarios`
- `GET/POST /departamentos`
- `GET/POST /reembolsos`
- `GET/PUT/DELETE /reembolsos/{id}`
- `POST /reembolsos/{id}/enviar`
- `POST /reembolsos/{id}/aprovar`
- `POST /reembolsos/{id}/recusar`
- `POST /reembolsos/{id}/pagar`
- `GET /historico/{id}`

O contrato atualizado e a segurança Bearer são publicados pelo OpenAPI/Swagger.

## Testes automatizados

```bash
pytest -v
```

A suíte contém 20 casos organizados por autenticação, autorização, CRUD, regras de negócio e validações. Os testes usam banco SQLite isolado em memória e não alteram o banco de desenvolvimento.

## Documentos complementares

- `docs/MATRIZ_DE_PERMISSOES.md`
- `docs/RELATORIO_DE_EVOLUCAO.md`
- `docs/PLANO_DE_DEPLOY.md`

## Deploy

Para publicar, configure em um serviço ASGI o comando `uvicorn app.main:app --host 0.0.0.0 --port $PORT`, as variáveis `DATABASE_URL`, `JWT_SECRET_KEY`, `JWT_ALGORITHM` e `ACCESS_TOKEN_EXPIRE_MINUTES`, e um PostgreSQL persistente. A publicação efetiva depende de configurar o serviço e suas credenciais no provedor escolhido.

## Integrantes

Preencher com os nomes e responsabilidades dos integrantes do grupo antes da entrega final.
