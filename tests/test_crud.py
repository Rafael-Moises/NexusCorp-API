def test_criar_reembolso(client,tokens,payload):
    r=client.post('/reembolsos',json=payload,headers=tokens['ana@test.com'])
    assert r.status_code==201 and r.json()['situacao']=='RASCUNHO'

def test_listar_reembolsos_retorna_apenas_proprios(client,tokens,payload):
    client.post('/reembolsos',json=payload,headers=tokens['bruno@test.com'])
    r=client.get('/reembolsos',headers=tokens['ana@test.com'])
    assert r.status_code==200 and r.json()==[]

def test_atualizar_rascunho(client,tokens,payload):
    rid=client.post('/reembolsos',json=payload,headers=tokens['ana@test.com']).json()['id']
    r=client.put(f'/reembolsos/{rid}',json={'justificativa':'Texto atualizado'},headers=tokens['ana@test.com'])
    assert r.status_code==200 and r.json()['justificativa']=='Texto atualizado'

def test_excluir_rascunho(client,tokens,payload):
    rid=client.post('/reembolsos',json=payload,headers=tokens['ana@test.com']).json()['id']
    r=client.delete(f'/reembolsos/{rid}',headers=tokens['ana@test.com'])
    assert r.status_code==200 and r.json()['mensagem']=='Solicitação excluída'
