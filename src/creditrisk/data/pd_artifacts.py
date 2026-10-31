"""Provenance gate for the existing Parquet-based PD runners.

The manifest records a caller-supplied source description and hashes the
normalized evidence file and generated samples. It cannot authenticate the
upstream event ledger or prove the adapter's source assertions.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


SAMPLES = ("train", "test", "oot")
MANIFEST_NAME = "pd_evidence_manifest.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_evidenced_samples(processed_dir: Path) -> dict:
    """Refuse legacy or modified Parquet inputs before PD modelling runs."""
    manifest_path = processed_dir / MANIFEST_NAME
    if not manifest_path.is_file():
        raise ValueError("Missing PD evidence manifest; legacy target samples are not eligible")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (manifest.get("contract") != "pd-foundation-12m-v1"
            or not manifest.get("source_description")
            or not re.fullmatch(r"[0-9a-f]{64}", str(manifest.get("input_sha256", "")))
            or not manifest.get("selected_features")
            or set(manifest.get("sample_sha256", {})) != set(SAMPLES)):
        raise ValueError("Incomplete PD evidence manifest")
    if any(not re.fullmatch(r"[0-9a-f]{64}", str(value))
           for value in manifest["sample_sha256"].values()):
        raise ValueError("Invalid PD sample checksum in manifest")
    for sample in SAMPLES:
        path = processed_dir / f"{sample}.parquet"
        if not path.is_file() or sha256_file(path) != manifest["sample_sha256"][sample]:
            raise ValueError(f"PD evidence sample missing or changed: {sample}")
    return manifest


def bind_artifact(path: Path, processed_dir: Path) -> None:
    """Bind a fitted artifact to the exact evidenced sample manifest."""
    require_evidenced_samples(processed_dir)
    binding = {"manifest_sha256": sha256_file(processed_dir / MANIFEST_NAME),
               "artifact_sha256": sha256_file(path)}
    path.with_name(path.name + ".pd-evidence.json").write_text(
        json.dumps(binding, indent=2) + "\n", encoding="utf-8")


def require_bound_artifact(path: Path, processed_dir: Path) -> None:
    """Reject stale binning/model artifacts from another target or sample set."""
    require_evidenced_samples(processed_dir)
    binding_path = path.with_name(path.name + ".pd-evidence.json")
    if not path.is_file() or not binding_path.is_file():
        raise ValueError(f"Missing PD evidence binding for {path.name}")
    binding = json.loads(binding_path.read_text(encoding="utf-8"))
    if (binding.get("manifest_sha256") != sha256_file(processed_dir / MANIFEST_NAME)
            or binding.get("artifact_sha256") != sha256_file(path)):
        raise ValueError(f"PD artifact differs from evidenced samples: {path.name}")
