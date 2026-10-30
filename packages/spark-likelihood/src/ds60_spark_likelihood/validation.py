"""Explicit installed-wheel qualification; never invoked by package import or fit."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import shutil
import sys
from pathlib import Path


def assert_installed_wheel():
    """Refuse source-tree masking when claiming an installed distribution pass."""
    import ds60_torch_training as training_package

    import ds60_spark_likelihood as package

    distribution = importlib.metadata.distribution("ds60-spark-likelihood")
    if distribution.read_text("WHEEL") is None:
        raise RuntimeError("validation requires wheel metadata, not source-tree egg-info")
    direct_url = distribution.read_text("direct_url.json")
    if direct_url and json.loads(direct_url).get("dir_info", {}).get("editable"):
        raise RuntimeError("validation requires a non-editable installed wheel")
    declared = distribution.locate_file("ds60_spark_likelihood/__init__.py").resolve()
    actual = Path(package.__file__).resolve()
    if actual != declared or not actual.is_file():
        raise RuntimeError(
            "validation must resolve the installed wheel, not an editable/source checkout"
        )
    training_declared = distribution.locate_file("ds60_torch_training/__init__.py").resolve()
    training_actual = Path(training_package.__file__).resolve()
    if training_actual != training_declared or not training_actual.is_file():
        raise RuntimeError("Torch training must resolve through the same installed wheel")
    files = {str(path) for path in distribution.files or ()}
    required_training = {
        "ds60_torch_training/" + name + ".py"
        for name in (
            "__init__",
            "_integration_fixture",
            "contracts",
            "program",
            "data",
            "checkpoint",
            "torch_adapter",
            "runner",
            "launch",
            "observer",
            "training_examples",
        )
    }
    if not required_training <= files:
        raise RuntimeError("Installed wheel is missing a Torch training source module")
    try:
        importlib.metadata.distribution("ds60-torch-training-draft")
    except importlib.metadata.PackageNotFoundError:
        pass
    else:
        raise RuntimeError("Obsolete separate draft wheel masks one-wheel acceptance")
    if any(path.startswith("ds60sqlpy/") for path in files):
        raise RuntimeError("standalone wheel unexpectedly contains classroom code")
    if any(name == "ds60sqlpy" or name.startswith("ds60sqlpy.") for name in sys.modules):
        raise RuntimeError("standalone qualification imported the classroom")
    print(
        json.dumps(
            {
                "kind": "package-wheel-isolation",
                "passed": True,
                "version": distribution.version,
                "module_path": str(actual),
                "training_module_path": str(training_actual),
                "classroom_imported": False,
                "rscript_present": shutil.which("Rscript") is not None,
            },
            sort_keys=True,
        )
    )


def main(arguments=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", choices=("numerical", "spark", "ml"))
    args = parser.parse_args(arguments)
    assert_installed_wheel()
    if any(name == "ds60sqlpy" or name.startswith("ds60sqlpy.") for name in sys.modules):
        raise RuntimeError("standalone qualification must not import the classroom")
    if args.case == "numerical":
        from .validation_gamma_poisson import numerical as custom_unit
        from .validation_predictions import run as predictions
        from .validation_rows import run as rows
        from .validation_units import run as units

        rows()
        units()
        predictions()
        custom_unit()
    elif args.case == "spark":
        from .validation_gamma_poisson import spark_check as custom_unit
        from .validation_spark_rows import run as rows
        from .validation_spark_units import run as units

        rows()
        units()
        custom_unit()
    else:
        from .validation_dataframe_ml import main as run

        run()


if __name__ == "__main__":
    main()
