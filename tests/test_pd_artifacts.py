"""Synthetic manifest checks that do not require modelling dependencies."""

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from creditrisk.data.pd_artifacts import (  # noqa: E402
    MANIFEST_NAME, bind_artifact, require_bound_artifact,
    require_evidenced_samples, sha256_file,
)


class PDEvidenceArtifactTests(unittest.TestCase):
    def test_missing_manifest_rejects_legacy_samples(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "Missing PD evidence manifest"):
                require_evidenced_samples(Path(directory))

    def test_sample_and_model_hashes_are_bound_to_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sample_hashes = {}
            for name in ("train", "test", "oot"):
                path = root / f"{name}.parquet"
                path.write_bytes(f"synthetic {name}".encode())
                sample_hashes[name] = sha256_file(path)
            manifest = {
                "contract": "pd-foundation-12m-v1",
                "source_description": "synthetic test fixture",
                "input_sha256": hashlib.sha256(b"synthetic panel").hexdigest(),
                "selected_features": ["annual_inc"],
                "sample_sha256": sample_hashes,
            }
            (root / MANIFEST_NAME).write_text(json.dumps(manifest), encoding="utf-8")
            require_evidenced_samples(root)
            model = root / "model.pkl"
            model.write_bytes(b"synthetic fitted model")
            bind_artifact(model, root)
            require_bound_artifact(model, root)
            model.write_bytes(b"stale model")
            with self.assertRaisesRegex(ValueError, "artifact differs"):
                require_bound_artifact(model, root)
            model.write_bytes(b"synthetic fitted model")
            (root / "test.parquet").write_bytes(b"changed sample")
            with self.assertRaisesRegex(ValueError, "sample missing or changed"):
                require_bound_artifact(model, root)


if __name__ == "__main__":
    unittest.main()
