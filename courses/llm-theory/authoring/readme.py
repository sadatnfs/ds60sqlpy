"""Derive the full theory route index from its plan and authored manifest."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]


def write_readme():
    plan = json.loads((ROOT / 'docs/expansion/plans/llm-theory.json').read_text())
    manifest = json.loads((ROOT / 'courses/llm-theory/lessons.json').read_text())
    registered = {row['id']: row for row in manifest['lessons']}
    assert len(registered) == len(plan['lessons']) == 48
    assert set(registered) == {row['id'] for row in plan['lessons']}
    labels = {'python-core': 'Core / NumPy', 'llm-torch-cpu': 'PyTorch CPU', 'reading': 'Reading'}
    counts = {profile: sum(row['runtime_profile'] == profile for row in registered.values()) for profile in labels}
    text = f'''# Language-model mechanisms and evidence

All **48 chapters** are authored, from probability and tokenization through actual tiny-model training, inference, evaluation and modern Transformer mechanisms. The route has {counts['python-core']} Core/NumPy lessons, {counts['llm-torch-cpu']} PyTorch CPU lessons and {counts['reading']} reading lessons. The index below is generated from the reviewed plan and complete authored manifest.

## Start in the Docker classroom

Use the [Docker classroom setup](../../docs/docker-classroom.md), open **Journeys**, and choose the LLM theory journey. Select a chapter, read its guide, save your own learner pad and use **Run** for an executable lesson. The selected worker supplies the declared Python packages. Host Python, PyTorch and TensorFlow installations are not prerequisites for this route.

Reading chapters use written calculations and reasoning cases. Their read marker is a study record, not an executed test or proof of mastery. For code chapters, record predictions, attempt the six tasks, use progressive hints, then compare the separate executable and explained solutions after an attempt. Preserve learner work under the classroom's saved pad or ignored `.learning/expansion/` directories.

The default lessons use tiny literal offline fixtures and bounded CPU computations. No default chapter downloads model weights or calls a paid model API. Actual reference and worked-example qualification is recorded in the [ML content status](../../docs/implementation/ml-content-status.md), [expert chapter status](../../docs/implementation/llm-expert-status.md) and [depth-review record](../../docs/implementation/ml-depth-review.md). Runtime evidence is separate from a claim that a small model is a reliable subject expert.

## Follow a complete Transformer calculation

[Inside a Transformer](../../docs/learning/inside-a-transformer.md) walks through an inspectable NumPy decoder forward pass, tensor shapes, causal-prefix checks, a finite-difference derivative and an explicitly head-only update. Use it alongside chapters 009-011 and 016, then continue to 043-048 for architecture families, positional methods, RMSNorm/SwiGLU, head sharing and exact blockwise attention, sparse experts and speculative decoding.

For a subject assistant, retrieval or fine-tuning project, continue into [Applied LLM systems](../llm-applied/README.md). That route develops corpus provenance, chunking, lexical/hybrid retrieval, access boundaries, grounded citations, abstention, evaluation, actual tiny-model adaptation and an explicitly optional pretrained recipe. [NLP foundations](../nlp/README.md) supplies additional text and classical retrieval methods. The dedicated [PyTorch](../deep-learning-pytorch/README.md) and [TensorFlow](../deep-learning-tensorflow/README.md) journeys cover their frameworks broadly.

## Complete chapter index

'''
    sections = [
        ('Probability, tokens and attention', 1, 14),
        ('A tiny causal model: training, inference and evidence', 15, 28),
        ('Adaptation, evaluation and system decisions', 29, 42),
        ('Expert Transformer mechanisms', 43, 48),
    ]
    for title, first, last in sections:
        text += f'### {title}\n\n| Chapter | Topic | Runtime |\n| --- | --- | --- |\n'
        for row in plan['lessons']:
            number = int(row['id'].rsplit('-', 1)[1])
            if first <= number <= last:
                topic = row['title'].replace('|', '\\|')
                runtime = labels[registered[row['id']]['runtime_profile']]
                text += f"| [{row['id']}](guides/{row['id']}.md) | {topic} | {runtime} |\n"
        text += '\n'
    text += '''## Maintainer sources

[The authored manifest](lessons.json) records complete bundles. [The reviewed plan](../../docs/expansion/plans/llm-theory.json) supplies stable IDs, ordering and prerequisites. The earlier completion specifications live under `courses/deep-learning-tensorflow/authoring/`; the six expert chapters have their own [authoring sources](authoring/README.md). Regenerate this index with `python courses/llm-theory/authoring/readme.py` rather than hand-maintaining a second lesson list.
'''
    (ROOT / 'courses/llm-theory/README.md').write_text(text)


if __name__ == '__main__':
    write_readme()
