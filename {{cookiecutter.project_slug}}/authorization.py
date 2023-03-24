"""Pyramid Authorization classes."""
from pyramid.authorization import ALL_PERMISSIONS, Allow, Authenticated

from pyramid_mod_accounts.config import MySecurityPolicy, RootFactory


class GlobalSecurityPolicy(MySecurityPolicy):
    """Define the effective principals."""

    def effective_principals(self, request):
        """Return a sequence representing the effective principals.
        Typically this is including the :term:`userid` and any groups belonged
        to by the current user, always including 'system' groups such
        as ``pyramid.security.Everyone`` and
        ``pyramid.security.Authenticated``.
        """
        principals = super().effective_principals(request)
        return principals


class GlobalRootFactory(RootFactory):
    """Define the ACL."""

    __acl__ = [
        (Allow, Authenticated, Authenticated),
        (Allow, "role:admin", ALL_PERMISSIONS),
    ]
