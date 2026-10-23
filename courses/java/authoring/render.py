from pathlib import Path
import json,textwrap
ROOT=Path(__file__).resolve().parents[3]
SPECS={}
def ex(title,prompt,expected,code,why):return dict(title=title,prompt=prompt,expected=expected,code=textwrap.dedent(code).strip(),why=why)
def add(n,mental,anatomy,terms,exercises,helper='',imports='import java.util.*;',source='https://docs.oracle.com/en/java/javase/21/docs/api/index.html',run_notes=''):
 assert len(exercises)==6
 SPECS[f'java-{n:03d}']=dict(mental=mental,anatomy=anatomy,terms=terms,exercises=exercises,helper=textwrap.dedent(helper).strip(),imports=imports,source=source,run_notes=run_notes)
def program(s,blocks):
 return s['imports']+'\n\npublic class Main {\n'+textwrap.indent(s['helper'],'    ')+'\n    public static void main(String[] args) throws Exception {\n'+textwrap.indent('\n\n'.join(blocks),'        ')+'\n    }\n}\n'
def write_all():
 base=ROOT/'courses/java';plan=json.loads((base/'track.json').read_text());inventory=json.loads((base/'lessons.json').read_text());existing={e['id'] for e in inventory['lessons']}
 for p in plan['lessons']:
  id=p['id']
  if id not in SPECS:continue
  s=SPECS[id];guide=f'courses/java/guides/{id}.md';learner=f'courses/java/lessons/{id}.java';solution=f'courses/java/solutions/{id}_solution.java';explanation=f'courses/java/solutions/{id}_solutions.md'
  prereq=', '.join('`'+v+'`' for v in p['prerequisites']) or 'None. This lesson starts from a plain text source file.'
  terms='\n\n'.join(f'**{k}:** {v}' for k,v in s['terms'])
  exercises='\n\n'.join(f"{i}. **{e['title']}.** {e['prompt']}\n   **Expected:** {e['expected']}\n   **Verify:** Compare your assertion values or captured diagnostic with {e['expected']}" for i,e in enumerate(s['exercises'],1))
  examples='\n\n'.join(f"### Example {chr(65+i)}: {e['title']}\n\n{e['why']}\n\n```java\n{program(s,[x['code'] for x in s['exercises'][:i+1]])}\n```\n\n**Expected:** {e['expected']}" for i,e in enumerate(s['exercises'][:2]))
  prompt=f'''Use $guide-ds60sqlpy-learning for {id}: {p['title']}.
Read {guide} and {learner}. Direct prerequisites: {prereq}.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.'''
  guide_text=f'''# {id}: {p['title']}

## Level and prerequisites

{p['level'].capitalize()}, approximately {p['minutes']} minutes. Direct prerequisites: {prereq}

## Learning objectives

Explain {', '.join(k.lower() for k,v in s['terms'])} using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. The first investigation is {s['exercises'][0]['prompt']} The final exercise transfers the mechanism to {s['exercises'][-1]['title'].lower()}.

## Purpose and mental model

{s['mental']}

## Vocabulary and concepts

{terms}

## How to run this lesson

Open the Docker classroom, choose the prepared Java21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/{id}/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.

{s.get('run_notes','')}

## Syntax anatomy and execution trace

{s['anatomy']}

## Worked example / walkthrough

{examples}

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

{exercises}

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

First reconstruct the values and identities in the worked example. Next isolate the line that changes the result when one input is altered. Finally compare the normal and failure paths with the stated contract. Use a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

## Self-check and retrieval

Close the solution and explain {', '.join(k for k,v in s['terms'][:3])} in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java21 API or language reference]({s['source']}), reviewed2026-10-22. Examples and exercise fixtures are original course material. Consult `docs/implementation/java-content-status.md` for the actual compile/run receipts. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask an AI tutor about this lesson

```text
{prompt}
```
'''
  explanation_text=f'''# {id}: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

{s['mental']}

{terms}

## Reading the reference

{s['anatomy']}

'''
  code_blocks=[]
  for i,e in enumerate(s['exercises'],1):
   explanation_text+=f'''## Exercise {i}: {e['title']}

Task: {e['prompt']}

{e['why']}

```java
{e['code']}
```

**Expected:** {e['expected']}

**Verify:** Compare the program values or named exception with {e['expected']} Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

'''
   code_blocks.append(f'// Exercise {i}: {e["title"]}\n'+e['code'])
  explanation_text+='''## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
'''
  for path,text in [(guide,guide_text),(solution,program(s,code_blocks)),(explanation,explanation_text)]:
   target=ROOT/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text, encoding="utf-8", errors="backslashreplace")
  comments=[]
  for i,e in enumerate(s['exercises'],1):comments.append(f'// Exercise {i}: {e["title"]}\n'+'\n'.join('// '+line for line in textwrap.wrap(e['prompt'],90))+'\n// Expected: '+e['expected'])
  (ROOT/learner).parent.mkdir(parents=True,exist_ok=True);(ROOT/learner).write_text('''// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {
    public static void main(String[] args) throws Exception {
'''+textwrap.indent('\n\n'.join(comments),'        ')+'\n        System.out.println("Implement and check the six exercises in your saved copy.");\n    }\n}\n')
  if id not in existing:inventory['lessons'].append(dict(id=id,status='authored',language='java',runtime_profile='java21',guide_path=guide,source_path=learner,solution_paths=[solution,explanation],verification_id=None))
  p['outcome']=s['mental'].split('.')[0]+'.';p['lab']=s['exercises'][0]['prompt'];p['verification']=s['exercises'][0]['expected']+' '+s['exercises'][-1]['expected']
 inventory['lessons'].sort(key=lambda e:e['id']);(base/'lessons.json').write_text(json.dumps(inventory,indent=2)+'\n');(base/'track.json').write_text(json.dumps(plan,indent=2)+'\n')
 print('Authored Java lessons:',len(SPECS))
