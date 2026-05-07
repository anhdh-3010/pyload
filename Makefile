.PHONY: run

run:
	uv run uvicorn main:app --reload --host localhost --port 8000
