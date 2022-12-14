import sqlite3
from pathlib import Path
import logging


class Database:
    def __init__(self, filename: Path, logger: logging.Logger) -> None:
        self.conn = sqlite3.connect(filename)
        self.cur = self.conn.cursor()

        self.logger = logger
        self.logger.info("Database initialized")

    def create_table(self, table_name: str) -> None:
        self.table_name = table_name
        self.cur.execute(
            f"CREATE TABLE IF NOT EXISTS {table_name} (datetime DATETIME PRIMARY KEY, cpu_load DECIMAL(3, 1))")
        self.logger.info(f"Table {table_name} created")
        self.conn.commit()

    def write_data(self, cpu_load: float) -> None:
        self.cur.execute(
            f"INSERT INTO {self.table_name} VALUES (datetime('now'), ?)", (cpu_load,))

        self.logger.debug(f"Written to database: {cpu_load}")
        self.conn.commit()
