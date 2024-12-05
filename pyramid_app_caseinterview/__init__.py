"""Return a Pyramid WSGI application."""

import os

import pkg_resources
from pyramid.config import Configurator
from pyramid.events import NewRequest
from pyramid.settings import asbool

from .authorization import GlobalRootFactory, GlobalSecurityPolicy

__version__ = pkg_resources.get_distribution(__name__).version

CORS_ENABLED = asbool(os.getenv("CORS_ENABLED", False))


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
    config.include("pyramid_mod_basemodel")
    config.include("pyramid_mod_huisstijl")
    config.include("pyramid_mod_accounts")
    config.include("pyramid_mod_dataframe")

    settings = config.get_settings()
    security_policy = GlobalSecurityPolicy(
        settings["auth.secret"],
        hashalg="sha512",
        path=settings["cookie.path"],
        max_age=settings["auth.max_age"],
    )
    config.set_security_policy(security_policy)

    config.include(".routes")

    config.scan()
    return config


def main(global_config, **settings):
    """Return a Pyramid WSGI application."""
    config = get_config(settings=settings)

    return config.make_wsgi_app()
