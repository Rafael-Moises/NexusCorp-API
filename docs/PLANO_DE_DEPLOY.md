# Plano de publicação

A publicação não é executada automaticamente pelo código-fonte. No provedor escolhido:

1. Criar serviço web Python conectado ao repositório.
2. Build: `pip install -r requirements.txt`.
3. Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
4. Provisionar PostgreSQL persistente e configurar `DATABASE_URL`.
5. Configurar `JWT_SECRET_KEY` aleatória, `JWT_ALGORITHM=HS256` e `ACCESS_TOKEN_EXPIRE_MINUTES=60`.
6. Confirmar HTTPS, abrir `/docs`, autenticar e validar CRUD e permissões.

Não usar SQLite em disco efêmero do provedor para a versão de produção. Nunca cadastrar o conteúdo do `.env` no Git.
