"""Contains imports of all models.

import or define all models here to ensure they are attached to the
Base.metadata prior to any initialization routines
"""

import logging
from abc import ABCMeta
from functools import partial

import zope.sqlalchemy  # noqa
from sqlalchemy import engine_from_config
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import configure_mappers, sessionmaker
from sqlalchemy.schema import MetaData

log = logging.getLogger(__name__)

# run configure_mappers after defining all of the models to ensure
# all relationships can be setup
configure_mappers()


def get_engine(settings, prefix="sqlalchemy."):
    """Return a database session."""
    return engine_from_config(settings, prefix)


def get_session_factory(engine, query_cls=None):
    """Return a database session factory.

    Optionally pass a custom query class.
    """
    if query_cls:
        factory = sessionmaker(query_cls=query_cls)
    else:
        factory = sessionmaker()
    factory.configure(bind=engine)
    return factory


def get_tm_session(session_factory, transaction_manager):
    """Get a ``sqlalchemy.orm.Session`` instance backed by a transaction.

    This function will hook the session to the transaction manager which
    will take care of committing any changes.

    - When using pyramid_tm it will automatically be committed or aborted
      depending on whether an exception is raised.

    - When using scripts you should wrap the session in a manager yourself.
      For example::

          import transaction

          engine = get_engine(settings)
          session_factory = get_session_factory(engine)
          with transaction.manager:
              session = get_tm_session(session_factory, transaction.manager)

    """
    session = session_factory()
    zope.sqlalchemy.register(session, transaction_manager=transaction_manager)
    return session


NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class DeclarativeABCMeta(DeclarativeMeta, ABCMeta):
    """Intersection of DeclarativeMeta and ABCMeta."""

    pass


declarative_base_with_abc = partial(declarative_base, metaclass=DeclarativeABCMeta)

metadata = MetaData(naming_convention=NAMING_CONVENTION)
Base = declarative_base_with_abc(metadata=metadata)


__all__ = [
    "Base",
    "get_engine",
    "get_session_factory",
    "get_tm_session",
    "metadata",
]
