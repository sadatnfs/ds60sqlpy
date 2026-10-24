from pathlib import Path
import json
import textwrap

ROOT = Path(__file__).resolve().parents[3]
SPECS = {}


def ex(title, prompt, expected, code, why):
    return dict(title=title, prompt=prompt, expected=expected,
                code=textwrap.dedent(code).strip(), why=why)


def add(number, mental, anatomy, terms, exercises, helper='',
        imports="import { strict as assert } from 'node:assert';",
        source='https://nodejs.org/docs/latest-v24.x/api/', notes=''):
    assert len(exercises) == 6
    SPECS[f'js-{number:03d}'] = dict(
        mental=mental, anatomy=anatomy, terms=terms, exercises=exercises,
        helper=textwrap.dedent(helper).strip(), imports=imports, source=source, notes=notes)


def program(spec, blocks, reference=True, typed=False):
    signature = ': Promise<{ checks: number; status: string }>' if typed else ''
    result = spec['imports'] + '\n\n' + spec['helper'] + '\n\n'
    result += 'export async function verify()' + signature + ' {\n'
    for i, block in enumerate(blocks, 1):
        label = f'Exercise {i}: {spec["exercises"][i-1]["title"]}' if reference else 'Worked example'
        result += f'  // {label}\n  {{\n' + textwrap.indent(block, '    ') + '\n  }\n\n'
    result += f'  return {{ checks: {len(blocks)}, status: "passed" }};\n}}\n'
    return result + '\nconsole.log(JSON.stringify(await verify()));\n'


