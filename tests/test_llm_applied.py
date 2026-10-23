"""Task-specific correctness and teaching contracts for applied LLM lessons."""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'courses/llm-applied'
ENTRIES = json.loads((BASE / 'lessons.json').read_text())['lessons']


def load(lesson_id: str):
    path = BASE / 'solutions' / f'{lesson_id}_solution.py'
    spec = importlib.util.spec_from_file_location(lesson_id.replace('-', '_'), path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_applied_route_is_complete_and_profiles_are_explicit() -> None:
    plan = json.loads((BASE / 'track.json').read_text())
    assert len(ENTRIES) == len(plan['lessons']) == 24
    assert {entry['id'] for entry in ENTRIES} == {f'llm-applied-{i:03d}' for i in range(1, 25)}
    planned = {item['id']: item for item in plan['lessons']}
    for entry in ENTRIES:
        assert entry['runtime_profile'] == planned[entry['id']]['runtime']
        assert entry['status'] == 'authored'
        for relative in [entry['source_path'], entry['guide_path'], *entry['solution_paths']]:
            path = ROOT / relative
            assert path.is_file() and path.resolve().is_relative_to(BASE)
            text = path.read_text()
            assert '\u2014' not in text
            if path.suffix == '.py':
                ast.parse(text, filename=relative)
        guide = (ROOT / entry['guide_path']).read_text()
        assert all(f'### Example {label}:' in guide for label in 'ABC')
        assert len(re.findall(r'^\s*[1-6]\. \*\*', guide, re.MULTILINE)) == 6
        assert guide.count('**Expected:**') >= 9
        assert entry['guide_path'] in guide and entry['source_path'] in guide


@pytest.mark.parametrize('lesson_id', [e['id'] for e in ENTRIES if e['runtime_profile'] == 'python-core'])
def test_core_reference_exercises_execute(lesson_id: str) -> None:
    assert load(lesson_id).verify() == {'checks': 6, 'status': 'passed'}


@pytest.mark.skipif(os.environ.get('DS60_TEST_TORCH') != '1', reason='Requires separately prepared PyTorch CPU runtime')
@pytest.mark.parametrize('lesson_id', [e['id'] for e in ENTRIES if e['runtime_profile'] == 'llm-torch-cpu'])
def test_actual_torch_adaptation_references(lesson_id: str) -> None:
    assert load(lesson_id).verify() == {'checks': 6, 'status': 'passed'}


def test_shared_depth_and_practice_contracts() -> None:
    from ds60sqlpy.catalog import Catalog, Lesson
    from scripts.audit_lesson_depth import audit
    from scripts.audit_practice import count_practice

    plan = {item['id']: item for item in json.loads((BASE / 'track.json').read_text())['lessons']}
    lessons = []
    for entry in ENTRIES:
        spec = plan[entry['id']]
        lessons.append(Lesson(
            id=entry['id'], track='llm-applied', day=int(entry['id'][-3:]), title=spec['title'],
            level=spec['level'], phase='Applied LLM systems', estimated_minutes=spec['minutes'],
            prerequisites=tuple(spec['prerequisites']), lesson_path=entry['source_path'],
            guide_path=entry['guide_path'], solution_paths=tuple(entry['solution_paths']),
            dependency_group='core', network='offline',
            runner='none' if entry['language'] == 'markdown' else 'python',
        ))
        for relative in [entry['source_path'], entry['guide_path'], *entry['solution_paths']]:
            assert count_practice(ROOT / relative, solution='/solutions/' in relative) >= 6
    catalog = Catalog(ROOT, lessons, tracks={'llm-applied': {'title': 'Applied LLMs', 'plan': 'courses/llm-applied/README.md'}})
    failures = [(row.lesson_id, row.issues) for row in audit(catalog) if not row.passes]
    assert not failures


def test_chunk_offsets_preserve_source_bytes_and_overlap_is_bounded() -> None:
    module = load('llm-applied-005')
    text = 'alpha\tβeta  gamma\ndelta'
    chunks = module.chunk(text, 'd', 3, 2, 1)
    assert [c['text'] for c in chunks] == ['alpha\tβeta', 'βeta  gamma', 'gamma\ndelta']
    assert all(text[c['start']:c['end']] == c['text'] for c in chunks)
    assert all(c['version'] == 3 and c['document_id'] == 'd' for c in chunks)
    for size, overlap in [(1, 1), (2, -1), (False, 0)]:
        with pytest.raises(ValueError):
            module.chunk(text, 'd', 3, size, overlap)


def test_bm25_matches_an_independent_single_term_calculation() -> None:
    import math
    module = load('llm-applied-006')
    scores = dict(module.bm25('rare', {'a': 'rare rare', 'b': 'other other'}))
    idf = math.log(1 + (2 - 1 + .5) / (1 + .5))
    expected = idf * 2 * (1.2 + 1) / (2 + 1.2)
    assert scores['a'] == pytest.approx(expected, abs=1e-12) and scores['b'] == 0
    assert module.bm25('rare rare', {'a': 'rare rare', 'b': 'other other'}) == module.bm25('rare', {'a': 'rare rare', 'b': 'other other'})


def test_embedding_rank_rejects_wrong_dimension_and_zero_norm() -> None:
    module = load('llm-applied-007')
    with pytest.raises(ValueError, match='dimensions'):
        module.cosine_rank([1, 0], {'d': [1, 0, 0]})
    with pytest.raises(ValueError, match='norm'):
        module.unit([0, 0])
    np.testing.assert_allclose(module.unit([3, 4]), [.6, .8], atol=1e-12, rtol=0)


def test_rrf_cannot_gain_votes_from_duplicate_ids() -> None:
    module = load('llm-applied-008')
    original = module.rrf([['b', 'a'], ['a', 'c']], 10)
    repeated = module.rrf([['b', 'b', 'a', 'a'], ['a', 'c', 'c']], 10)
    assert repeated == original
    scores = dict(original)
    assert scores['a'] == pytest.approx(1 / 12 + 1 / 11, abs=1e-12)


def test_access_policy_is_applied_before_context_and_cache_identity() -> None:
    module = load('llm-applied-009')
    public = module.admit(module.DOCUMENTS, {'public'})
    assert all(doc['scope'] == 'public' for doc in public)
    assert 'private-v1' not in {doc['id'] for doc in public}
    key = module.cache_key('same', {'public'}, 'v1', 'r1')
    assert key != module.cache_key('same', {'public', 'restricted'}, 'v1', 'r1')
    assert key != module.cache_key('same', {'public'}, 'v2', 'r1')
    assert key == module.cache_key('same', set(['public']), 'v1', 'r1')


def test_multihop_traversal_bounds_cycles_and_unauthorized_targets() -> None:
    module = load('llm-applied-010')
    graph = {'a': ['b', 'secret'], 'b': ['a', 'c'], 'c': []}
    assert module.walk('a', graph, 1) == ['a', 'b']
    assert module.walk('a', graph, 10) == ['a', 'b', 'c']
    assert module.walk('absent', graph, 10) == []
    with pytest.raises(ValueError):
        module.walk('a', graph, -1)


def test_sft_target_mask_handles_truncation_without_double_shift() -> None:
    module = load('llm-applied-014')
    inputs, labels = module.prepare([1, 2, 3], [4, 5, 6], 5)
    assert inputs == [1, 2, 3, 4] and labels == [-100, -100, 4, 5]
    with pytest.raises(ValueError, match='truncation'):
        module.prepare([1, 2, 3], [4], 3)
    with pytest.raises(ValueError, match='integer'):
        module.prepare([True], [2], 5)


def test_capstone_public_unknown_does_not_reveal_restricted_identity() -> None:
    module = load('llm-applied-024')
    assistant = module.Assistant(module.DOCUMENTS, {'public'}, 'v1')
    result = assistant.answer('restricted_threshold')
    assert result['status'] == 'unknown'
    assert 'private-v1' not in json.dumps(result) and 'seven' not in json.dumps(result)
    with pytest.raises(ValueError):
        module.conversion(True, 1)
    with pytest.raises(ValueError):
        module.conversion(0, 0)


def _optional_module(name: str):
    folder = BASE / 'fixtures/pretrained'
    spec = importlib.util.spec_from_file_location(name, folder / f'{name}.py')
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(folder))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
    return module


