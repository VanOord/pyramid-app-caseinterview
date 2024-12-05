"""Contains imports of all models.

import or define all models here to ensure they are attached to the
Base.metadata prior to any initialization routines
"""

from sqlalchemy.orm import configure_mappers

from pyramid_app_caseinterview.models.activity import Activity
from pyramid_app_caseinterview.models.depthseries import Depthseries
from pyramid_app_caseinterview.models.timeseries import Timeseries
from pyramid_mod_accounts import Role, User, UserRole
from pyramid_mod_basemodel import (
    Base,
    get_engine,
    get_session_factory,
    get_tm_session,
    metadata,
)

# run configure_mappers after defining all of the models to ensure
# all relationships can be setup
configure_mappers()

__all__ = [
    "Base",
    "get_engine",
    "get_session_factory",
    "get_tm_session",
    "metadata",
    "Role",
    "User",
    "UserRole",
    "Timeseries",
    "Depthseries",
    "Activity",
]
