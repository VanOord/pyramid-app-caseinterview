"""Initialize database.

Usage:
  pyramid_app_caseinterview_initialize_db <inifile> [options]
  pyramid_app_caseinterview_initialize_db --help

Options:
  -h --help                 Show this screen.
  -o --options=LIST         Comma-separated list of key=value pairs overwriting default setting in initfile.
  --drop-all                Drop all databases first.

"""

import logging
import os

import transaction
from docopt import docopt
from pyramid.paster import get_appsettings, setup_logging

from alembic import command
from alembic.config import Config
from pyramid_app_caseinterview import get_config
from pyramid_app_caseinterview.models import Base, get_engine

logger = logging.getLogger(__name__)

ALEMBIC_INI = os.path.join(os.path.dirname(__file__), "..", "..", "alembic.ini")


def main(argv=None):
    """Initialize database."""
    args = docopt(__doc__, argv=argv)

    setup_logging(args["<inifile>"])
    settings = get_appsettings(args["<inifile>"])
    if args["--options"]:
        settings.update(
            {
                k.strip(): v.strip()
                for kv in args["--options"].split(",")
                for k, v in kv.split("=")
            }
        )
    config = get_config(settings=settings).get_settings()
    engine = get_engine(config)

    if args["--drop-all"]:
        logger.warning("Dropping database schema!")
        Base.metadata.drop_all(engine)

    # create all tables
    Base.metadata.create_all(engine)

    with transaction.manager:
        logger.info("Adding alembic stamp...")
        alembic_cfg = Config(ALEMBIC_INI)
        command.stamp(alembic_cfg, "head")

    logger.info("Finished initializing database.")


if __name__ == "__main__":
    main()
