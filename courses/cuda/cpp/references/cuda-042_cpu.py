"""cuda-042: CPU reference only, not CUDA execution."""

mib, transitions = 64, 20
modeled_moved_mib = mib * transitions
assert modeled_moved_mib == 1280
print({"simplified_transition_volume_MiB": modeled_moved_mib, "actual_migration_measured": False})
