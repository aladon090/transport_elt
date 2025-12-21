.PHONY: help setup extract load dbt-run dbt-test test airflow-up airflow-down airflow-restart clean

help:
	@echo "Transport ELT Pipeline - Available Commands:"
	@echo ""
	@echo "  make setup           - Install Python dependencies"
	@echo "  make extract         - Run data extraction (CSV to Parquet)"
	@echo "  make load            - Load data to GCP (GCS + BigQuery)"
	@echo "  make dbt-run         - Run all dbt models"
	@echo "  make dbt-test        - Run dbt tests"
	@echo "  make test            - Run Python unit tests"
	@echo "  make airflow-up      - Start Airflow services"
	@echo "  make airflow-down    - Stop Airflow services"
	@echo "  make airflow-restart - Restart Airflow services"
	@echo "  make clean           - Clean temporary files and caches"
	@echo ""

setup:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt
	@echo "Setup complete!"

extract:
	@echo "Running data extraction..."
	python -m src.extract.extract_parquet

load:
	@echo "Loading data to GCP..."
	python -m src.load.load_to_gcp

dbt-run:
	@echo "Running dbt models..."
	cd dbt && dbt run --profiles-dir ../config/dbt

dbt-test:
	@echo "Running dbt tests..."
	cd dbt && dbt test --profiles-dir ../config/dbt

test:
	@echo "Running Python unit tests..."
	pytest tests/ -v --cov=src

airflow-up:
	@echo "Starting Airflow..."
	cd orchestration && \
	mkdir -p ./logs ./plugins ./config && \
	docker-compose up airflow-init && \
	docker-compose up -d
	@echo "Airflow is running at http://localhost:8080"
	@echo "Username: airflow | Password: airflow"

airflow-down:
	@echo "Stopping Airflow..."
	cd orchestration && docker-compose down

airflow-restart:
	@echo "Restarting Airflow..."
	cd orchestration && docker-compose restart

clean:
	@echo "Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "Clean complete!"
