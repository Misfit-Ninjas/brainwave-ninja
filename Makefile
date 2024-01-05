SHELL := /bin/bash # Use bash syntax
ARG := $(word 2, $(MAKECMDGOALS) )

.DEFAULT_GOAL := help

.PHONY: setup
setup: ## Set up initial files
	cp -v --update=none backend/.env.example backend/.env
	cp -v --update=none backend/brainwave/settings/local.py.example backend/brainwave/settings/local.py


.PHONY: help
help: ## Show this help message
	@# https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


.PHONY: clean
clean: ## Remove all cached files
	@find . -name "*.pyc" -exec rm -rf {} \;
	@find . -name "__pycache__" -delete


.PHONY: test
test: ## Run tests (keeping the database)
	poetry run backend/manage.py test backend/ $(ARG) --parallel --keepdb

.PHONY: test_reset
test_reset: ## Run tests (but reset the database)
	poetry run backend/manage.py test backend/ $(ARG) --parallel

# Commands for Docker version
.PHONY: docker_setup
docker_setup: ## Do initial Docker setup
	docker volume create brainwave_dbdata
	docker-compose build --no-cache backend
	docker-compose run frontend npm install

.PHONY: lint
lint: ## Perform linting (using Docker)
	npm run lint
	poetry run ruff check --fix
	poetry run ruff format

.PHONY: docker_test
docker_test: ## Run tests (keeping the database)
	docker-compose run backend python manage.py test $(ARG) --parallel --keepdb

.PHONY: docker_test_reset
docker_test_reset: ## Run tests (but reset the database)
	docker-compose run backend python manage.py test $(ARG) --parallel

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
