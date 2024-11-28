"""Initialize database.

Usage:
  {{cookiecutter.project_slug}}_initialize_db <inifile> [options]
  {{cookiecutter.project_slug}}_initialize_db --help

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
from {{cookiecutter.project_slug}} import get_config
from {{cookiecutter.project_slug}}.models import (
    Base,
    get_engine,
    get_session_factory,
    get_tm_session,
)
from pyramid_mod_accounts.models import Role, User, UserRole

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
    session_factory = get_session_factory(engine)

    if args["--drop-all"]:
        logger.warning("Dropping database schema!")
        Base.metadata.drop_all(engine)

    # create all tables
    Base.metadata.create_all(engine)

    # create admin role and user
    role_names = ["admin"]
    with transaction.manager:
        session = get_tm_session(session_factory, transaction.manager)
        user = session.query(User).limit(1).one_or_none()
        if not user:
            user = User(name="admin", email="admin@vanoord.com")
            user.password = "admin"
            session.add(user)
            session.flush()
            session.refresh(user)
            for role_name in role_names:
                role = Role()
                role.name = role_name
                role.created_by_user_id = user.id
                session.add(role)
                session.flush()
                session.refresh(role)
                userrole = UserRole()
                userrole.role_id = role.id
                userrole.user_id = user.id
                userrole.created_by_user_id = user.id
                session.add(userrole)

            logger.info("Adding alembic stamp...")
            alembic_cfg = Config(ALEMBIC_INI)
            command.stamp(alembic_cfg, "head")

    logger.info("Finished initializing database.")


if __name__ == "__main__":
    main()
