"""Original two-process CPU training cases launched by Spark TorchDistributor.

These qualify single-machine process coordination and gradient semantics. They
do not qualify a remote cluster, GPU resource allocation or multi-node failure
recovery. No rank reads an implicit full training dataset.
"""

from __future__ import annotations


def train_ddp_step():
    import datetime

    import torch
    import torch.distributed as dist
    from torch.nn.parallel import DistributedDataParallel

    torch.set_num_threads(1)
    dist.init_process_group("gloo", timeout=datetime.timedelta(seconds=60))
    try:
        rank, world = dist.get_rank(), dist.get_world_size()
        assert world in {1, 2}
        # Unequal shard sizes intentionally expose the rank-mean weighting error.
        ids = list(range(6)) if world == 1 else ([0, 1, 2, 3] if rank == 0 else [4, 5])
        all_y = [0.0, 1.0, 1.0, 1.0, 1.0, 0.0]
        y = torch.tensor([all_y[i] for i in ids], dtype=torch.float64)
        x = torch.ones((len(ids), 1), dtype=torch.float64)
        model = torch.nn.Linear(1, 1, bias=False, dtype=torch.float64)
        with torch.no_grad():
            model.weight.zero_()
        model = DistributedDataParallel(model)
        count = torch.tensor(float(len(ids)), dtype=torch.float64)
        dist.all_reduce(count, op=dist.ReduceOp.SUM)
        optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
        optimizer.zero_grad()
        local_sum = torch.nn.functional.binary_cross_entropy_with_logits(
            model(x).flatten(), y, reduction="sum"
        )
        # DDP averages rank gradients: undo that average before dividing by N.
        objective = local_sum * world / count
        objective.backward()
        gradient = float(model.module.weight.grad.item())
        assert abs(gradient + 1 / 6) < 1e-12
        optimizer.step()
        value = float(model.module.weight.item())
        assert abs(value - 1 / 60) < 1e-12
        shard_ids = [None] * world
        dist.all_gather_object(shard_ids, ids)
        flattened = [item for shard in shard_ids for item in shard]
        assert len(flattened) == len(set(flattened)) == 6
        assert sorted(flattened) == list(range(6))
        rank_values = [None] * world
        dist.all_gather_object(rank_values, value)
        assert max(rank_values) - min(rank_values) < 1e-14
        return {
            "kind": "spark-torch-distributor-ddp",
            "passed": True,
            "world_size": world,
            "rank_shards": shard_ids,
            "global_observations": int(count.item()),
            "gradient": gradient,
            "parameter_after_step": value,
            "rank_parameters": rank_values,
            "backend": "gloo",
            "multi_node_executed": False,
            "gpu_executed": False,
        }
    finally:
        dist.destroy_process_group()


def train_lightning_step():
    import torch
    import torch.distributed as dist
    from lightning.pytorch import LightningModule, Trainer
    from torch.utils.data import DataLoader, TensorDataset

    torch.set_num_threads(1)

    class BernoulliIntercept(LightningModule):
        def __init__(self):
            super().__init__()
            self.coefficient = torch.nn.Parameter(torch.zeros((), dtype=torch.float64))
            self.observed_ids = []

        def training_step(self, batch, batch_index):
            ids, targets = batch
            self.observed_ids.extend(int(item) for item in ids.tolist())
            # Equal shards here. Unequal shards need the explicit DDP sum scaling
            # shown in train_ddp_step, not the unweighted mean used below.
            return torch.nn.functional.binary_cross_entropy_with_logits(
                self.coefficient.expand_as(targets), targets, reduction="mean"
            )

        def configure_optimizers(self):
            return torch.optim.SGD(self.parameters(), lr=0.1)

    model = BernoulliIntercept()
    ids = torch.arange(6)
    targets = torch.tensor([0, 1, 1, 1, 1, 0], dtype=torch.float64)
    # Lightning installs a DistributedSampler. Six records divide exactly by two,
    # so this case introduces no padded duplicate observations.
    loader = DataLoader(TensorDataset(ids, targets), batch_size=3, shuffle=False, num_workers=0)
    trainer = Trainer(
        accelerator="cpu",
        devices=2,
        num_nodes=1,
        strategy="ddp",
        precision="64-true",
        max_epochs=1,
        max_steps=1,
        logger=False,
        enable_checkpointing=False,
        enable_progress_bar=False,
        enable_model_summary=False,
        num_sanity_val_steps=0,
        deterministic=True,
        use_distributed_sampler=True,
        default_root_dir="/tmp/lightning-case",
    )
    try:
        trainer.fit(model, train_dataloaders=loader)
        value = float(model.coefficient.detach().item())
        assert abs(value - 1 / 60) < 1e-12
        gathered = [None] * dist.get_world_size()
        dist.all_gather_object(gathered, model.observed_ids)
        all_ids = [item for shard in gathered for item in shard]
        assert sorted(all_ids) == list(range(6))
        assert len(all_ids) == len(set(all_ids))
        result = {
            "kind": "spark-torch-distributor-lightning",
            "passed": True,
            "world_size": dist.get_world_size(),
            "rank_shards": gathered,
            "parameter_after_step": value,
            "global_step": trainer.global_step,
            "multi_node_executed": False,
            "gpu_executed": False,
        }
        dist.barrier()
        return result
    finally:
        if dist.is_initialized():
            dist.destroy_process_group()


def sampler_audit():
    import torch
    from torch.utils.data import DistributedSampler

    dataset = torch.arange(5)
    padded = [
        list(DistributedSampler(dataset, num_replicas=2, rank=r, shuffle=False)) for r in range(2)
    ]
    dropped = [
        list(DistributedSampler(dataset, num_replicas=2, rank=r, shuffle=False, drop_last=True))
        for r in range(2)
    ]
    flat = [x for shard in padded for x in shard]
    assert len(flat) == 6 and len(set(flat)) == 5
    assert sum(len(shard) for shard in dropped) == 4
    exact = [list(range(r, len(dataset), 2)) for r in range(2)]
    assert sorted(x for shard in exact for x in shard) == list(range(5))
    return {
        "kind": "sampler-padding-audit",
        "passed": True,
        "dataset_rows": 5,
        "default_padded_shards": padded,
        "drop_last_shards": dropped,
        "explicit_unequal_shards": exact,
        "training_executed": False,
    }
