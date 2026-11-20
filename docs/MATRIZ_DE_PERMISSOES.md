# Matriz de permissões — NexusCorp

| Recurso/operação | COLABORADOR | GESTOR | FINANCEIRO |
|---|---|---|---|
| Consultar próprios reembolsos | Sim | — | Sim |
| Consultar reembolsos do departamento | Não | Sim | Sim |
| Criar reembolso | Sim | Não | Não |
| Alterar/excluir rascunho próprio | Sim | Não | Não |
| Enviar reembolso próprio | Sim | Não | Não |
| Aprovar etapa do gestor | Não | Sim, próprio departamento | Não |
| Aprovar etapa financeira | Não | Não | Sim |
| Recusar na etapa correspondente | Não | Sim, próprio departamento | Sim |
| Registrar pagamento | Não | Não | Sim |
| Criar/listar usuários | Não | Não | Sim |
| Criar departamento | Não | Não | Sim |
| Consultar histórico | Próprio | Próprio departamento | Sim |

## Controles implementados

- Autenticação Bearer/JWT nas operações protegidas.
- Colaborador consulta apenas recursos de sua titularidade; recurso alheio retorna 404.
- Gestor consulta e decide somente sobre solicitações do seu departamento.
- Financeiro realiza a etapa final e pagamentos.
- Criação de usuários e atribuição de perfis é restrita ao FINANCEIRO.
- A alteração/exclusão é permitida somente enquanto o reembolso está em RASCUNHO.
- A sequência de aprovação é validada no servidor.

## Códigos HTTP de autorização

- `401`: ausência ou invalidade da autenticação.
- `403`: usuário autenticado sem permissão para a operação.
- `404`: recurso inexistente ou não pertencente ao colaborador.
- `409`: conflito com o estado atual ou duplicidade.