def write_all():
    base = ROOT / 'courses/javascript-typescript'
    plan = json.loads((base / 'track.json').read_text())
    manifest = json.loads((base / 'lessons.json').read_text())
    existing = {e['id'] for e in manifest['lessons']}
    for folder in ('guides', 'lessons', 'solutions', 'fixtures', 'authoring'):
        (base / folder).mkdir(exist_ok=True)
    for row in plan['lessons']:
        identity = row['id']
        if identity not in SPECS:
            continue
        spec = SPECS[identity]
        reading = row['runtime'] == 'reading'
        typed = row['runtime'] == 'typescript-node'
        suffix = 'md' if reading else 'mts' if typed else 'mjs'
        language = 'markdown' if reading else 'typescript' if typed else 'javascript'
        guide = f'courses/javascript-typescript/guides/{identity}.md'
        learner = f'courses/javascript-typescript/lessons/{identity}.{suffix}'
        solution = f'courses/javascript-typescript/solutions/{identity}_solution.{suffix}'
        explanation = f'courses/javascript-typescript/solutions/{identity}_solutions.md'
        prerequisites = ', '.join('`' + p + '`' for p in row['prerequisites']) or 'None. This lesson starts from the language and host distinction.'
        terms = '\n\n'.join(f'**{name}:** {meaning}' for name, meaning in spec['terms'])
        tasks = '\n\n'.join(
            f"{i}. **{e['title']}.** {e['prompt']}\n   **Expected:** {e['expected']}\n   **Verify:** Record the observed value, exception or browser state and compare it with that expectation."
            for i, e in enumerate(spec['exercises'], 1))
        examples = []
        for i, e in enumerate(spec['exercises'][:2]):
            code = e['code'] if reading else program(spec, [e['code']], False, typed)
            examples.append(f"### Example {chr(65+i)}: {e['title']}\n\n{e['why']}\n\n```{'html' if reading else language}\n{code}\n```\n\n**Expected:** {e['expected']}")
        if reading:
            run = ('This is a browser reading and practice lesson. Node has no document or window. Use the separate checked-in browser fixture described below and record its visible interaction, focus and state changes. The manifest deliberately supplies no Node execution claim for these DOM examples.')
        elif typed:
            run = ('Use the prepared TypeScript 5.9.3 profile. The classroom saves main.mts, checks strict NodeNext resolution with noEmitOnError and an ES2022 target, then runs compiled/main.mjs on Node 24.22.1. Node typings 24.10.0 are prepared. Compilation and execution are separate stages. Types are erased and do not validate external JSON. No npm installation belongs inside the lesson.')
        else:
            run = ('Use the prepared Node 24.22.1 profile. The classroom saves an ES module as main.mjs and executes it with Node. Only built-in Node or ECMAScript APIs are used. For a prepared native environment, node main.mjs is the same command on PowerShell and POSIX. Browser APIs have separate host requirements.')
        prompt = f'''Use $guide-ds60sqlpy-learning for {identity}: {row['title']}.
Read {guide} and {learner}. Direct prerequisites: {prerequisites}.
Explain the mechanism, ask me to predict a value or failure, review my own attempt,
give one hint, request compile/runtime/browser evidence, and ask a fresh retrieval question.
Keep courses/javascript-typescript/solutions/ closed until I request comparison or show an attempt.
Done when I can explain the state and host contracts, pass all six exercise checks,
diagnose a controlled failure, and solve a new boundary case without copying the answer.'''
        document = f'''# {identity}: {row['title']}

## Level and prerequisites

{row['level'].capitalize()}, approximately {row['minutes']} minutes. Direct prerequisites: {prerequisites}

## Learning objectives

Explain {', '.join(name.lower() for name, _ in spec['terms'])} with a concrete program. Trace how the values change, identify the assumptions, and make a boundary or invalid case observable. The first investigation is: {spec['exercises'][0]['prompt']} The final task tests {spec['exercises'][-1]['title'].lower()}.

## Purpose and mental model

{spec['mental']}

## Vocabulary and concepts

{terms}

## How to run this lesson

{run}

Save your own learner copy under ignored `.learning/expansion/{identity}/` or use a saved classroom pad. Record predictions before execution. Each worked program includes its helper definitions. The reference puts the six exercises in separate scopes, so a task cannot silently rely on a variable from a previous task. A successful assertion is silent; the final JSON receipt reports how many exercise blocks completed. A failing assertion must produce a failed process, not a generic success message.

{spec['notes']}

## Syntax anatomy and execution trace

{spec['anatomy']}

## Worked example / walkthrough

{chr(10).join(examples)}

## Prediction before your attempt

Trace the entry point and identify the values that exist before each operation. Distinguish a value from a reference to an object, a returned Promise from its eventual result, and a compile-time type from a runtime check. Write down the first observation that would disprove your explanation. A useful prediction includes an expected value or failure category, not merely a claim that the program should work.

For a loop, write the state before and after one iteration. For a callback, identify the caller and the arguments it supplies. For an asynchronous operation, identify who starts it, who awaits it, and who owns cleanup. These small traces make failures local: you can compare the first incorrect state instead of guessing from a much later symptom.

## Exercises

{tasks}

## Common pitfalls and diagnosis

Keep the smallest fixture that distinguishes the intended behavior from a tempting alternative. Read the assertion message and inspect the input, return value and state at that point. Do not remove a failing check just to reach the success receipt. Preserve the original failure, repair the responsible assumption, then check the normal path and the negative case again.

If a host API is absent, confirm the actual host and version before changing the algorithm. A successful parse does not prove that an API exists. Compiler success does not prove that external data satisfies a type. A browser interaction requires browser evidence. For resource-owning examples, inspect cleanup after failure as carefully as the happy path. The separate explanations discuss the specific mistaken inference in each exercise.

## Progressive hints

Start by comparing the actual value with the literal expected result. Next, isolate the expression that transforms it or the boundary where its type or ownership changes. If the discrepancy involves scheduling, replace unrelated work with a small trace array and await the exact completion you intend to observe. Finally, ask for one hint about the first incorrect assumption before opening the reference. Keep one controlled failure that would catch the same mistake returning.

## Self-check and retrieval

Close the solution and explain {', '.join(name for name, _ in spec['terms'][:3])} using the fixture. Reconstruct one example from a blank saved copy. Change a boundary input and predict the new result before running it. Explain the assumptions under which the mechanism is useful and a situation in which its cost or host requirements make another design preferable. A copied program is useful rehearsal; a fresh case demonstrates transfer.

## Sources and verification status

[Official language or host reference]({spec['source']}). Fixtures and exercises are original course material. Actual prepared Node, TypeScript and browser execution evidence is tracked in `docs/implementation/javascript-content-status.md`. Manual-only steps remain unqualified until performed. No default lesson installs dependencies, downloads a model or contacts a shared service.

## Ask an AI tutor about this lesson

```text
{prompt}
```
'''
        answer = f'''# {identity}: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

## Mechanism review

{spec['mental']}

{terms}

## Reading the implementation

{spec['anatomy']}

'''
        for i, e in enumerate(spec['exercises'], 1):
            answer += f'''## Exercise {i}: {e['title']}

Task: {e['prompt']}

{e['why']}

```{'html' if reading else language}
{e['code']}
```

**Expected:** {e['expected']}

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

'''
        answer += '''## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
'''
        (ROOT / guide).write_text(document)
        (ROOT / explanation).write_text(answer)
        if reading:
            (ROOT / learner).write_text(f'# {identity}: {row["title"]}\n\nUse the browser fixture and record predictions before inspecting solutions.\n\n## Exercises\n\n' + tasks + '\n')
        else:
            (ROOT / solution).write_text(program(spec, [e['code'] for e in spec['exercises']], True, typed))
            comments = []
            for i, e in enumerate(spec['exercises'], 1):
                comments.append(f'// Exercise {i}: {e["title"]}\n' + '\n'.join('// ' + line for line in textwrap.wrap(e['prompt'], 90)) + '\n// Expected: ' + e['expected'])
            (ROOT / learner).write_text('// Answer-free learner source. Save your own copy before editing.\n' + ('\nexport {};\n' if typed else '') + '\n\n'.join(comments) + '\n\nconsole.log("Implement the six exercises in your saved copy.");\n')
        if identity not in existing:
            manifest['lessons'].append(dict(id=identity, status='authored', language=language,
                runtime_profile=row['runtime'], guide_path=guide, source_path=learner,
                solution_paths=[explanation] if reading else [solution, explanation], verification_id=None))
        row['outcome'] = spec['mental'].split('.')[0] + '.'
        row['lab'] = spec['exercises'][0]['prompt']
        row['verification'] = spec['exercises'][0]['expected'] + ' ' + spec['exercises'][-1]['expected']
        row['concepts'] = [name for name, _ in spec['terms']]
    manifest['lessons'].sort(key=lambda e: e['id'])
    (base / 'lessons.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (base / 'track.json').write_text(json.dumps(plan, indent=2) + '\n')
    print('Authored JS/TS lessons:', len(SPECS))
