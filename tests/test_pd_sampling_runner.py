"""Synthetic round trip for the existing Parquet sampling interface."""

import hashlib
import json
import sys

import pandas as pd
import pytest

from creditrisk.data import run_sampling
from creditrisk.data.pd_artifacts import require_evidenced_samples


def test_evidenced_sampling_writes_only_eligible_chronological_rows(tmp_path, monkeypatch):
    def loan(identifier, originated, decided, observed, **changes):
        row = {
            "loan_id": identifier,
            "origination_date": originated,
            "decision_at": decided,
            "observed_through": observed,
            "event_history_complete": True,
            "default_event_date": None,
            "default_event_type": None,
            "default_event_source": None,
            "observed_status": "Current",
            "features": {"annual_inc": 50000},
            "feature_observed_at": {"annual_inc": decided},
        }
        row.update(changes)
        return row

    rows = [
        loan("train", "2009-01-01", "2008-12-31T12:00:00+00:00", "2010-01-01"),
        loan("test", "2011-01-01", "2010-12-31T12:00:00+00:00", "2012-01-01",
             default_event_date="2011-06-01", default_event_type="charge_off",
             default_event_source="synthetic ledger"),
        loan("oot", "2013-01-01", "2012-12-31T12:00:00+00:00", "2014-01-01"),
        loan("censored", "2013-02-01", "2013-01-31T12:00:00+00:00", "2013-08-01"),
    ]
    evidence = tmp_path / "synthetic.jsonl"
    evidence.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    policy = {
        "as_of_date": "2015-01-01",
        "cohorts": [
            {"name": "train", "start": "2007-01-01", "end": "2010-01-01"},
            {"name": "test", "start": "2011-01-01", "end": "2012-01-01"},
            {"name": "oot", "start": "2013-01-01", "end": "2014-01-01"},
        ],
        "approved_features": ["annual_inc"],
        "selected_features": ["annual_inc"],
        "source_description": "synthetic fixture only",
        "input_sha256": hashlib.sha256(evidence.read_bytes()).hexdigest(),
    }
    policy_path = tmp_path / "policy.json"
    policy_path.write_text(json.dumps(policy), encoding="utf-8")
    processed = tmp_path / "processed"
    monkeypatch.setattr(run_sampling, "PROCESSED_DATA_DIR", processed)
    monkeypatch.setattr(sys, "argv", ["run_sampling", "--evidence-jsonl", str(evidence),
                                  "--policy", str(policy_path)])
    run_sampling.main()

    manifest = require_evidenced_samples(processed)
    assert manifest["exclusions"]["censored_or_incomplete"] == 1
    assert manifest["sample_counts"] == {"train": 1, "test": 1, "oot": 1}
    assert pd.read_parquet(processed / "test.parquet")["default_12m"].tolist() == [1]

    policy["input_sha256"] = "0" * 64
    policy_path.write_text(json.dumps(policy), encoding="utf-8")
    with pytest.raises(ValueError, match="SHA-256 differs"):
        run_sampling.main()
