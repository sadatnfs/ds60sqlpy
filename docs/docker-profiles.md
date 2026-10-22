# Optional Docker lesson packages

The normal image installs Core: notebooks, data science, Python/PostgreSQL integration, professional tools, SQL notebooks, and quality tools. It keeps the first download smaller. Optional packages are installed only when you explicitly build another profile. Clicking Run never installs a missing package.

The app reports two separate facts: whether its Python/SQL backend can run a snippet, and whether the selected lesson's full package profile is present. A missing optional profile does not prevent standard-library practice. An installed package is not proof that its native imports, model files, dataset cache, GPU, external service, or full notebook workflow have been verified.

| `DS60_DOCKER_PROFILES` value | Adds to Core |
|---|---|
| `core` | The default package set |
| `ml` | XGBoost, LightGBM, SHAP, LIME, pmdarima, imbalance tools, Numba |
| `production` | FastAPI, Dask, MLflow, Prefect, Pydantic, Uvicorn |
| `deep-learning` | PyTorch and torchvision |
| `nlp` | Transformers, datasets, evaluate, spaCy, accelerate |
| `geo` | GeoPandas, geodatasets, contextily, NetworkX |
| `advanced` | All five optional lesson groups above |

You can combine names, for example `deep-learning,nlp`. Other exact optional extras declared in `pyproject.toml`, such as `mcp`, can also be selected. Unknown names, URLs and installer arguments are rejected before installation. Core remains included.

## Build the package set you need

Copy `.env.example` to `.env` if you do not already have `.env`. Preserve any existing settings. Set these values:

```dotenv
DS60_DOCKER_PROFILES=deep-learning,nlp
DS60_LAB_MEMORY=4g
```

Build explicitly, then start. From Windows PowerShell, with no Python or Git prerequisite:

```powershell
.\START_DOCKER_LAB.cmd -Action build
.\START_DOCKER_LAB.cmd -Action start
```

From macOS, Linux, or a WSL shell:

```bash
bash scripts/docker_lab.sh start --build
```

These commands build locally. They do not push an image. Changing `.env` without rebuilding does not add or remove Python packages. Rebuilding replaces the local image tag; restarting recreates the app's official course copy while retaining the host `.learning` directory and database volume. See [persistent storage](offline-app.md) before moving or backing up a course folder.

All selected extras come from the frozen `uv.lock`. Linux and Windows locked environments use the official CPU-only PyTorch index; macOS retains its platform-specific wheel choices. The default Compose service does not request a GPU. GPU drivers, compatible GPU wheels, container device access, and GPU validation require a separate explicit setup. The [official uv PyTorch integration guide](https://docs.astral.sh/uv/guides/integration/pytorch/) explains the index distinction. Unlocked pip installation does not use `tool.uv.sources` and may choose different wheels.

## Memory, downloads and offline work

Core limits the app container to `2g` by default. `DS60_LAB_MEMORY` changes that container limit; it does not add physical RAM or increase the engine VM's allocation. Choose a value within your engine and host capacity. Long training jobs can still exceed the selected 15, 60 or 120 second coding-pad limit; use the notebook workflow for longer work.

Advanced is substantially larger. The repaired Linux arm64 proof image reported 1,257,193,256 bytes (about 1.26 GB) through Docker image inspection. Separately, BuildKit reported about 4.5 GB for an unpacked dependency build-cache record and 3.4 GB for its shared package cache. Those build-cache records include retained intermediate work and are not the final image size or an amount you can simply add to it. Repeated rebuilds need additional temporary disk space. These observations cover one architecture and lock, not universal size guarantees. Select the groups you need and inspect available space before building. Do not broadly prune another project's images, volumes or cache to make room.

Package installation does not download pretrained models, trained spaCy pipelines, map tiles or every example dataset. Prepare the exact assets described by the lesson before disconnecting. Container home and caches live below the host `.learning` directory; paths and first-run downloads chosen by learner code still matter. Inspect the lesson's network hint. `HF_HUB_OFFLINE=1` and the library-specific offline settings can verify a prewarmed Hugging Face workflow without silently fetching a missing model.

The browser runs an ordinary Python program, marked notebook cells, or a guarded whole SQL script. Notebook starters preserve `# %%` boundaries; with IPython installed, cells and magics run in sequence with one shared namespace inside that Run, including inline PNG plots. Each Run starts a fresh process. Persistent kernels, interactive services, infrastructure changes, privileged server exercises and long training have their own notebook or external workflows. Registering a C++, Scala, or Kubernetes lesson does not install an execution adapter; unavailable adapters support reading and saved source without claiming a successful run.

The Advanced Linux arm64 proof imported the optional package groups with networking disabled and ran tiny CPU autograd, randomly initialized BERT, blank spaCy, and geospatial geometry checks. It downloaded no pretrained model. That proof does not establish native Windows/macOS imports, GPU execution, trained-model quality, or production service acceptance.
