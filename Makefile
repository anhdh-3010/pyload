.PHONY: run run-api run-outbox-publisher run-worker run-scheduler

run:
	uv run uvicorn main:app --reload --host localhost --port 8000

run-api:
	uv run python -m services.api.main

run-outbox-publisher:
	uv run python -m services.outbox_publisher.main

run-worker:
	uv run python -m services.worker.main

run-scheduler:
	uv run python -m services.scheduler.main
