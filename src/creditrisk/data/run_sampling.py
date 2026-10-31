"""Build existing PD Parquet samples from a normalized dated evidence panel.

The old raw LendingClub snapshot is intentionally not accepted: its status and
last-payment fields cannot establish a 12-month default event.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path

import pandas as pd

from creditrisk.data.pd_artifacts import MANIFEST_NAME, sha256_file
from creditrisk.data.pd_foundation import Cohort, PDPolicy, build_model_rows
from creditrisk.data.schema import get_pd_eligible_columns


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "pd_evidenced"


def load_policy(path: Path) -> tuple[PDPolicy, list[str], dict]:
    """Read a reviewed policy, feature list and upstream source assertion."""
    spec = json.loads(path.read_text(encoding="utf-8"))
    required = {"as_of_date", "cohorts", "approved_features", "selected_features",
                "source_description", "input_sha256"}
    if (set(spec) != required or not isinstance(spec["source_description"], str)
            or not spec["source_description"].strip()
            or not isinstance(spec["input_sha256"], str)
            or not re.fullmatch(r"[0-9a-fA-F]{64}", spec["input_sha256"])):
        raise ValueError(f"Policy requires exactly {sorted(required)} and source provenance")
    if (not isinstance(spec["selected_features"], list)
            or not set(spec["selected_features"]) <= set(get_pd_eligible_columns())):
        raise ValueError("Selected PD features must belong to the model variable dictionary")
    policy = PDPolicy(
        as_of_date=date.fromisoformat(spec["as_of_date"]),
        cohorts=tuple(Cohort(item["name"], date.fromisoformat(item["start"]),
                             date.fromisoformat(item["end"])) for item in spec["cohorts"]),
        approved_features=frozenset(spec["approved_features"]),
    )
    return policy, spec["selected_features"], spec


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-jsonl", required=True, type=Path,
                        help="Source-adapted records satisfying docs/PD_TARGET_FOUNDATION.md")
    parser.add_argument("--policy", required=True, type=Path,
                        help="Reviewed as-of, cohorts, selected features and input SHA-256")
    args = parser.parse_args()
    policy, features, spec = load_policy(args.policy)
    if sha256_file(args.evidence_jsonl).lower() != spec["input_sha256"].lower():
        raise ValueError("Normalized evidence file SHA-256 differs from reviewed policy")
    with args.evidence_jsonl.open(encoding="utf-8") as handle:
        rows = [json.loads(line) for line in handle if line.strip()]
    samples, exclusions = build_model_rows(rows, policy, features)
    if any(not samples[name] for name in ("train", "test", "oot")):
        raise ValueError("Every chronological PD sample must contain eligible loans")

    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    hashes = {}
    for name, model_rows in samples.items():
        path = PROCESSED_DATA_DIR / f"{name}.parquet"
        pd.DataFrame(model_rows).to_parquet(path, index=False)
        hashes[name] = sha256_file(path)
    manifest = {
        "contract": "pd-foundation-12m-v1",
        "source_description": spec["source_description"],
        "input_sha256": spec["input_sha256"].lower(),
        "as_of_date": spec["as_of_date"],
        "cohorts": spec["cohorts"],
        "selected_features": features,
        "sample_counts": {name: len(value) for name, value in samples.items()},
        "exclusions": exclusions,
        "sample_sha256": hashes,
    }
    (PROCESSED_DATA_DIR / MANIFEST_NAME).write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("Wrote evidenced PD samples and exclusion manifest; no model was trained")


if __name__ == "__main__":
    main()
