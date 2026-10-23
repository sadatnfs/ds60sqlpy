import hashlib,json
from pathlib import Path

def main():
    base=Path(__file__).resolve().parents[1]/'fixtures/provenance'
    statement=json.loads((base/'attestation.json').read_text())
    content=b'fixture-bytes-v1'
    assert hashlib.sha256(content).hexdigest()==statement['content_sha256']
    assert hashlib.sha256(content+b'!').hexdigest()!=statement['content_sha256']
    assert (base/'attestation.json').read_bytes()!=(base/'attestation-tampered.json').read_bytes()
    assert b'PRIVATE KEY' not in (base/'publisher-public.txt').read_bytes()
    print('k8s-038 content-hash checks passed; use the documented qualified CLI for signature verification')

if __name__ == "__main__":
    main()
