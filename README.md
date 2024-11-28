[ ![docs](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://vanoord.github.io/pyramid-app-voice/docs/) [ ![coverage](https://github.com/VanOord/pyramid-app-voice/blob/gh-pages/coverage/coverage.svg)](https://vanoord.github.io/pyramid-app-voice/coverage/) [![CICD - ACR - Python](https://github.com/VanOord/pyramid-app-caseinterview/actions/workflows/action.yml/badge.svg)](https://github.com/VanOord/pyramid-app-caseinterview/actions/workflows/action.yml)



# caseinterview
A pyramid app for case interview

# Installation and running caseinterview

## Installation instructions:

Make sure you have python>3.5.1 and git installed, so they are available from the command line. 

```bash
# clone code from git
git clone https://github.com/VanOord/pyramid-app-caseinterview.git
cd pyramid-app-caseinterview

# upgrade pip
pip install -U pip
pip install -U setuptools

# install requirements
pip install -r requirements.txt

# install this package
pip install -e .
```

Note that, for development, it is advised to manually checkout and install the requirements listed in `requirements-git.txt`.

## Database connection

Keep \*.ini files under version control, but **do not store passwords in version control**. Therefore the parameters for the database connection should be defined as environmental variables.

Precedence of the defined parameters for database access is as follows:

1.  sqlalchemy.url set in \*.ini (use this form: `sqlalchemy.url = postgresql://user:password@host:port/dbname`)
2.  `PG_USER`, `PG_PASSWORD`, `PG_HOST`, `PG_PORT` and `PG_DBNAME` set in \*.ini
3.  `PG_USER`, `PG_PASSWORD`, `PG_HOST`, `PG_PORT` and `PG_DBNAME` environmental variables
4.  Default values

(Temporarily) set correct database settings in \*.ini or environmental variables. When using the \*.ini file, make sure **not to commit this file to GitHub**.

The default settings and how to set them as environmental variables are listed below. This differs for windows and linux.

### Linux / OSX

```bash
export PG_PASSWORD=
export PG_USER=postgres
export PG_HOST=localhost
export PG_PORT=5432
export PG_DBNAME=test
```

Add variables to `/etc/environment` to persist them, see [here](https://help.ubuntu.com/community/EnvironmentVariables)

### Windows

```bat
SET PG_PASSWORD=
SET PG_USER=postgres
SET PG_HOST=localhost
SET PG_PORT=5432
SET PG_DBNAME=test
```

Use `SETX` instead to persist the variables, see [here](http://stackoverflow.com/questions/5898131/set-a-persistent-environment-variable-from-cmd-exe)

```bat
SETX PG_PASSWORD
SETX PG_USER postgres
SETX PG_HOST localhost
SETX PG_PORT 5432
SETX PG_DBNAME test
```

Optionally initialize the email SMTP settings:

```bat
SET EMAIL_SMTP_URL=smtp.office365.com:587
SET EMAIL_SMTP_USER=openearth@vanoord.com
SET EMAIL_SMTP_PASSWORD=
```

Again, use `SETX` instead to persist the variables

## Initialize database

When the application is installed (with `pip install ...`), several executable-scripts are made
available on your PATH. This might require a reload of the command prompt / shell environment.
These scripts are made available as executables (.exe on Windows) rather than as python scripts,
so you can run them from anywhere without starting a python instance yourselves (in Anaconda3\Scripts\ on Windows).
With these executable-scripts, the database can be initialised as follows:

    pyramid_app_caseinterview_initialize_db development.ini

Serve with

    pserve development.ini

or for debugging

    pserve development.ini --reload

Browse to `http://localhost:6543`

## Testing

Set environmental variables if necessary (see above) and run

```bash
pytest
```

# run pyramid_app_caseinterview app in containers

Make sure you have docker and docker-compose installed.

Build the image:

```bash
docker build -t pyramid_app_caseinterview .
```

Create and run the docker-compose.yml file:

```bash
docker-compose up
```

Start a terminal inside the application container:

```bash
docker exec -it pyramid_app_caseinterview_app /bin/bash
```

Install the environment:

```bash
pip install -e .
```

Initialize and synchronize the database:

```bash
pyramid_app_caseinterview_initialize_db development-docker.ini
```

Run the application:

```bash
pserve development-docker.ini --reload
```