def test_optional_asset_verifier_detects_tampering_without_loading_a_model(tmp_path: Path) -> None:
    module = _optional_module('verify_assets')
    contract = json.loads((BASE / 'fixtures/pretrained/asset_contract.json').read_text())
    payload = b'not model weights; hash-verification fixture only'
    (tmp_path / 'fixture.safetensors').write_bytes(payload)
    manifest = {**contract, 'files': {'fixture.safetensors': hashlib.sha256(payload).hexdigest()}}
    (tmp_path / 'course-assets.json').write_text(json.dumps(manifest))
    assert module.verify_assets(tmp_path)['revision'] == contract['revision']
    (tmp_path / 'fixture.safetensors').write_bytes(b'changed')
    with pytest.raises(ValueError, match='hash mismatch'):
        module.verify_assets(tmp_path)


def test_optional_dataset_families_are_disjoint_and_messages_are_valid() -> None:
    module = _optional_module('train_local')
    folder = BASE / 'fixtures/pretrained'
    training = module.read_records(folder / 'train.jsonl')
    evaluation = module.read_records(folder / 'eval.jsonl')
    assert len(training) == 4 and len(evaluation) == 1
    assert not {row['family'] for row in training} & {row['family'] for row in evaluation}


def test_optional_scripts_are_local_only_except_explicit_acquisition_entrypoint() -> None:
    folder = BASE / 'fixtures/pretrained'
    for path in folder.glob('*.py'):
        ast.parse(path.read_text(), filename=path.name)
    for name in ['train_local.py', 'infer_local.py']:
        source = (folder / name).read_text()
        tree = ast.parse(source)
        loads = [node for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'from_pretrained']
        assert loads
        for call in loads:
            keywords = {keyword.arg: keyword.value for keyword in call.keywords}
            assert isinstance(keywords.get('local_files_only'), ast.Constant) and keywords['local_files_only'].value is True
        assert 'snapshot_download' not in source
        assert "os.environ['HF_HUB_OFFLINE'] = '1'" in source
    acquisition = (folder / 'prepare_assets.py').read_text()
    assert '--acknowledge-network' in acquisition and 'if not args.acknowledge_network' in acquisition
    assert 'revision=contract' in acquisition
    assert not any(path.suffix in {'.safetensors', '.bin', '.pt'} for path in folder.rglob('*'))


def test_optional_training_checks_masks_before_train_and_records_only_actual_execution() -> None:
    source = (BASE / 'fixtures/pretrained/train_local.py').read_text()
    assert source.index('completion_mask') < source.index('trainer.train()')
    assert source.index("batch['labels']") < source.index('trainer.train()')
    assert "max_steps=10" in source and "max_length=128" in source
    assert source.index("'status': 'executed'") > source.index('trainer.train()')
    assert not (BASE / 'fixtures/pretrained/receipt.json').exists()
