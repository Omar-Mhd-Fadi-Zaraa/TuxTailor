import click
import logging

from cli.commands.database import start_db

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)-8s %(name)s: %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S",
)

logger = logging.getLogger(__name__)


@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging")
@click.pass_context
def cli(ctx, verbose):
    """TuxTailor backend CLI"""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    if ctx.obj["verbose"]:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled.")
    pass


cli.add_command(start_db)
