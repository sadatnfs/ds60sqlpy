# Optional pinned pretrained-model experiment

This optional recipe is authored and statically checked. No pretrained weights were downloaded and no pretrained training was run during course authoring. The default lessons remain offline and use literal data or the tiny PyTorch decoder.

The model is `HuggingFaceTB/SmolLM2-135M-Instruct`, pinned to revision `12fd25f77366fa6b3b4b768ec3050bf629380bac`. Its model card reported `apache-2.0` when checked on2026-10-22. Review the actual model license and your own training-data permissions before choosing an intended use. The small fixture is a mechanics experiment, not a domain-assistant quality benchmark.

## Files and contracts

- [requirements.txt](requirements.txt) pins direct packages for a separate Python3.12 environment. These are real released versions checked against package metadata. This is not a complete transitive lock or a claim that this exact platform combination has executed. Resolve and retain a platform-specific hash lock and wheels before sharing a qualified environment.
- [asset_contract.json](asset_contract.json) fixes model identity and the default10-step/128-token budget.
- [prepare_assets.py](prepare_assets.py) is the only connected acquisition entry point. It refuses to run without `--acknowledge-network`, refuses an existing destination, downloads the pinned snapshot and writes a local SHA256 manifest. It is never imported or invoked by a default lesson.
- [verify_assets.py](verify_assets.py) checks revision, license metadata, safe paths and every recorded file hash using only local reads.
- [train_local.py](train_local.py) supports full SFT or LoRA on local assets, checks family isolation, template prefix alignment, completion masks and collated labels, then performs exactly10 CPU updates and writes an actual receipt only after execution.
- [infer_local.py](infer_local.py) performs optional bounded local generation from the pinned base and an optional local adapter. Its output is explicitly an unvalidated proposal. Citation and support validation remain required before treating it as an answer.
- [train.jsonl](train.jsonl) and [eval.jsonl](eval.jsonl) are authored prompt/completion fixtures with disjoint families. Four training records and one evaluation record are far too small to establish useful domain performance.

## Separate preparation from offline work

Choose a new learner-owned directory under `.learning/optional-models/`. Prepare dependencies in a separate environment using the interpreter selected by your setup. Do not replace the main classroom environment. The following package installation is an optional connected setup action, not part of default lesson execution:

```text
python -m pip install -r courses/llm-applied/fixtures/pretrained/requirements.txt
```

Acquire the model only when you deliberately choose the connected step. From the repository root, PowerShell and POSIX can use the same argument structure with their selected interpreter:

```text
python courses/llm-applied/fixtures/pretrained/prepare_assets.py --destination .learning/optional-models/smollm2-135m-pinned --acknowledge-network
```

The destination must not already exist. A failed partial acquisition is retained for inspection; the script does not delete or overwrite it. Resolve the failure deliberately and use a new destination for another acquisition. No credentials are printed or written by the course code.

Once dependencies and assets exist, the training script sets Hugging Face offline flags before importing model libraries. It calls every `from_pretrained` with a local directory and `local_files_only=True`; model loading also uses `trust_remote_code=False`. Missing or modified files fail instead of triggering a network fallback.

```text
python courses/llm-applied/fixtures/pretrained/train_local.py --model-dir .learning/optional-models/smollm2-135m-pinned --output-dir .learning/optional-models/run-lora-001 --mode lora
```

Use a different empty output directory and `--mode full` for a controlled full-SFT comparison. The scripts are CPU-first, `float32`, batch1, maximum length128, seed7 and maximum10 updates. LoRA uses rank4, alpha8, no adapter dropout and `q_proj`/`v_proj` targets. No GPU speed or memory claim is made. The resource requirement includes the pretrained base, activations, gradients and optimizer state, so it is substantially larger than the default tiny decoder.

## Inspect the mask before trusting the objective

The fixture uses conversational prompt/completion records. The tokenizer renders the prompt with `add_generation_prompt=True` and the full conversation with `add_generation_prompt=False`. The script requires the prompt IDs to be an exact prefix of the full IDs and refuses examples longer than128 tokens. This avoids silently truncating every answer target.

TRL processes the same records with `completion_only_loss=True` and `packing=False`. The script requires a completion mask containing both ignored prompt and active completion positions, then inspects an actual collated batch. Active labels must equal input token IDs at the same positions. The causal model performs its own next-token shift internally. Manually shifting these labels again would train on the wrong positions.

