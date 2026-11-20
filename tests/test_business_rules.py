def test_comprovante_duplicado_impedido(client,tokens,payload):
    client.post('/reembolsos',json=payload,headers=tokens['ana@test.com'])
    r=client.post('/reembolsos',json=payload,headers=tokens['ana@test.com'])
    assert r.status_code==409

def test_data_futura_impedida(client,tokens,payload):
    payload['data_despesa']='2999-01-01'
    assert client.post('/reembolsos',json=payload,headers=tokens['ana@test.com']).status_code==400

def test_edicao_apos_envio_impedida(client,tokens,payload):
    rid=client.post('/reembolsos',json=payload,headers=tokens['ana@test.com']).json()['id']
    client.post(f'/reembolsos/{rid}/enviar',headers=tokens['ana@test.com'])
    assert client.put(f'/reembolsos/{rid}',json={'justificativa':'alterada'},headers=tokens['ana@test.com']).status_code==409

def test_envio_muda_status_para_aguardando_gestor(client,tokens,payload):
    rid=client.post('/reembolsos',json=payload,headers=tokens['ana@test.com']).json()['id']
    r=client.post(f'/reembolsos/{rid}/enviar',headers=tokens['ana@test.com'])
    assert r.status_code==200 and r.json()['situacao']=='AGUARDANDO_GESTOR'

def test_gestor_aprova_e_encaminha_financeiro(client,tokens,payload):
    rid=client.post('/reembolsos',json=payload,headers=tokens['ana@test.com']).json()['id']
    client.post(f'/reembolsos/{rid}/enviar',headers=tokens['ana@test.com'])
    r=client.post(f'/reembolsos/{rid}/aprovar',json={'observacao':'Conferido'},headers=tokens['patricia@test.com'])
    assert r.status_code==200 and r.json()['situacao']=='AGUARDANDO_FINANCEIRO'

def test_financeiro_nao_aprova_antes_do_gestor(client,tokens,payload):
    rid=client.post('/reembolsos',json=payload,headers=tokens['ana@test.com']).json()['id']
    client.post(f'/reembolsos/{rid}/enviar',headers=tokens['ana@test.com'])
    r=client.post(f'/reembolsos/{rid}/aprovar',json={'observacao':'ok'},headers=tokens['fin@test.com'])
    assert r.status_code==409
