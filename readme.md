# Lahman Baseabll Database Loader [Functional, In-progress]

This repo contains code to load the [Lahman Baseball Database](https://sabr.org/lahman-database/), to a Postgres database. This
repo is provided as a supplement to walkthroughs and demos from baseball tutorials on the YouTube channel, [Build Whatever You Want](https://www.youtube.com/@BuildWhateverYouWant)


This tutorial series is undergoing refinement and improvement, so please excuse any errors.

# Quickstart

## Setup
```
git clone https://github.com/BuildWhateverYouWant/lahman_baseball_database_loader.git

cd lahman_baseball_database_loader

python -m venv .venv

source .venv/bin/activate

pip install -r dependencies/requirements.txt
```

## Download CSV data
This loader is designed to ingest CSV data for the Lahman Basebal Database into a PostgreSQL database. Download the
[CSV](https://sabr.app.box.com/s/y1prhc795jk8zvmelfd3jq7tl389y6cd) data. You will later reference this file when running the loader.

## Create config.yaml

Once here, copy the contents of `config.yaml.example` into a file called `config.yaml`, and update the values for your specific configuration. This file contains several fields:

- path_to_csvs: Specify the fully-qualified path for the file that contains the CSV data (example: `/path/to/lahman_1871-2025_csv`)
- username: The username for your Postgres user.
- password: The password for your Postgres user.
- host: The host for your Postgres database.
- port: The port for your Posgres database.
- database: The name of the database in which the baseball database tables will be created and the data will be inserted into.

## Run program

The program can be run like:

`python --path_to_config /path/to/config`
