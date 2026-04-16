import urllib.request
import json

req = urllib.request.Request(
    'http://localhost:5000/api/process',
    data=json.dumps({'command': 'mask salary in employee table for analyst role'}).encode(),
    headers={'Content-Type': 'application/json'},
    method='POST'
)
with urllib.request.urlopen(req, timeout=60) as r:
    print('Status:', r.status)
    body = r.read().decode()
    print(body[:1200])
