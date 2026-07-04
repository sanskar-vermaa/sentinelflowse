from sentinelflow_worker.jobs.alerts import process_alert_batch


def run_worker() -> None:
    print("SentinelFlow worker booted")
    process_alert_batch(batch_id="local-dev")

