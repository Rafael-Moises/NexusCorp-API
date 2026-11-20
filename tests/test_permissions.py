def test_colaborador_nao_lista_usuarios(client,tokens):
    assert client.get('/usuarios',headers=tokens['ana@test.com']).status_code==403

def test_colaborador_consulta_proprio_reembolso(client,tokens,payload):
    rid=client.post('/reembolsos',json=payload,headers=tokens['ana@test.com']).json()['id']
    assert client.get(f'/reembolsos/{rid}',headers=tokens['ana@test.com']).status_code==200

def test_colaborador_nao_acessa_reembolso_alheio(client,tokens,payload):
    rid=client.post('/reembolsos',json=payload,headers=tokens['bruno@test.com']).json()['id']
    assert client.get(f'/reembolsos/{rid}',headers=tokens['ana@test.com']).status_code==404

def test_gestor_de_outro_departamento_nao_aprova(client,tokens,payload):
    rid=client.post('/reembolsos',json=payload,headers=tokens['bruno@test.com']).json()['id']
    client.post(f'/reembolsos/{rid}/enviar',headers=tokens['bruno@test.com'])
    r=client.post(f'/reembolsos/{rid}/aprovar',json={'observacao':'ok'},headers=tokens['patricia@test.com'])
    assert r.status_code==403
