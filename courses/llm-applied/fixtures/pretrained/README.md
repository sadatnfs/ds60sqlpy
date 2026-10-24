# Optional pretrained-model adaptation, fully local after preparation

This recipe fine-tunes a small real pretrained language model on a deliberately
tiny authored dataset. It is separate from the ordinary classroom. After the
explicit dependency and model downloads, training and generation run with
Docker networking disabled. No API account, API key or GPU is required.

The pinned model is `HuggingFaceTB/SmolLM2-135M-Instruct`, revision
`12fd25f77366fa6b3b4b768ec3050bf629380bac`. Its model card identifies the license
as Apache 2.0. The weights are 269, 060, 552 bytes, about 257 MiB. Review the
[pinned model card](https://huggingface.co/HuggingFaceTB/SmolLM2-135M-Instruct/tree/12fd25f77366fa6b3b4b768ec3050bf629380bac)
for its intended scope and limitations.

## What has actually been tested

On 23 October 2026, the Linux arm64 Docker image built successfully with a full
hashed dependency lock. Pinned acquisition recorded 13 files. Both full
fine-tuning and LoRA completed exactly 10 CPU updates with maximum sequence
length 128, and the saved LoRA adapter reloaded for offline generation.

| Check | Observed result |
| --- | --- |
| Full fine-tuning | 134, 515, 008 trainable parameters;10 updates |
| LoRA | 230, 400 trainable parameters;10 updates |
| LoRA held-out token loss | 6.721148 before;6.474194 after |
| Full fine-tuning held-out token loss | 6.721148 before;0.008058 after |
| Saved-adapter generation | Executed offline; factual answer was not accepted |

These results establish that the preparation, masks, optimization and saved
artifact paths execute. They do not establish useful domain-assistant quality.
Two fresh LoRA runs in the same qualified image produced identical adapter
file hashes and identical evaluation loss. The seed is set before adapter
construction: setting only the trainer seed happens too late for matrices that
were already initialized. This is a same-environment repeatability check, not
a promise of bitwise equality across CPUs, libraries or precision settings.

The data contains four training records and one evaluation record. Their
`family` fields separate authored labels, but the examples share an assignment
unit extraction task and prompt template. The one held-out entity label is a
mechanics check, not an independent sample of business-question families.
The large loss drop in full fine-tuning must be read in that narrow context.

The generation probe supplies the correct conversion-rate definition as
evidence. The first qualified adapter produced a fluent answer that incorrectly
described eligible visits divided by eligible visits. It also did not establish
claim-level citation support. This is a concrete example of why a completed
training run, lower token loss and fluent prose are insufficient acceptance
criteria. The JSON marks the answer as unvalidated and distinguishes supplied
evidence IDs from verified citations.

Linux amd64 dependency resolution is prepared separately; native execution on
amd64 and Windows/WSL 2 has not been established by this arm64 run. The same
Linux-container commands are intended for local Docker engines on all OSes.

## 1. Build the optional environment

Use Docker with Linux containers and Compose, as described in the
[classroom guide](../../../../docs/docker-classroom.md). Open a terminal in the
repository root. On Windows, the engine uses its WSL 2 backend. Run each command
separately and stop if it fails. These commands work in Command Prompt,
PowerShell and macOS/Linux terminals without host Python.

First build the CPU PyTorch worker that supplies the optional image's base:

```text
docker compose --progress plain -f compose.classroom.yaml --profile llm-torch-cpu --parallel 1 build llm-worker
```

Then build the separate recipe image:

```text
docker build --progress=plain -f courses/llm-applied/fixtures/pretrained/Dockerfile.optional -t ds60-pretrained-recipe:local courses/llm-applied/fixtures/pretrained
```

The image reuses local `ds60sqlpy-worker-llm-torch-cpu:0.3.0`, then installs the
complete `requirements.arm64.lock` or `requirements.amd64.lock` with required
hashes and binary wheels. Torch 2.9.1 is CPU-only. Transformers 4.57.1,
TRL 0.24.0 and PEFT 0.17.1 are explicit version choices. No CUDA dependency tree is
installed by this recipe. `pip check` must pass during the build.

The [direct declaration](pyproject.toml), [full arm64 lock](requirements.arm64.lock)
and [full amd64 lock](requirements.amd64.lock) are distinct: the declaration
expresses intended top-level dependencies, while a lock records every resolved
package and accepted artifact hashes. Maintainers regenerate locks with
`python courses/llm-applied/fixtures/pretrained/lock_dependencies.py` using uv.
Changing a lock requires a fresh image build and runtime qualification.

## 2. Acquire the pinned model deliberately

Create a named Docker volume for downloaded assets and saved training outputs:

```text
docker volume create ds60-pretrained-learning
```

This data is local to the Docker engine and persists when a run container is
removed. Reusing this volume name selects the same artifacts. It is separate
from the ordinary classroom's progress volume. Do not remove it to diagnose a
training error.

The next command is the connected model acquisition step. It explicitly enables
the Hub download client and acknowledges network access:

```text
docker run --rm --cpus 2 --memory 2g --mount type=volume,source=ds60-pretrained-learning,target=/models --env HF_HUB_OFFLINE=0 ds60-pretrained-recipe:local /recipe/prepare_assets.py --destination /models/smollm2-pinned --acknowledge-network
```

The destination must not exist. The script downloads only the fixed revision
and writes `course-assets.json` with file hashes. A partial acquisition is
retained for inspection. It does not overwrite or delete an earlier model.
Use a new destination name for a deliberate retry, then use that same name in
later commands. A network failure must be fixed before attempting training.

The scripts do not use paid services or automatically download a replacement
model. Verification checks the exact local artifact inventory, rejects unsafe
paths and unlisted files, and detects modified bytes before loading weights.

## 3. Train offline and preserve a receipt

Run the LoRA path with a bounded CPU and memory budget:

```text
docker run --rm --network none --cpus 2 --memory 6g --pids-limit 128 --mount type=volume,source=ds60-pretrained-learning,target=/models ds60-pretrained-recipe:local /recipe/train_local.py --model-dir /models/smollm2-pinned --output-dir /models/run-lora-001 --mode lora
```

For the full fine-tuning comparison, use another new output directory:

```text
docker run --rm --network none --cpus 2 --memory 6g --pids-limit 128 --mount type=volume,source=ds60-pretrained-learning,target=/models ds60-pretrained-recipe:local /recipe/train_local.py --model-dir /models/smollm2-pinned --output-dir /models/run-full-001 --mode full
```

Each run uses float 32, batch 1, seed 7 and exactly 10 updates. LoRA uses rank 4,
alpha 8, zero adapter dropout and `q_proj`/`v_proj` targets. The output directory
must be absent or empty. A repeated run needs a new name so previous models,
logs and receipts remain intact.

The 6 GiB limit is a chosen resource boundary for this short fixture, not a
promise that any model or dataset will fit. Full fine-tuning stores parameter
gradients and optimizer state. LoRA reduces trainable state but still retains
the base model and intermediate activations. Longer sequences, larger batches
and other models require new measurements. This recipe makes no GPU speed claim.

## 4. Understand the training mask

The training fixture uses conversational prompt/completion records. The
tokenizer renders the prompt with `add_generation_prompt=True` and the complete
conversation without an extra generation prompt. The script requires the prompt
token IDs to be an exact prefix of the full token IDs. It rejects any example
longer than 128 tokens, rather than truncating away its answer targets.

TRL receives `completion_only_loss=True` and `packing=False`. The processed
dataset must contain both ignored prompt positions and active completion
positions. The script then inspects an actual collated batch: ignored labels
are `-100`, and active labels equal the input token IDs at those positions.
The causal model performs the next-token shift internally. Shifting labels
again would optimize the wrong prediction target.

An attention mask controls which context positions are available; a loss mask
controls which targets contribute to optimization. Prompt tokens can provide
context without receiving a direct completion-loss term. Missing masks or an
all-active target mask fail visibly. Do not substitute all-ones labels merely
to make a run succeed.

Every completed run saves a model or adapter, a tokenizer directory and a
`receipt.json`. The receipt records update count, template lengths, trainable
parameter count, before/after evaluation losses, installed versions, source
data hashes and the pinned base revision. It is written after actual training.
An authored script or failed run does not produce a success receipt.

## 5. Reload an adapter and inspect the proposal

```text
docker run --rm --network none --cpus 2 --memory 3g --mount type=volume,source=ds60-pretrained-learning,target=/models,readonly ds60-pretrained-recipe:local /recipe/infer_local.py --model-dir /models/smollm2-pinned --adapter-dir /models/run-lora-001/model --question "How is conversion rate defined?"
```

The probe uses the pinned base, the saved adapter, a public evidence sentence,
greedy decoding and at most 64 new tokens. The tokenizer's explicit attention
mask is passed into generation. The output is a proposed answer, not a validated
metric definition. Check the formula, eligibility rule and citation against the
provided source. A truncated or unsupported answer should fail evaluation.

The tiny training task is assignment-unit extraction; it does not train a
conversion-rate assistant. The generation question deliberately tests a
different use of the model. Build a real evaluation corpus before treating an
adapted model as a subject expert. Lessons 011, 012, 022 and 024 of the applied LLM
journey explain evidence support, separated evaluation, reviewed tools and
the full assistant decision.

## 6. Export your artifacts

Use a temporary helper to access the persistent volume. Choose a helper name
that is not already used. These copy commands create ordinary local files:

```text
docker create --name ds60-pretrained-export --network none --mount type=volume,source=ds60-pretrained-learning,target=/models,readonly ds60-pretrained-recipe:local -c "print('export helper')"
docker cp ds60-pretrained-export:/models/run-lora-001 ./run-lora-001-export
docker cp ds60-pretrained-export:/models/run-full-001 ./run-full-001-export
docker rm ds60-pretrained-export
```

The helper need not run. Its mount is read-only. Verify the copied receipt and
model files before moving them to another machine. Retain the pinned base
identity and dependency lock with the adapter; an adapter alone is not the
complete model. If a local export destination exists, choose a new destination
name instead of mixing two runs.

Sources: [Transformers 4.57 chat templates](https://huggingface.co/docs/transformers/v4.57.1/en/chat_templating),
[TRL 0.24 SFTTrainer](https://huggingface.co/docs/trl/v0.24.0/en/sft_trainer),
and [PEFT LoRA configuration](https://huggingface.co/docs/peft/v0.17.0/en/package_reference/lora).
