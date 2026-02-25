.PHONY: setup test demo lint docker-up docker-down clean

setup:
	uv venv .venv
	uv pip install -r requirements.txt

test:
	PYTHONPATH=. .venv/bin/python -m pytest tests/ -v

demo:
	PYTHONPATH=. .venv/bin/python -m services.rca.demo

lint:
	uv run ruff check services/ tests/

docker-up:
	docker compose -f infra/docker-compose.yml up -d

docker-down:
	docker compose -f infra/docker-compose.yml down

clean:
	rm -rf .venv __pycache__ services/__pycache__ tests/__pycache__
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
