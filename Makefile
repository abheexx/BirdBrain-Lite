.PHONY: help dev dev-backend dev-frontend build test lint format clean docker-up docker-down

help: ## Show this help message
	@echo "BirdBrain Lite - Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

dev: ## Start both backend and frontend in development mode
	@echo "Starting BirdBrain Lite in development mode..."
	@echo "Backend will be available at http://localhost:8000"
	@echo "Frontend will be available at http://localhost:5173"
	@echo "API docs will be available at http://localhost:8000/docs"
	docker-compose up --build

dev-backend: ## Start only the backend in development mode
	@echo "Starting backend only..."
	cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Start only the frontend in development mode
	@echo "Starting frontend only..."
	cd frontend && npm run dev

build: ## Build both backend and frontend
	@echo "Building BirdBrain Lite..."
	@echo "Building backend..."
	cd backend && python -m pip install -r requirements.txt
	@echo "Building frontend..."
	cd frontend && npm ci && npm run build

test: ## Run all tests
	@echo "Running backend tests..."
	cd backend && python -m pytest tests/ -v
	@echo "Running frontend tests..."
	cd frontend && npm run lint

lint: ## Run linting for both backend and frontend
	@echo "Linting backend..."
	cd backend && python -m ruff check . && python -m mypy .
	@echo "Linting frontend..."
	cd frontend && npm run lint

format: ## Format code for both backend and frontend
	@echo "Formatting backend..."
	cd backend && python -m black . && python -m ruff check --fix .
	@echo "Formatting frontend..."
	cd frontend && npm run format

docker-up: ## Start the application with Docker Compose
	@echo "Starting BirdBrain Lite with Docker..."
	docker-compose up --build

docker-down: ## Stop the Docker Compose services
	@echo "Stopping BirdBrain Lite..."
	docker-compose down

clean: ## Clean up build artifacts and dependencies
	@echo "Cleaning up..."
	cd backend && rm -rf __pycache__ .pytest_cache .mypy_cache
	cd frontend && rm -rf node_modules dist .vite
	docker-compose down -v
