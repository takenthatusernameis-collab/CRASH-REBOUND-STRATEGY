"""Tests for campaign resume / checkpoint-restart accounting.

A long-running Kilo campaign can be interrupted (idle timeout, worker
restart). On resume it must rebuild its working set from the durable
ledger without re-processing already-completed work or losing in-flight
state. These tests pin the resume accounting contract.
"""

import json

import pytest


def rebuild_campaign_state(ledger_records, completed_keys):
    """Reconstruct the campaign's working set from a ledger snapshot.

    Returns (pending, resumed) where `pending` is work not yet recorded as
    completed and `resumed` is in-flight work picked back up.
    """
    pending = []
    resumed = []
    for key, record in ledger_records.items():
        status = record.get("status")
        if key in completed_keys:
            continue
        if status == "completed":
            continue
        if status == "in_progress":
            resumed.append(key)
        else:
            pending.append(key)
    return pending, resumed


def make_record(status, attempt=1):
    return {"status": status, "capture_attempts": attempt}


def test_empty_ledger_yields_all_pending():
    pending, resumed = rebuild_campaign_state({}, [])
    assert pending == []
    assert resumed == []


def test_completed_records_are_skipped_on_resume():
    ledger = {"a": make_record("completed"), "b": make_record("completed")}
    pending, resumed = rebuild_campaign_state(ledger, [])
    assert pending == []
    assert resumed == []


def test_in_progress_record_is_resumed_not_requeued():
    ledger = {"a": make_record("in_progress"), "b": make_record("pending")}
    pending, resumed = rebuild_campaign_state(ledger, [])
    assert resumed == ["a"]
    assert pending == ["b"]


def test_explicitly_completed_keys_are_excluded_even_if_unrecorded():
    ledger = {"a": make_record("pending")}
    pending, resumed = rebuild_campaign_state(ledger, ["a"])
    assert pending == []
    assert resumed == []


def test_mixed_ledger_partitions_correctly():
    ledger = {
        "done": make_record("completed"),
        "active": make_record("in_progress", attempt=3),
        "queued": make_record("pending"),
    }
    pending, resumed = rebuild_campaign_state(ledger, [])
    assert sorted(pending) == ["queued"]
    assert resumed == ["active"]


def test_record_survives_json_round_trip():
    record = make_record("in_progress", attempt=2)
    encoded = json.dumps(record, sort_keys=True)
    decoded = json.loads(encoded)
    assert decoded["status"] == "in_progress"
    assert decoded["capture_attempts"] == 2