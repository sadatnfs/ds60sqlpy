"""Complete PyTorch route contracts and opt-in prepared-CPU numerical evidence."""
from __future__ import annotations

import ast
import importlib.util
import json
import os
from pathlib import Path
import re
import textwrap

import pytest

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'courses/deep-learning-pytorch'
ENTRIES=json.loads((BASE/'lessons.json').read_text())['lessons']
PLAN={row['id']:row for row in json.loads((BASE/'track.json').read_text())['lessons']}


def reference(lesson_id: str):
    path=BASE/'solutions'/f'{lesson_id}_solution.py'
    spec=importlib.util.spec_from_file_location(lesson_id.replace('-','_'),path)
    assert spec and spec.loader
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_complete_route_has36_real_bundles_and_exact_tensorflow_pairs() -> None:
    assert len(ENTRIES)==len(PLAN)==36
    assert {entry['id'] for entry in ENTRIES}=={f'torch-{i:03d}' for i in range(1,37)}
    for entry in ENTRIES:
        lesson=PLAN[entry['id']]
        paired=f"tf-{int(entry['id'][-3:]):03d}"
        assert lesson['paired_lesson_id']==paired
        assert entry['runtime_profile']==lesson['runtime']
        assert entry['runtime_profile']==('reading' if entry['id']=='torch-001' else 'llm-torch-cpu')
        for relative in [entry['source_path'],entry['guide_path'],*entry['solution_paths']]:
            path=ROOT/relative
            assert path.is_file() and path.resolve().is_relative_to(BASE)
            text=path.read_text()
            assert '\u2014' not in text and '\u200b' not in text
            if path.suffix=='.py':ast.parse(text,filename=relative)
        guide=(ROOT/entry['guide_path']).read_text()
        assert f'../../deep-learning-tensorflow/guides/{paired}.md' in guide
        assert (ROOT/'courses/deep-learning-tensorflow/guides'/f'{paired}.md').is_file()
        assert all(f'### Example {label}:' in guide for label in 'ABC')
        assert '## Interview reasoning with worked answers' in guide
        assert len(re.findall(r'^\s*[1-6]\. \*\*',guide,re.MULTILINE))==6
        assert guide.count('**Expected:**')>=9
        assert entry['guide_path'] in guide and entry['source_path'] in guide
        for prerequisite in lesson['prerequisites']:assert f'`{prerequisite}`' in guide


def test_shared_teaching_depth_and_practice_contracts() -> None:
    from ds60sqlpy.catalog import Catalog,Lesson
    from scripts.audit_lesson_depth import audit
    from scripts.audit_practice import count_practice
    lessons=[]
    for entry in ENTRIES:
        spec=PLAN[entry['id']]
        lessons.append(Lesson(id=entry['id'],track='deep-learning-pytorch',day=int(entry['id'][-3:]),title=spec['title'],level=spec['level'],phase='PyTorch foundations and model evidence',estimated_minutes=spec['minutes'],prerequisites=tuple(spec['prerequisites']),lesson_path=entry['source_path'],guide_path=entry['guide_path'],solution_paths=tuple(entry['solution_paths']),dependency_group='core',network='offline',runner='none' if entry['language']=='markdown' else 'python'))
        for relative in [entry['source_path'],entry['guide_path'],*entry['solution_paths']]:
            assert count_practice(ROOT/relative,solution='/solutions/' in relative)>=6
    catalog=Catalog(ROOT,lessons,tracks={'deep-learning-pytorch':{'title':'Deep learning with PyTorch','plan':'courses/deep-learning-pytorch/README.md'}})
    failures=[(row.lesson_id,row.issues) for row in audit(catalog) if not row.passes]
    assert not failures


@pytest.mark.skipif(os.environ.get('DS60_TEST_TORCH')!='1',reason='Requires the separately prepared PyTorch2.9 CPU runtime')
@pytest.mark.parametrize('lesson_id',[entry['id'] for entry in ENTRIES if entry['language']=='python'])
def test_every_pytorch_reference_executes_six_real_checks(lesson_id: str) -> None:
    assert reference(lesson_id).verify()=={'checks':6,'status':'passed'}