These checks can fail if a model template or library behavior differs from the expected contract. Preserve the failure and inspect the exact template and processed example. Do not replace missing masks with all-ones labels to make training run. The PEFT0.17.1 package pin was verified from release metadata; the official0.17.0 LoRA reference documents the relevant configuration fields.

## Evaluate and preserve actual evidence

The script records pre/post held-out loss, exact update count, template lengths, trainable parameter count, data hashes, base revision and installed versions. It saves the model or adapter plus tokenizer into the new output directory. A receipt is written only after an actual run; this repository does not contain a fabricated pretrained success receipt.

For local generation after a LoRA run:

```text
python courses/llm-applied/fixtures/pretrained/infer_local.py --model-dir .learning/optional-models/smollm2-135m-pinned --adapter-dir .learning/optional-models/run-lora-001/model --question "How is conversion rate defined?"
```

The probe supplies one public fixture source, uses greedy generation and caps new tokens at64. It does not implement real authentication, a production retriever or a complete semantic-support checker. Treat output as a proposal and validate it through the citation, abstention and tool contracts in lessons011,022 and024. Evaluate supported, unsupported, stale, contradictory and access-restricted questions before making any subject-assistant claim.

Sources: [versioned Transformers chat templates](https://huggingface.co/docs/transformers/v4.57.1/en/chat_templating), [TRL0.24 SFTTrainer](https://huggingface.co/docs/trl/v0.24.0/en/sft_trainer), [PEFT LoRA configuration](https://huggingface.co/docs/peft/v0.17.0/en/package_reference/lora), and the [pinned model card](https://huggingface.co/HuggingFaceTB/SmolLM2-135M-Instruct/tree/12fd25f77366fa6b3b4b768ec3050bf629380bac).

## Size and memory planning

The pinned model tree reports `model.safetensors` as269,060,552 bytes, about257MiB, before tokenizer/configuration files. This value was read from repository metadata without downloading the weights. The optional environment and package wheels require additional disk space, often severalGiB depending on platform and Torch distribution.

The model has roughly135million parameters. A float32 base alone is approximately540million bytes. Full-SFT parameter,gradient and two Adam-moment arrays alone are approximately2.16billion bytes before activations,temporary tensors and framework overhead. A4-8GiB CPU memory budget is a planning estimate for this small batch/context recipe,not a measured requirement or guarantee. LoRA reduces trainable gradient/optimizer state but retains the base and activations. Measure actual peak memory in the prepared environment before increasing lengths or batches.

## Optional container with persistent learner-owned artifacts

The [optional Dockerfile](Dockerfile.optional) is separate from the classroom images and has not been built by this authoring pass. Supply a reviewed,digest-pinned Python3.12 base image through `PYTHON_BASE_IMAGE`; no floating base tag is silently selected. Image preparation is connected because it installs the pinned direct dependencies. A qualified release should additionally use a complete platform-specific hash lock.

```text
docker build --build-arg PYTHON_BASE_IMAGE=<reviewed-python312-image@sha256:digest> -f courses/llm-applied/fixtures/pretrained/Dockerfile.optional -t ds60-pretrained-recipe:local courses/llm-applied/fixtures/pretrained
```

After explicit asset acquisition, mount a learner-owned model/run directory. Do not save downloaded weights or trained adapters in an ephemeral browser pad. The following offline run keeps both base artifacts and training outputs in the mounted host directory.

POSIX,from the repository root:

```bash
docker run --rm --network none --mount "type=bind,source=$(pwd)/.learning/optional-models,target=/models" ds60-pretrained-recipe:local /recipe/train_local.py --model-dir /models/smollm2-135m-pinned --output-dir /models/run-lora-001 --mode lora
```

PowerShell,from the repository root:

```powershell
$ModelRoot = (Resolve-Path .learning\optional-models).Path
docker run --rm --network none --mount "type=bind,source=$ModelRoot,target=/models" ds60-pretrained-recipe:local /recipe/train_local.py --model-dir /models/smollm2-135m-pinned --output-dir /models/run-lora-001 --mode lora
```

The directory must already exist and contain the verified model snapshot. The new run directory must be absent or empty. These are manual commands for the optional prepared image,not a claim that the default classroom includes Transformers/TRL/PEFT or that this recipe has executed.
