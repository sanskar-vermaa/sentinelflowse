from sentinelflow_worker.jobs.alerts import process_alert_batch


def test_process_alert_batch_returns_empty_result_for_new_batch() -> None:
    result = process_alert_batch(batch_id="batch-1")

    assert result.batch_id == "batch-1"
    assert result.processed == 0
    assert result.grouped == 0
    assert result.failed == 0

