# REMEMBER Makefile

.PHONY: help build test lint clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Build the server container
	cd server && podman build -f Containerfile -t remember-server:latest . || buildah build -f Containerfile -t remember-server:latest .

build-docker: ## Build the server container with Docker
	cd server && docker build -f Dockerfile -t remember-server:latest .

test: ## Run tests
	cd server && pytest tests/ -v

lint: ## Run linters
	cd server && ruff check . && ruff format --check .

format: ## Format code
	cd server && ruff format .

clean: ## Clean build artifacts
	rm -rf server/dist server/build server/*.egg-info
	rm -rf .pytest_cache .ruff_cache

migrate: ## Run database migrations
	cd server && alembic upgrade head

run: ## Run the server locally
	cd server && python -m uvicorn remember.server:mcp.app --reload --host 0.0.0.0 --port 8000

helm-lint: ## Lint Helm chart
	helm lint helm/remember

helm-template: ## Template Helm chart
	helm template remember helm/remember

deploy: ## Deploy to Kubernetes
	helm upgrade --install remember helm/remember -f helm/remember/values.yaml

undeploy: ## Undeploy from Kubernetes
	helm uninstall remember
