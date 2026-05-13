.PHONY: dev test lint type-check coverage list benchmark smoke install clean

install:
	pip install -e ".[dev]"
dev:
	sortui --algorithm bubble --size 60
test:
	pytest -q
lint:
	ruff check sortui tests
type-check:
	mypy sortui --ignore-missing-imports
coverage:
	pytest --cov=sortui --cov-report=html --cov-report=term-missing
list:
	sortui --list
benchmark:
	sortui --benchmark bubble insertion shellsort timsort quicksort heapsort radix_lsd counting --size 500 --seed 42
smoke:
	python3 scripts/validate-startup.py
	bash scripts/smoke-test.sh
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; true
	find . -name "*.pyc" -delete 2>/dev/null; true
