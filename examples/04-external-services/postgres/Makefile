.PHONY: up down build setup clean test

up:
	docker-compose up -d
	@echo "PostgreSQL is ready on port 5432"
	@echo "Connection: postgresql://duckalog:duckalog@localhost:5432/demo"

build:
	duckalog build catalog.yaml

setup:
	python setup.py

test:
	duckalog validate catalog.yaml
	@echo "Test query: SELECT COUNT(*) FROM pg_customers"

clean:
	docker-compose down -v
	rm -rf data/*.duckdb

down:
	docker-compose down
