import logging
import sqlite3
import click

from db import db

logger = logging.getLogger(__name__)


@click.group()
def database():
    """Database utilities"""
    pass


@click.command
@click.pass_context
def start_db(ctx):
    logger.info("Starting database...")
    try:
        _DB = db.Database()
    except sqlite3.OperationalError as e:
        logger.error("Database error: %s", e)
    except sqlite3.Error as e:
        logger.error("SQLite error: %s", e)
    click.secho("Database started successfully", fg="green")
