"""Return a Pyramid WSGI application."""

import logging
import os
import re
from urllib.parse import unquote, urlparse, urlunparse

import pkg_resources
import zope.sqlalchemy  # noqa
from pyramid.config import Configurator
from pyramid.events import NewRequest
from pyramid.settings import asbool

from pyramid_app_caseinterview.models import (
    get_engine,
    get_session_factory,
    get_tm_session,
)

from .authorization import GlobalRootFactory, GlobalSecurityPolicy

__version__ = pkg_resources.get_distribution(__name__).version

CORS_ENABLED = asbool(os.getenv("CORS_ENABLED", False))

log = logging.getLogger(__name__)


def add_cors_headers_response_callback(event):
    """Handle CORS headers errors."""

    def cors_headers(request, response):
        response.headers.update(
            {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*",
            }
        )

    event.request.add_response_callback(cors_headers)


def get_config(settings=None):
    """Return the app configuration."""
    settings = {} if settings is None else settings
    config = Configurator(settings=settings)

    if CORS_ENABLED:
        config.add_subscriber(add_cors_headers_response_callback, NewRequest)

    config.set_root_factory(GlobalRootFactory)

    config.include("pypugjs.ext.pyramid")

    def include_default_values():
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
                            parts.hostname,
                            parts.port,
                            netloc_username(parts.netloc),
                            "***",
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

    include_default_values()

    settings = config.get_settings()
    security_policy = GlobalSecurityPolicy()
    config.set_security_policy(security_policy)

    config.include(".routes")

    config.scan()
    return config


def main(global_config, **settings):
    """Return a Pyramid WSGI application."""
    config = get_config(settings=settings)

    return config.make_wsgi_app()
