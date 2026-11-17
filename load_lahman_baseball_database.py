import argparse
import csv
import logging
import os
import psycopg2
import yaml

logging_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=logging_format, handlers=[logging.StreamHandler()])

logger = logging.getLogger(__name__)

MAX_BATCH_SIZE: int = 5000

def generate_create_table_statement(
    table_name: str,
    columns: list[str]
) -> str:
    # List comprehension.
    # Enclosing column names in quotes for columns such as the doubles column (2B).
    column_definitions: list[str] = [f"\t\t\"{column_name.strip()}\" VARCHAR" for column_name in columns]

    column_sql: str = ",\n".join(column_definitions)
    sql: str = f"""
    CREATE TABLE "{table_name}" (
        "uuid" VARCHAR PRIMARY KEY,
{column_sql}
    )"""
    return sql


def cleanse_input(value: str):
    return value.strip().replace("'", "''")


def generate_tuple(row: str):
    values: list[str] = row.split(",")
    values_for_insert: List[str] = ["\n\t\tUUIDV7()"]
    for value in values:
        if value is None or len(value.strip()) == 0:
            values_for_insert.append("\t\tNULL")
        else:
            values_for_insert.append(f"\t\t'{cleanse_input(value)}'")
    sql: str = ",\n".join(values_for_insert)
    return f"""\n\t({sql}\n\t)"""


def insert_batch_for_table(config: dict, table_name: str, columns: list[str], batch: list[str]):
    columns_sql: str = ",\n".join([f'\t\t"{column_name.strip()}"' for column_name in columns])
    values_sql: str = ",".join(batch)
    sql: str = f"""
    INSERT INTO "{table_name}" (
        "uuid",
{columns_sql}
    ) VALUES {values_sql}"""
    logger.info(f"Inserting {len(batch)} records into {table_name}...")
    apply_sql(config, sql)


def apply_sql(config: dict, sql: str):
    connection = None
    cursor = None
    try:
        connection = psycopg2.connect(config["pg_conn_url"])
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()
    except (Exception, psycopg2.Error) as exception:
        logging.info(f"Error connecting to the database: {exception}")
        raise exception
    finally:
        if connection:
            cursor.close()
            connection.close()
            logging.info("Database connection closed.")


def process_csv(config: dict, path_to_csv: str):
    with open(path_to_csv, newline="") as csvfile:
        try:
            file_name: str = path_to_csv.split("/")[-1]
            table_name: str = file_name.split(".")[0]
            header: str = csvfile.readline()
            columns: list[str] = header.split(",")
            create_table_sql: str = generate_create_table_statement(table_name, columns)
            apply_sql(config, create_table_sql)
        except Exception as exception:
            logger.error(exception)
            raise exception
        batch: list[str] = []
        for line in csvfile:
            tuple: str = generate_tuple(line)
            batch.append(tuple)
            if len(batch) == MAX_BATCH_SIZE:
                insert_batch_for_table(config, table_name, columns, batch)
                batch.clear()
        insert_batch_for_table(config, table_name, columns, batch)


def parse_yaml(path_to_yaml: str) -> dict:
    with open(path_to_yaml) as yamlfile:
        return yaml.safe_load(yamlfile)


def is_empty(value: str) -> bool:
    # If value is cast to int.
    if value is None or len(str(value).strip()) == 0:
        return True
    return False


def validate_key(key_name: str, config: dict):
    if key_name not in config:
        raise Exception(f"Database {key_name} is required.")

    if is_empty(config[key_name]):
        raise Exception(f"Database {key_name} cannot be empty.")


def validate_config(config: dict):
    if "path_to_csvs" not in config:
        raise Exception("path_to_csvs is required in config. Download Lahman Baseball Database CSVs from https://sabr.org/lahman-database/ and try again.")

    validate_key("username", config)
    validate_key("password", config)
    validate_key("host", config)
    validate_key("database", config)
    validate_key("port", config)


def main():
    parser = argparse.ArgumentParser(
        description="Lahman Baseball Database Ingestion Tool"
    )

    parser.add_argument(
        "--path_to_config",
        help="Path to the configuration file for Lahman database ingestion.",
        required=True
    )

    args: dict = parser.parse_args()

    path_to_yaml: str = args.path_to_config

    config: dict = parse_yaml(path_to_yaml)

    validate_config(config)

    config["pg_conn_url"] = f'postgresql://{config["username"]}:{config["password"]}@{config["host"]}:{config["port"]}/{config["database"]}'

    contents = os.listdir(config["path_to_csvs"])

    for item in contents:
        if not item.endswith(".csv"):
            continue
        path_to_csv: str = f'{config["path_to_csvs"]}/{item}'
        process_csv(config, path_to_csv)


if __name__ == "__main__":
    main()




