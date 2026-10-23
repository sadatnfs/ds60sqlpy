"""Authored Java teaching contracts and opt-in real JDK21 reference execution."""
from __future__ import annotations
import json
import os
from pathlib import Path
import re
import subprocess

import pytest

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'courses/java'
ENTRIES=json.loads((BASE/'lessons.json').read_text())['lessons']


def test_authored_java_bundles_follow_reviewed_plan_and_preserve_solutions() -> None:
    planned={item['id']:item for item in json.loads((BASE/'track.json').read_text())['lessons']}
    assert len(ENTRIES)>=20
    assert {entry['id'] for entry in ENTRIES} <= set(planned)
    for entry in ENTRIES:
        assert entry['language']=='java' and entry['runtime_profile']=='java21'
        guide=(ROOT/entry['guide_path']).read_text()
        assert len(re.findall(r'^\s*[1-6]\. \*\*',guide,re.MULTILINE))==6
        assert all(f'### Example {letter}:' in guide for letter in 'AB')
        assert len(re.findall(r"\b[\w'-]+\b",guide))>=1050
        for prerequisite in planned[entry['id']]['prerequisites']:
            assert f'`{prerequisite}`' in guide
        for relative in [entry['source_path'],entry['guide_path'],*entry['solution_paths']]:
            path=ROOT/relative
            assert path.is_file() and path.resolve().is_relative_to(BASE)
            text=path.read_text()
            assert '\u2014' not in text
            if path.suffix=='.java':
                assert 'public class Main' in text and 'public static void main(String[] args)' in text
                assert re.findall(r'// Exercise ([1-6]):',text)==list('123456')
            if '/solutions/' in relative and path.suffix=='.md':
                assert len(re.findall(r"\b[\w'-]+\b",text))>=700
                assert re.findall(r'^## Exercise ([1-6]):',text,re.MULTILINE)==list('123456')


@pytest.mark.skipif(os.environ.get('DS60_TEST_JAVA')!='1',reason='Requires an explicitly prepared JDK21 environment')
@pytest.mark.parametrize('entry',ENTRIES,ids=[entry['id'] for entry in ENTRIES])
def test_java_reference_compiles_and_runs_with_assertions(entry: dict,tmp_path: Path) -> None:
    source=next(ROOT/path for path in entry['solution_paths'] if path.endswith('.java'))
    (tmp_path/'Main.java').write_text(source.read_text())
    compiled=subprocess.run(['javac','--release','21','-d',str(tmp_path),str(tmp_path/'Main.java')],capture_output=True,text=True,timeout=60,check=False)
    assert compiled.returncode==0,compiled.stdout+compiled.stderr
    classpath=str(tmp_path)
    optional=os.environ.get('DS60_JAVA_CLASSPATH')
    if optional:classpath+=os.pathsep+optional
    executed=subprocess.run(['java','-ea','-cp',classpath,'Main'],capture_output=True,text=True,timeout=60,check=False)
    assert executed.returncode==0,executed.stdout+executed.stderr
