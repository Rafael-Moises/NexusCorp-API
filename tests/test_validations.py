def test_cadastro_sem_campos_obrigatorios_retorna_422(client,tokens):
    r=client.post('/reembolsos',json={'categoria':'Transporte'},headers=tokens['ana@test.com'])
    assert r.status_code==422

def test_valor_zero_retorna_422(client,tokens,payload):
    payload['valor']=0
    r=client.post('/reembolsos',json=payload,headers=tokens['ana@test.com'])
    assert r.status_code==422
