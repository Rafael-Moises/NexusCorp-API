def test_login_valido_retorna_jwt(client):
    r=client.post('/auth/login',json={'email':'ana@test.com','senha':'Senha@123'})
    assert r.status_code==200 and r.json()['token_type']=='bearer' and r.json()['access_token']

def test_senha_incorreta_rejeitada(client):
    r=client.post('/auth/login',json={'email':'ana@test.com','senha':'errada'})
    assert r.status_code==401

def test_token_ausente_rejeitado(client):
    r=client.get('/me')
    assert r.status_code==401

def test_token_invalido_rejeitado(client):
    r=client.get('/me',headers={'Authorization':'Bearer token-invalido'})
    assert r.status_code==401
