"""Explicit optional connected acquisition. Never called by a default lesson."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--destination', type=Path, required=True)
    parser.add_argument('--acknowledge-network', action='store_true')
    args = parser.parse_args()
    if not args.acknowledge_network:
        parser.error('Connected model acquisition requires --acknowledge-network')
    destination = args.destination.resolve()
    if destination.exists():
        parser.error('Choose a new directory; existing artifacts are preserved')
    contract = json.loads((Path(__file__).parent / 'asset_contract.json').read_text())
    from huggingface_hub import snapshot_download
    snapshot_download(
        repo_id=contract['model_id'], revision=contract['revision'],
        local_dir=str(destination),
        allow_patterns=['*.json', '*.safetensors', '*.model', '*.txt', 'README.md', 'LICENSE*'],
    )
    hashes = {}
    for path in sorted(destination.rglob('*')):
        if path.is_file() and '.cache' not in path.relative_to(destination).parts:
            hashes[path.relative_to(destination).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    if not hashes or not any(name.endswith('.safetensors') for name in hashes):
        raise RuntimeError('Expected local safetensors weights were not acquired')
    manifest = {**contract, 'files': hashes, 'acquisition': 'explicit human-invoked connected step'}
    (destination / 'course-assets.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'files_recorded': len(hashes), 'revision': contract['revision']}))


if __name__ == '__main__':
    main()
