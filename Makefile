SHELL := /bin/bash # Use bash syntax
ARG := $(word 2, $(MAKECMDGOALS) )

.DEFAULT_GOAL := help

.PHONY: setup
setup: ## Set up initial files
	test -f backend/.env || cp -v backend/.env.example backend/.env
	test -f backend/services/web/.env || cp -v backend/services/web/.env.example backend/services/web/.env
	test -f backend/brainwave/settings/local.py || cp -v backend/brainwave/settings/local.py.example backend/brainwave/settings/local.py


.PHONY: help
help: ## Show this help message
	@# https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


.PHONY: clean
clean: ## Remove all cached files
	@find . -name "*.pyc" -exec rm -rf {} \;
	@find . -name "__pycache__" -delete


.PHONY: test
test: ## Run tests
	poetry run pytest $(ARG)
	npm run test


# Commands for Docker version
.PHONY: docker_setup
docker_setup: ## Do initial Docker setup
	docker volume create brainwave_dbdata
	docker-compose build --no-cache backend
	docker-compose run frontend npm install

.PHONY: lint
lint: ## Perform linting
	npm run lint
	poetry run ruff check --fix
	poetry run ruff format

.PHONY: docker_test
docker_test: ## Run tests
	docker-compose run backend pytest $(ARG)
	docker-compose run frontend npm run test

.PHONY: docker_up
docker_up: ## Run the project containers
	docker-compose up -d

.PHONY: docker_update_dependencies
docker_update_dependencies: ## Rebuild containers and pick up new dependencies
	docker-compose down
	docker-compose up -d --build

.PHONY: docker_down
docker_down: ## Stop the project containers
	docker-compose down

.PHONY: docker_logs
docker_logs: ## View logs from the containers
	docker-compose logs -f $(ARG)

.PHONY: docker_makemigrations
docker_makemigrations: ## Create database migrations
	docker-compose run --rm backend python manage.py makemigrations

.PHONY: docker_migrate
docker_migrate: ## Apply database migrations
	docker-compose run --rm backend python manage.py migrate

.PHONY: docker_lint
docker_lint: ## Perform linting (using Docker)
	docker-compose run frontend npm run lint
	docker-compose run backend ruff check --fix
	docker-compose run backend ruff format

.PHONY: docker_frontend
docker_frontend: ## Access the bash shell for the frontend
	docker-compose run --rm frontend sh

.PHONY: docker_backend
docker_backend: ## Access the bash shell for the backend
	docker-compose run --rm backend bash

# Commands for pre-commit (both local and docker versions)
.PHONY: precommit_eslint precommit_eslint_docker
precommit_eslint:
	npm run lint
precommit_eslint_docker:
	docker-compose run -T frontend npm run lint

.PHONY: precommit_pyright precommit_pyright_docker
precommit_pyright:
	pyright
precommit_pyright_docker:
	docker-compose run -T backend pyright

.PHONY: precommit_missing_migrations precommit_missing_migrations_docker
precommit_missing_migrations:
	poetry run python backend/manage.py makemigrations --check
precommit_missing_migrations_docker:
	docker-compose run -T backend python manage.py makemigrations --check

.PHONY: precommit_update_neuron_docs precommit_update_neuron_docs_docker
precommit_update_neuron_docs: setup
	poetry run python backend/services/neurons/_mkdoc.py backend/services/neurons backend/services/neurons/README.md
precommit_update_neuron_docs_docker: setup
	docker-compose run -T backend python services/neurons/_mkdoc.py services/neurons services/neurons/README.md
