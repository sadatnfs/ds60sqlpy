"""Optional bounded pretrained SFT. All assets must already exist locally."""
from __future__ import annotations
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
from verify_assets import verify_assets


def read_records(path: Path) -> list[dict]:
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    if not 1 <= len(rows) <= 32:
        raise ValueError('This optional fixture accepts1..32 records per partition')
    ids = [row['id'] for row in rows]
    if len(set(ids)) != len(ids):
        raise ValueError('Duplicate record IDs')
    for row in rows:
        if set(row) != {'id', 'family', 'prompt', 'completion'}:
            raise ValueError('Exact record fields required')
        if not row['prompt'] or len(row['completion']) != 1 or row['completion'][0]['role'] != 'assistant':
            raise ValueError('Prompt and one assistant completion required')
        for message in row['prompt'] + row['completion']:
            if set(message) != {'role', 'content'} or not isinstance(message['content'], str):
                raise ValueError('Message schema mismatch')
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-dir', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--mode', choices=['lora', 'full'], default='lora')
    args = parser.parse_args()
    manifest = verify_assets(args.model_dir)
    if args.output_dir.exists() and any(args.output_dir.iterdir()):
        parser.error('Output directory must be absent or empty; prior work is preserved')
    # Set these before importing libraries that can resolve remote artifacts.
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['TRANSFORMERS_OFFLINE'] = '1'
    os.environ['HF_DATASETS_OFFLINE'] = '1'
    import torch
    from datasets import Dataset
    from peft import LoraConfig
    from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed
    from trl import SFTConfig, SFTTrainer

    # Seed before SFTTrainer creates the randomly initialized LoRA matrices.
    # TrainingArguments.seed alone is applied too late for that construction.
    set_seed(7)
    folder = Path(__file__).parent
    training = read_records(folder / 'train.jsonl')
    evaluation = read_records(folder / 'eval.jsonl')
    if {row['family'] for row in training} & {row['family'] for row in evaluation}:
        raise ValueError('Training/evaluation family leakage')
    tokenizer = AutoTokenizer.from_pretrained(str(args.model_dir), local_files_only=True, trust_remote_code=False)
    if tokenizer.chat_template is None or tokenizer.eos_token_id is None:
        raise ValueError('A reviewed chat template and EOS token are required')
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    template_checks = []
    for row in training + evaluation:
        prompt_ids = tokenizer.apply_chat_template(row['prompt'], tokenize=True, add_generation_prompt=True)
        full_ids = tokenizer.apply_chat_template(row['prompt'] + row['completion'], tokenize=True, add_generation_prompt=False)
        if full_ids[:len(prompt_ids)] != prompt_ids or len(full_ids) <= len(prompt_ids):
            raise ValueError('Chat template does not preserve the checked prompt/completion prefix')
        if len(full_ids) > 128:
            raise ValueError('Fixture exceeds128 tokens; do not silently truncate answer targets')
        template_checks.append({'id': row['id'], 'prompt_tokens': len(prompt_ids), 'total_tokens': len(full_ids)})
    model = AutoModelForCausalLM.from_pretrained(
        str(args.model_dir), local_files_only=True, trust_remote_code=False,
        dtype=torch.float32, attn_implementation='eager',
    )
    model.config.use_cache = False
    adapter = None if args.mode == 'full' else LoraConfig(
        r=4, lora_alpha=8, lora_dropout=0.0, target_modules=['q_proj', 'v_proj'],
        bias='none', task_type='CAUSAL_LM',
    )
    config = SFTConfig(
        output_dir=str(args.output_dir), max_steps=10, max_length=128,
        per_device_train_batch_size=1, per_device_eval_batch_size=1,
        gradient_accumulation_steps=1, learning_rate=1e-4, seed=7,
        use_cpu=True, bf16=False, fp16=False, packing=False,
        completion_only_loss=True, logging_steps=1, save_strategy='no',
        eval_strategy='no', report_to=[], dataloader_num_workers=0,
    )
    clean = lambda rows: [{key: row[key] for key in ('prompt', 'completion')} for row in rows]
    trainer = SFTTrainer(
        model=model, args=config, train_dataset=Dataset.from_list(clean(training)),
        eval_dataset=Dataset.from_list(clean(evaluation)), processing_class=tokenizer,
        peft_config=adapter,
    )
    for row in trainer.train_dataset:
        mask = row.get('completion_mask')
        if mask is None or not any(mask) or all(mask):
            raise ValueError('Processed data must retain prompt and completion participation masks')
        first = mask.index(1)
        if any(mask[:first]) or not all(mask[first:]):
            raise ValueError('Expected one contiguous completion under this fixture contract')
    batch = next(iter(trainer.get_train_dataloader()))
    active = batch['labels'] != -100
    if not bool(active.any()) or not bool((~active).any()):
        raise ValueError('Collated batch must include ignored prompt and active answer labels')
    if not torch.equal(batch['labels'][active], batch['input_ids'][active]):
        raise ValueError('Unexpected label shift in collator; causal model owns the shift')
    before = trainer.evaluate()
    result = trainer.train()
    after = trainer.evaluate()
    if trainer.state.global_step != 10:
        raise RuntimeError('Unexpected update count')
    trainer.save_model(str(args.output_dir / 'model'))
    tokenizer.save_pretrained(str(args.output_dir / 'tokenizer'))
    receipt = {
        'status': 'executed', 'mode': args.mode, 'base_revision': manifest['revision'],
        'steps': trainer.state.global_step, 'template_checks': template_checks,
        'trainable_parameters': sum(p.numel() for p in trainer.model.parameters() if p.requires_grad),
        'before_eval': before, 'after_eval': after, 'training_metrics': result.metrics,
        'data_hashes': {name: hashlib.sha256((folder / name).read_bytes()).hexdigest() for name in ['train.jsonl', 'eval.jsonl']},
        'versions': {name: importlib.metadata.version(name) for name in ['torch', 'transformers', 'trl', 'peft', 'datasets', 'accelerate']},
        'scope': 'Tiny authored task; no production or domain-expertise acceptance claim',
    }
    (args.output_dir / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'steps': receipt['steps'], 'mode': args.mode, 'receipt': str(args.output_dir / 'receipt.json')}))


if __name__ == '__main__':
    main()
