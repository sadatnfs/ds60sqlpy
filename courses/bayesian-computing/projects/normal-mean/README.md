# Standard Stan data-block project

This optional project uses the same normal-mean question as bayes-017 while
separating reusable model code from a real JSON data file. It is distinct from
the classroom's single-source Stan pad, whose bounded fixtures live in
`transformed data`. The pad does not accept a second JSON editor or arbitrary
compiler arguments.

## Files and mathematical oracle

- [model.stan](model.stan) declares a standard data block, one parameter and generated values.
- [data.json](data.json) provides five measurements, prior settings and known observation noise.
- [run.py](run.py) validates the data, compiles a copied model, samples four serial chains,
  retains CSVs/diagnostics and records exact model/data hashes.
- [requirements.txt](requirements.txt) pins the optional Python interface to CmdStanPy 1.3.0.

For the supplied fixture the exact posterior mean is \(40/21\) and variance \(4/21\).
The sample mean should be compared using its Monte Carlo error, not exact equality.
A zero process exit does not certify convergence or a scientifically valid model.

## Prepare the Docker toolchain

Use the repository's Linux Stan image on Linux, macOS or Windows through WSL 2.
No host Python installation or C++ compiler is required. From the repository
root, prepare the locally built image once:

```sh
./classroom build --profile stan-cpu --local-build
```

The build installs the pinned CmdStan 2.40.0 toolchain and CmdStanPy 1.3.0. It
needs network access to prepare dependencies. Running the project below needs
no network access and does not rebuild the image. The image name shown here is
for release 1.1.0; use the matching local release tag if working on a later release.

## Compile, sample and save results

From the repository root, enter this project and create its output parent:

```sh
cd courses/bayesian-computing/projects/normal-mean
mkdir -p work
```

Run the complete model and JSON data through CmdStanPy:

```sh
docker run --rm --init \
  --network none --read-only --cap-drop ALL \
  --security-opt no-new-privileges \
  --user "$(id -u):$(id -g)" \
  --cpus 2 --memory 3g --pids-limit 128 \
  --env HOME=/tmp --tmpfs /tmp:rw,nosuid,exec,size=256m \
  --mount "type=bind,src=$PWD,dst=/project,readonly" \
  --mount "type=bind,src=$PWD/work,dst=/output" \
  --entrypoint python ds60sqlpy-worker-stan-cpu:1.1.0 \
  /project/run.py --cmdstan /opt/cmdstan --output /output/normal-mean-run
```

These commands use a POSIX shell, including the WSL 2 shell on Windows. The
project is mounted read-only and copied into its own writable output directory
before compilation. The numerical work runs inside Linux; output files belong
to your host user and remain under `work/normal-mean-run` after the temporary
container exits. `--rm` removes only this temporary container, not those files.
No classroom progress or database volume is mounted or changed.

Review `summary.csv`, `diagnostics.txt` and `run.json` together with the chain
CSVs in `chains/`. The copied `model.stan` and `data.json` make the calculation
reviewable; `run.json` records their hashes and the analytic posterior oracle.
The chain CSV headers retain sampler settings. The default is four serial
chains with 1000 warmup and 1000 retained draws per chain. This is a starting
configuration, not a convergence guarantee. The first run compiles the model
inside the container; an existing classroom image does not skip compilation
of this separate project model.

Choose a new output name for each run, such as `/output/wider-prior-run`. The
driver refuses to overwrite an existing directory, including one from an
interrupted attempt. `--warmup` and `--draws` accept integers from 100 through
5000. To use another local fixture, place it in this project directory and add
`--data /project/other-data.json`; it must match the declared schema. No cloud
account or external dataset is used.

## Optional native contributor environment

Contributors who deliberately prefer a native Linux environment can prepare
Python, a compatible C++ build toolchain and CmdStan 2.40.0 using the
[official installation guide](https://mc-stan.org/cmdstanpy/installation.html).
This driver does not install CmdStan or download packages automatically. Use
project and toolchain directories without spaces for the underlying Make build.
From this project directory, after preparing the toolchain:

```sh
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python run.py --cmdstan /absolute/path/to/cmdstan-2.40.0 --output work/native-run
```

## Two comparisons

1. Change the prior standard deviation while keeping data fixed. Explain how
   posterior precision combines prior and likelihood precision. Retain both
   manifests rather than rewriting the original result.
2. Change the known observation standard deviation. This changes the likelihood,
   not merely a display setting. Recompute the analytic posterior and compare
   the sampled uncertainty with the appropriate new target.

For prediction, `y_rep` includes observation variation around the unknown mean.
Its spread is different from the posterior spread of `mu`. `log_lik` contains
per-observation log densities, which support only the corresponding predictive
unit and assumptions. Separate larger scientific workflows should declare their
own data contracts, storage, convergence and evaluation requirements.
