# Brainwave

## Running

### Tools

-   Setup [editorconfig](http://editorconfig.org/), [ruff](https://github.com/astral-sh/ruff) and [ESLint](http://eslint.org/) in the text editor you will use to develop.

### Setup

-   Do the following:
    -   Create a git-untracked `local.py` settings file:
        `cp backend/{{project_name}}/settings/local.py.example backend/{{project_name}}/settings/local.py`
    -   Create a git-untracked `.env.example` file:
        `cp backend/.env.example backend/.env`

### If you are using Docker:

-   Open the `backend/.env` file on a text editor and uncomment the line `DATABASE_URL=postgres://brainwave:password@db:5432/brainwave`
-   Open a new command line window and go to the project's directory
-   Run the initial setup:
    `make docker_setup`
-   Create the migrations for `users` app:  
    `make docker_makemigrations`
-   Run the migrations:
    `make docker_migrate`
-   Run the project:
    `make docker_up`
-   Access `http://localhost:8000` on your browser and the project should be running there
-   To access the logs for each service, run:
    `make docker_logs <service name>` (either `backend`, `frontend`, etc). Leave `<service name>` blank to access all logs
-   To stop the project, run:
    `make docker_down`

#### Adding new dependencies

-   Open a new command line window and go to the project's directory
-   Update the dependencies management files by performing any number of the following steps:
    -   To add a new **frontend** dependency, run `make docker_frontend` to open an interactive shell and then run `npm install <package name> --save` to add the dependency
        > The above command will update your `package.json`, but won't make the change effective inside the container yet
    -   To add a new **backend** dependency, run `make docker_backend` to open an interactive shell and then run `poetry add {dependency}` to add the dependency. If the dependency should be only available for development user append `-G dev` to the command.
        > The above command will update your `pyproject.toml`, but won't make the change effective inside the container yet
    -   After updating the desired file(s), run `make docker_update_dependencies` to update the containers with the new dependencies
        > The above command will stop and re-build the containers in order to make the new dependencies effective

### If you are not using Docker:

#### Setup and run the frontend app

-   Open a new command line window and go to the project's directory
-   `npm install`
-   `npm run dev`
    -   This is used to serve the frontend assets to be consumed by [django-webpack-loader](https://github.com/django-webpack/django-webpack-loader) and not to run the React application as usual, so don't worry if you try to check what's running on port 3000 and see an error on your browser

#### Setup the backend app

-   Open the `backend/.env` file on a text editor and uncomment the line `DATABASE_URL=sqlite:///backend/db.sqlite3`
-   Open a new command line window and go to the project's directory
-   Run `poetry install`

#### Run the backend app

-   Go to the `backend` directory
-   Create the migrations for `users` app:
    `poetry run python manage.py makemigrations`
-   Run the migrations:
    `poetry run python manage.py migrate`
-   Run the project:
    `poetry run python manage.py runserver`
-   Open a browser and go to `http://localhost:8000` to see the project running

#### Setup Celery

(This isn't needed for now)

-   `poetry run celery --app=myproject worker --loglevel=info`

### Testing

`make test` or `make docker_test` (depending on if you are using docker or not)

You may pass a path to the desired test module in the make command. E.g.:

`make test someapp.tests.test_views`

### Adding new pypi libs

To add a new **backend** dependency, run `poetry add {dependency}`. If the dependency should be only available for development user append `-G dev` to the command.

## Linting

-   At pre-commit time (see below)
-   Manually with `poetry run ruff` and `npm run lint` on project root.
-   During development with an editor compatible with ruff and ESLint.

## Pre-commit hooks

-   **If you are NOT using Docker**: On project root, run `poetry run pre-commit install` to enable the hook into your git repo.
-   **Using Docker?**
    -    You'll need to [install pre-commit](https://pre-commit.com/#install) yourself
    -    On project root, run `pre-commit install --config .pre-commit-config-docker.yaml` to enable the hook into your git repo.

The hook will run automatically for each commit.
