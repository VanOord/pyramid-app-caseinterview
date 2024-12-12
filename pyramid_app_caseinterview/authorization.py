"""Pyramid Authorization classes."""

from pyramid.authorization import ACLHelper, Allow, Authenticated, Everyone


class GlobalSecurityPolicy:
    """Define the effective principals."""

    def __init__(self, **kwargs):
        self.acl = ACLHelper()

    def effective_principals(self):
        return set([Everyone])

    def permits(self, request, context, permission):
        principals = self.effective_principals()
        return self.acl.permits(context, principals, permission)

    def authenticated_userid(self, request):
        return "id"


class GlobalRootFactory(object):
    """Define the ACL."""

    __name__ = None
    __parent__ = None

    # the default Access Control List is very limited. This is expected to be
    # extended in the scope of the application that is used.
    __base_acl__ = [
        (Allow, Authenticated, Authenticated),
    ]

    __extra_acl__: list[tuple] = []  # This can be defined by the app.

    def __acl__(self):
        all_acls = [*self.__base_acl__, *self.__extra_acl__]
        merged_acl = {entry[1]: entry for entry in all_acls}
        return list(merged_acl.values())

    def __init__(self, request):
        """Instantiate root factory."""
        self.request = request
