"""Contains imports of all models.

import or define all models here to ensure they are attached to the
Base.metadata prior to any initialization routines
"""

import logging
import os
import re
from abc import ABCMeta
from functools import partial
from urllib.parse import unquote, urlparse, urlunparse

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


def includeme(config):
    """Put default value based on environment in `sqlalchemy.url`.

    Precedence is as follows:
     1. PG_USER, PG_PASSWORD, PG_HOST, PG_PORT and PG_DBNAME from
     environmental variables (possible to overwrite just one variable)
     2. sqlalchemy.url set in *.ini
     3. Default values
    """
    log.info("Configuring database connection")
    settings = config.get_settings()

    # First set default URL
    db_url = urlparse("postgresql://postgres:@localhost:5432/test")

    # If URL is set in INI config, then replace default URL with URL from INI file
    if "sqlalchemy.url" in settings:
        db_url = urlparse(settings["sqlalchemy.url"])

    # If values are set in env-vars, overwrite these in db_url
    username = os.getenv("PG_USER", db_url.username)
    password = os.getenv("PG_PASSWORD", db_url.password)
    hostname = os.getenv("PG_HOST", db_url.hostname)
    port = os.getenv("PG_PORT", db_url.port)
    dbname = os.getenv("PG_DBNAME", db_url.path.replace("/", ""))
    db_url = urlparse(
        "".join(
            [
                "postgresql://",
                str(username),
                ":",
                str(password),
                "@",
                str(hostname),
                ":",
                str(port),
                "/",
                str(dbname),
            ]
        )
    )

    if len(db_url.path) <= 1:
        raise ValueError(
            (
                "SQLAlchemy url has no database specified, "
                "specify PG_DBNAME in settings"
            )
        )
    config.add_settings({"sqlalchemy.url": db_url.geturl()})

    def rfc_1738_quote(text):
        """Encode url following RFC 1798."""
        # RFC 1798: Within the user and password field, any ":", "@", or "/" must
        # be encoded.
        # (Also "%" must be encoded.) Adapted from SQLAlchemy
        return re.sub(r"[:@/%]", lambda m: "%%%X" % ord(m.group(0)), text)

    def make_netloc(host, port=None, username=None, password=None):
        """Make a netloc for URL."""
        if username:
            userinfo = rfc_1738_quote(username)
            if password is not None:
                userinfo += ":" + rfc_1738_quote(password)
            userinfo += "@"
        else:
            userinfo = ""

        if ":" in host:
            netloc = "[" + host + "]"  # IPv6 literal
        else:
            netloc = host
        if port:
            netloc += ":" + str(port)
        return userinfo + netloc

    def netloc_username(netloc):
        """Extract decoded username from `netloc`."""
        if "@" in netloc:
            userinfo = netloc.rsplit("@", 1)[0]
            if ":" in userinfo:
                userinfo = userinfo.split(":", 1)[0]
            return unquote(userinfo)
        return None

    def obfuscate_url_password(url):
        """Obfuscate password in URL for use in logging."""
        parts = urlparse(url)
        if parts.password:
            url = urlunparse(
                (
                    parts.scheme,
                    make_netloc(
                        parts.hostname, parts.port, netloc_username(parts.netloc), "***"
                    ),
                    parts.path,
                    parts.params,
                    parts.query,
                    parts.fragment,
                )
            )
        return url

    log.info(
        "SQLAlchemy url used is: %s",
        obfuscate_url_password(config.get_settings()["sqlalchemy.url"]),
    )

    # use pyramid_tm to hook the transaction lifecycle to the request
    config.include("pyramid_tm")

    # optionally pass a custom query class through settings
    if "query_cls" in settings:
        session_factory = get_session_factory(
            get_engine(settings), settings["query_cls"]
        )
    else:
        session_factory = get_session_factory(get_engine(settings))
    config.registry["session_factory"] = session_factory

    # make request.dbsession available for use in Pyramid
    config.add_request_method(
        # r.tm is the transaction manager used by pyramid_tm
        lambda r: get_tm_session(session_factory, r.tm),
        "session",
        reify=True,
    )


__all__ = [
    "Base",
    "get_engine",
    "get_session_factory",
    "get_tm_session",
    "metadata",
]
