"""Read actual JVM-emitted analytic fixtures, with explicitly synthetic artifact metadata."""

import hashlib
import json
import unittest
from pathlib import Path

from ds60_spark_tmbad import FittedModel, PreparedParameters, PreparedRuntime
from ds60_spark_tmbad._evaluation import validate_evaluation


class JvmTargetParityTests(unittest.TestCase):
    def test_current_jvm_target_and_parameter_documents_parse_without_projection(self):
        root = Path(__file__).parent / "fixtures/jvm-target-v2"
        scope = json.loads((root / "SCOPE.json").read_text())
        self.assertFalse(scope["native_executed"])
        self.assertFalse(scope["spark_executed"])
        for name, digest in scope["files"].items():
            self.assertEqual(hashlib.sha256((root / name).read_bytes()).hexdigest(), digest)
        runtime = PreparedRuntime(json.loads((root / "synthetic-manifest.json").read_text()))
        checked = []
        for path in sorted(root.glob("*.json")):
            value = json.loads(path.read_text())
            if value.get("kind") == "spark-tmbad-model":
                FittedModel(runtime, value)
            elif value.get("kind") == "spark-tmbad-parameter-set":
                PreparedParameters(runtime, value)
            elif value.get("kind") == "spark-tmbad-evaluation":
                fitted = json.loads(
                    (root / path.name.replace("evaluation-", "schema2-")).read_text()
                )
                options = {
                    "reduction": value["reduction"],
                    "regularization": fitted["target"]["regularization"],
                    "fixed_parameters": fitted["target"]["fixed_parameters"],
                }
                validate_evaluation(value, runtime, value["model_id"], value["parameters"], options)
            else:
                continue
            checked.append(path.name)
        self.assertEqual(len(checked), 12)


if __name__ == "__main__":
    unittest.main()
