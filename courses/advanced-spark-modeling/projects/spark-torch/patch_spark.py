"""Compatibility preparation entrypoint; implementation lives in the pure package."""

import json
from pathlib import Path

from ds60_spark_likelihood.integrations.prepare_spark import patch_archive

if __name__ == "__main__":
    result = patch_archive(Path("/opt/spark/python/lib/pyspark.zip"))
    Path("/opt/spark/DS60_PATCHES.json").write_text(json.dumps(result, indent=2) + "\n")
