"""Deepen the existing guides from explicit content inputs and tested complete examples."""
from pathlib import Path
import json,re,runpy,sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
BASE=ROOT/'courses/cpp'
sys.path.insert(0,str(HERE))
runpy.run_path(str(HERE/'build_programs.py'),run_name='__main__')
DETAILS={}
for path in sorted(HERE.glob('details*.py')):DETAILS.update(runpy.run_path(str(path))['DETAILS'])
programs=json.loads((HERE/'program_inputs.json').read_text())
outputs=json.loads((HERE/'expected_outputs.json').read_text())
for record in programs:
    n=record['number'];key=f'cpp-{n:03d}';path=BASE/f'guides/{key}.md';guide=path.read_text()
    guide=guide.replace('Authored beta content. Content completion and runtime qualification are separate evidence.\n\n','')
    if n in DETAILS:
        heading,mechanism,pitfalls=DETAILS[n]
        block='<!-- depth:start -->\n## '+heading+'\n\n'+mechanism+'\n<!-- depth:end -->\n\n'
        if '<!-- depth:start -->' in guide:guide=re.sub(r'<!-- depth:start -->.*?<!-- depth:end -->\n\n',lambda _:block,guide,flags=re.S)
        else:guide=guide.replace('## Run and inspect',block+'## Run and inspect')
        guide=re.sub(r'(?<=## Common pitfalls\n\n).*?(?=\n\n## Retrieval and transfer)',lambda _:pitfalls,guide,flags=re.S)
        solution=BASE/f'solutions/{key}_solutions.md';text=solution.read_text()
        answer='<!-- depth:start -->\n## '+heading+'\n\n'+mechanism+'\n\n## Debugging the contract\n\n'+pitfalls+'\n<!-- depth:end -->\n\n'
        if '<!-- depth:start -->' in text:text=re.sub(r'<!-- depth:start -->.*?<!-- depth:end -->\n\n',lambda _:answer,text,flags=re.S)
        else:text=text.replace('## Worked example 1',answer+'## Worked example 1')
        solution.write_text(text)
    chunks=['## Worked example / walkthrough','Each example below is a complete independent program. Copy one into `main.cpp`,or compile its linked checked-in source using [the compile and run tutorial](../compile-and-run.md). Do not concatenate the two programs:each defines its own `main`. Use C++20 and the shown warning/thread flags. The printed success line follows the displayed assertions; it is a bounded example check,not a substitute for the six learner tasks.']
    for index in (1,2):
        name=f'{key}-example-{index}.cpp';code=(BASE/'examples'/name).read_text().rstrip();expected=outputs[name]
        chunks += [f'### Worked example {index}',f'[Complete program {index}](../examples/{name})', '```cpp\n'+code+'\n```', '**Expected:** With assertions enabled,the program exits0 and prints:\n\n```text\n'+expected.rstrip()+'\n```']
    # Retain the host-capstone handoff subheading after the original second example.
    old=re.search(r'## Worked example / walkthrough\n(.*?)\n## Exercises',guide,re.S)
    extra=''
    if old:
        match=re.search(r'\n(### (?:File-driven reference handoff|Complete host library project|Failure-accounting reference).*?)$',old.group(1),re.S)
        if match:extra='\n\n'+match.group(1)
    guide=re.sub(r'## Worked example / walkthrough\n.*?(?=\n## Exercises)',lambda _:'\n\n'.join(chunks)+extra+'\n',guide,flags=re.S)
    guide=guide.replace('Record the concrete output, assertion, field comparison or bounded transcript described here: ','')
    guide=guide.replace('First identify the changed input. Then trace the relevant operation in the worked examples. Finally compare the result to this clue: ','')
    path.write_text(guide)
# Remove internal publication labels without changing the original pilots' teaching bodies.
for n in (1,2,3,9):
    path=BASE/f'guides/cpp-{n:03d}.md';text=path.read_text()
    text=text.replace('Authored beta teaching content. Publication and runtime qualification are separate gates. Read the current capability notice before running. No opening or saving this lesson installs tools, starts a cluster or proves mastery.\n\n','')
    path.write_text(text)

# Reference links support the language/tool contract; examples remain original teaching fixtures.
refs={6:'[Numeric conversion contract](https://eel.is/c++draft/charconv.from.chars)',7:'[Vector capacity and invalidation](https://eel.is/c++draft/vector.capacity)',12:'[GCC compilation and linking stages](https://gcc.gnu.org/onlinedocs/gcc/Overall-Options.html)',13:'[CMake3.28 tutorial](https://cmake.org/cmake/help/v3.28/guide/tutorial/index.html)',25:'[GCC instrumentation options](https://gcc.gnu.org/onlinedocs/gcc/Instrumentation-Options.html)',29:'[Thread join contract](https://eel.is/c++draft/thread.thread.member)',31:'[Atomic ordering contract](https://eel.is/c++draft/atomics.order)',33:'[GCC instrumentation options](https://gcc.gnu.org/onlinedocs/gcc/Instrumentation-Options.html)'}
for n in DETAILS:
    path=BASE/f'guides/cpp-{n:03d}.md';text=path.read_text()
    reference=refs.get(n,'[C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines)')
    if '## Primary references' not in text:text=text.replace('## Ask an AI tutor about this lesson','## Primary references\n\n'+reference+'\n\n## Ask an AI tutor about this lesson')
    path.write_text(text)
runpy.run_path(str(HERE/'normalize_prose.py'),run_name='__main__')