@pytest.mark.parametrize('lesson_id',['torch-028','torch-032','torch-036'])
def test_fresh_process_sources_compile_and_report_child_failures(lesson_id: str) -> None:
    path=BASE/'solutions'/f'{lesson_id}_solution.py';source=path.read_text();tree=ast.parse(source);programs=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.Assign) and any(isinstance(target,ast.Name) and target.id in {'child','program'} for target in node.targets):
            if isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Attribute) and node.value.func.attr=='dedent':
                program=textwrap.dedent(ast.literal_eval(node.value.args[0]));compile(program,f'{lesson_id}-child','exec');programs.append(program)
    assert len(programs)==1
    assert 'result.stderr' in source and 'timeout=60' in source and 'weights_only=True' in source
    assert 'TemporaryDirectory' in source and 'temporary.cleanup()' in source


def test_default_sources_have_no_model_data_or_package_downloads() -> None:
    forbidden=('requests','urllib','huggingface_hub','torchvision','transformers')
    for entry in ENTRIES:
        if entry['language']!='python':continue
        source=(ROOT/entry['solution_paths'][0]).read_text();tree=ast.parse(source)
        imported=set()
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):imported.update(alias.name.split('.')[0] for alias in node.names)
            elif isinstance(node,ast.ImportFrom) and node.module:imported.add(node.module.split('.')[0])
        assert not imported.intersection(forbidden)
        assert 'pip install' not in source and 'torch.hub.load' not in source and 'download=True' not in source
    loader=(BASE/'solutions/torch-015_solution.py').read_text()
    assert 'num_workers=0' in loader


@pytest.mark.skipif(os.environ.get('DS60_TEST_TORCH')!='1',reason='Requires prepared PyTorch CPU runtime')
def test_attention_rejects_mask_errors_and_preserves_nonuniform_prefixes() -> None:
    import torch
    module=reference('torch-022')
    q=torch.tensor([[1.,2.],[0.,1.],[2.,-1.]],dtype=torch.float64)
    k=torch.tensor([[2.,0.],[1.,1.],[-1.,2.]],dtype=torch.float64)
    v=torch.tensor([[1.,3.],[2.,4.],[5.,7.]],dtype=torch.float64)
    allowed=torch.ones((3,3),dtype=torch.bool).tril()
    full=module.attention(q,k,v,allowed)
    torch.testing.assert_close(module.attention(q[:2],k[:2],v[:2],allowed[:2,:2]),full[:2],atol=1e-12,rtol=0)
    with pytest.raises(TypeError):module.attention(q,k,v,allowed.long())
    broken=allowed.clone();broken[0]=False
    with pytest.raises(ValueError):module.attention(q,k,v,broken)


@pytest.mark.skipif(os.environ.get('DS60_TEST_TORCH')!='1',reason='Requires prepared PyTorch CPU runtime')
def test_gradcheck_detects_a_wrong_custom_backward_rule() -> None:
    import torch
    module=reference('torch-026')
    class WrongCube(torch.autograd.Function):
        @staticmethod
        def forward(ctx,x):ctx.save_for_backward(x);return x**3
        @staticmethod
        def backward(ctx,incoming):
            (x,)=ctx.saved_tensors
            return incoming*2*x
    values=torch.tensor([.2,-.7],dtype=torch.float64,requires_grad=True)
    assert torch.autograd.gradcheck(module.Cube.apply,(values,))
    assert not torch.autograd.gradcheck(WrongCube.apply,(values,),raise_exception=False)


@pytest.mark.skipif(os.environ.get('DS60_TEST_TORCH')!='1',reason='Requires prepared PyTorch CPU runtime')
def test_inference_contract_rejects_silent_coercion_and_preserves_ownership() -> None:
    import torch
    module=reference('torch-033')
    values=torch.tensor([[2.,1.],[4.,3.]],dtype=torch.float32);before=values.clone()
    output=module.predict(values);assert output.tolist()==[3.,5.]
    output[0]=999;assert torch.equal(values,before)
    with pytest.raises(TypeError):module.predict(values.double())
    with pytest.raises(ValueError):module.predict(torch.empty((0,2)))
    with pytest.raises(ValueError):module.predict(torch.tensor([[float('inf'),1.]]))
