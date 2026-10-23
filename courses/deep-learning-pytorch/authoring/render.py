from pathlib import Path
import json, textwrap, re
ROOT = Path(__file__).resolve().parents[3]
SPECS = {}
def ex(title,prompt,expected,code,why):
    return dict(title=title,prompt=prompt,expected=expected,code=textwrap.dedent(code).strip(),why=why)
def add(id,mental,anatomy,terms,exercises,source,imports='import numpy as np',helper='',decisions='',comparison='',interview=()):
    assert len(exercises)==6, id
    SPECS[id]=dict(mental=mental,anatomy=anatomy,terms=terms,exercises=exercises,source=source,imports=imports,helper=textwrap.dedent(helper).strip(),decisions=decisions,comparison=comparison,interview=interview)
def polish(value):
    value=re.sub(r',(?=\S)', ', ', value)
    value=re.sub(r';(?=\S)', '; ', value)
    value=re.sub(r'\b(with|of|by|rank|alpha|beta|size|overlap|budget|reserve|lengths|visits|purchases|version|seed|steps|count|value|rate)(?=\d)', r'\1 ', value)
    value=re.sub(r'(?<=\d)(?=records|steps|tokens|bytes|updates|entries|documents|times|characters)', ' ', value)
    return value

def write_all(only=None):
 for track in ['deep-learning-pytorch']:
  base=ROOT/'courses'/track
  plan=json.loads((base/'track.json').read_text())
  inventory=json.loads((base/'lessons.json').read_text())
  existing={x['id'] for x in inventory['lessons']}
  for p in plan['lessons']:
   id=p['id']
   if id not in SPECS or (only is not None and id not in only): continue
   s=SPECS[id]
   for field in ['mental','anatomy','decisions','comparison']: s[field]=polish(s[field])
   for exercise in s['exercises']:
    for field in ['prompt','expected','why']: exercise[field]=polish(exercise[field])
   p['outcome']=s['mental'].split('.')[0]+'.'; p['lab']=s['exercises'][0]['prompt']; p['verification']=s['exercises'][0]['expected']+' '+s['exercises'][-1]['expected']; p['concepts']=[k for k,v in s['terms']]; reading=p['runtime']=='reading'; ext='md' if reading else 'py'
   prefix=f'courses/{track}'
   guide=f'{prefix}/guides/{id}.md'; learner=f'{prefix}/lessons/{id}.{ext}'
   solution=f'{prefix}/solutions/{id}_solution.py'; explanation=f'{prefix}/solutions/{id}_solutions.md'
   prereq=', '.join(f'`{q}`' for q in p['prerequisites'])
   terms='\n\n'.join(f'**{k}:** {v}' for k,v in s['terms'])
   exercise_text='\n\n'.join(f"{n}. **{e['title']}.** {e['prompt']}\n   **Expected:** {e['expected']}\n   **Verify:** Save the {('reasoning table' if reading else 'assertion results')} for exercise {n}, including {e['expected']}" for n,e in enumerate(s['exercises'],1))
   examples='\n\n'.join(f"### Example {chr(65+n)}: {e['title']}\n\n{e['why']}\n\n```{'text' if reading else 'python'}\n{(s['imports']+chr(10)+s['helper']+chr(10)) if not reading and n==0 else ''}{e['code']}\n```\n\n**Expected:** {e['expected']}" for n,e in enumerate(s['exercises'][:3]))
   runtime = ('Use the reading worksheet. Write a reasoned response for each case; no execution or model download is required.' if reading else f"Use a prepared `{p['runtime']}` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/{id}/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython {learner}`. For macOS/Linux, use the interpreter explicitly selected for a separately prepared native PyTorch environment, and invoke that interpreter on `{learner}` from the repository root. The repository's general `.venv` is not assumed to contain PyTorch; the prepared classroom profile is the default execution route.")
   study_guidance = 'Read the three worked cases in order and write the assumptions, intermediate reasoning and conclusion for each one. These are text cases, not programs to execute. Compare your written interpretation with the stated expected observations, then answer the six exercises in your saved worksheet. A correct argument must state its evidence boundary; source presence does not establish a model run.' if reading else 'Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the explicit tolerance in each assertion. Several analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone is not a universal numerical-error bound. Finite differences, reductions and conditioning can require different justified tolerances. Integer counts, identities and boolean decisions should be exact.'
   code_anatomy=s['anatomy']
   prompt=f'''Use the checked-in $guide-ds60sqlpy-learning skill for {id}, {p['title']}.
Read {guide} and {learner}. Direct prerequisites: {prereq}.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep {prefix}/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.'''
   paired=p['paired_lesson_id']
   interview_text='\n\n'.join('**'+question+'**\n\n'+answer for question,answer in s['interview'])
   diagnosis = s.get('diagnosis', 'When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.')
   document=f'''# {id}: {p['title']}

## Level and prerequisites

{p['level'].capitalize()}; approximately {p['minutes']} minutes. Direct prerequisites: {prereq}. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

{p['outcome']} The central investigation is concrete: {p['lab']} The finish condition is {p['verification']} A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

{s['mental']}

## Design decisions and when to use this method

{s.get('decisions','')}

## Paired TensorFlow comparison

Compare [{paired}](../../deep-learning-tensorflow/guides/{paired}.md) after deriving the shared numerical contract.

{s['comparison']}

## Vocabulary and concepts

{terms}

## How to run this lesson

{runtime}

{study_guidance}

## Syntax anatomy and reasoning sequence

{code_anatomy}

{s.get('deep_dive', '')}

## Worked example / walkthrough

{examples}

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: {p['verification']} Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

{exercise_text}

## Common pitfalls and diagnosis

{diagnosis}

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain {', '.join(k for k,v in s['terms'][:3])} using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite {prereq} if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [{s['source'][0]}]({s['source'][1]}), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/pytorch-content-status.md`; authored content does not imply that a heavy runtime was executed.

## Interview reasoning with worked answers

{interview_text}

{s.get('appendix','')}

## Ask Codex about this lesson

```text
{prompt}
```
'''
   explanation_doc=f'''# {id}: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

{s['mental']}

{terms}

## Reading the implementation

{s['anatomy']}

{s.get('deep_dive', '')}

'''
   blocks=[]
   for n,e in enumerate(s['exercises'],1):
    explanation_doc+=f'''## Exercise {n}: {e['title']}

The question is: {e['prompt']}

{e['why']}

```{'text' if reading else 'python'}
{e['code']}
```

**Expected:** {e['expected']}

**Verify:** Compare the computed values or written argument with {e['expected']}

'''
    blocks.append(f"    # Exercise {n}: {e['title']}\n"+textwrap.indent(e['code'],'    '))
   explanation_doc+='## Review after comparison\n\nRepeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.\n'
   (ROOT/guide).write_text(document)
   (ROOT/explanation).write_text(explanation_doc)
   if reading:
    (ROOT/learner).write_text(f'# {id}: {p["title"]}\n\nRead the guide, record a prediction, then answer the six cases without opening solutions.\n\n## Exercises\n\n'+exercise_text+'\n')
   else:
    source=f'"""{id}: {p["title"]}.\n\nAnswer-free learner worksheet. See the companion guide for worked examples.\nCopy to .learning before editing. Six independent attempts belong below.\n"""\n\n'
    for n,e in enumerate(s['exercises'],1):
     source+=f'# Exercise {n}: {e["title"]}\n'+ '\n'.join('# '+x for x in textwrap.wrap(e['prompt'],88))+'\n# Expected: '+e['expected']+'\n\n'
    source+='if __name__ == "__main__":\n    print("Read the guide and implement the six exercises in your saved copy.")\n'
    (ROOT/learner).write_text(source)
    code='"""'+id+': bounded local reference checks. No network or persistent data writes."""\n\n'+s['imports']+'\n\n'+s['helper']+'\n\n\ndef verify():\n'+'\n\n'.join(blocks)+'\n    return {"checks": 6, "status": "passed"}\n\n\nif __name__ == "__main__":\n    print(verify())\n'
    (ROOT/solution).write_text(code)
   if id not in existing:
    inventory['lessons'].append(dict(id=id,status='authored',language='markdown' if reading else 'python',runtime_profile=p['runtime'],guide_path=guide,source_path=learner,solution_paths=[explanation] if reading else [solution,explanation],verification_id=None))
  inventory['lessons'].sort(key=lambda x:x['id'])
  (base/'lessons.json').write_text(json.dumps(inventory,indent=2)+'\n')
  (base/'track.json').write_text(json.dumps(plan,indent=2)+'\n')
 print('Authored',len(SPECS),'lesson bundles')
