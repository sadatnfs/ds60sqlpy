# Cross-language IPC and actual Arrow Flight

Prepare the native `data-platforms-python` and `rust-stable` classroom images.
From a copied Arrow Flight workshop directory:

```bash
bash run.sh start
bash run.sh ipc-check
bash run.sh check
```

`ipc-check` compiles the checked-in `ipc_bridge.rs` using only the prepared Arrow60
library. It exchanges a nullable three-row IPC stream with Python Arrow23, checks
exact semantics and removes only its two temporary stream files. No Cargo download
occurs during execution. The real Flight check separately validates the service
read, source digest and invalid descriptor/ticket behavior.

```bash
bash run.sh stop
bash run.sh resume
bash run.sh check
bash run.sh down
bash run.sh start
bash run.sh check
```

Follow the project README for ownership and explicitly confirmed data deletion.
This notebook is read and edited in the classroom; service commands run from the
copied workshop in the host/WSL terminal.
