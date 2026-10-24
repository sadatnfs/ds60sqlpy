"""Offline consistency checks. No API calls or runtime qualification claims."""
from pathlib import Path
from ipaddress import ip_address, ip_network
import json
import yaml

BASE = Path(__file__).resolve().parent


def check() -> dict[str, object]:
    data = json.loads((BASE / 'topology.json').read_text(encoding='utf-8'))
    pods = ip_network(data['pod_cidr'])
    services = ip_network(data['service_cidr'])
    assert not pods.overlaps(services)
    assert ip_address(data['service']['ip']) in services
    nodes = {node['id'] for node in data['nodes']}
    ready = []
    for pod in data['pods']:
        assert ip_address(pod['ip']) in pods
        assert pod['node'] in nodes
        assert all(pod['labels'].get(k) == v for k, v in data['service']['selector'].items())
        assert pod['ports'][data['service']['target_port_name']] == data['service']['target_port']
        if pod['ready']:
            ready.append(pod['uid'])
    assert ready == ['pod-a']
    for case in data['client_cases']:
        allowed = (case['namespace_labels'].get('study-role') == 'client' and case['pod_labels'].get('role') == 'tester' and case['source_egress_allowed'])
        assert allowed is case['expected']
    documents = {}
    for path in sorted(BASE.glob('*.yaml')):
        parsed = list(yaml.safe_load_all(path.read_text(encoding='utf-8')))
        assert all(obj['apiVersion'] and obj['kind'] and obj['metadata']['name'] for obj in parsed)
        assert all('namespace' not in obj['metadata'] and 'status' not in obj for obj in parsed)
        documents[path.name] = parsed
    service = documents['service.yaml'][0]['spec']
    deployment = documents['deployment.yaml'][0]['spec']['template']
    assert all(deployment['metadata']['labels'][k] == v for k, v in service['selector'].items())
    assert service['ports'][0]['targetPort'] == deployment['spec']['containers'][0]['ports'][0]['name']
    assert documents['headless.yaml'][0]['spec']['clusterIP'] == 'None'
    peer = documents['network-policy.yaml'][0]['spec']['ingress'][0]['from'][0]
    assert set(peer) == {'namespaceSelector', 'podSelector'}
    assert documents['dual-stack-service.yaml'][0]['spec']['ipFamilyPolicy'] == 'RequireDualStack'
    return {'status': 'passed', 'scope': 'offline synthetic consistency only', 'api_calls': 0, 'ready_fixture_uids': ready, 'manifest_documents': sum(map(len, documents.values()))}


if __name__ == '__main__':
    print(json.dumps(check(), sort_keys=True))
