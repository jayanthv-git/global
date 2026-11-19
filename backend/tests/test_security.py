from .conftest import headers

def test_no_store_headers(client):
    r=client.get('/api/audit',headers=headers())
    assert r.headers['cache-control']=='no-store'
    assert r.headers['x-content-type-options']=='nosniff'
def test_untrusted_host_and_cross_origin_writes(client):
    assert client.get('/api/health',headers={'Host':'attacker.example'}).status_code==400
    assert client.post('/api/demo/session',json={'persona':'adult'},headers={'Origin':'https://attacker.example'}).status_code==403
