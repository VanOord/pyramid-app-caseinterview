"""Helper functions for tests."""

from uuid import UUID

from webtest.app import TestApp
from webtest.response import TestResponse


def sign_in(testapp: TestApp, user: str, password: str) -> TestResponse:
    testapp.get("/sign_out").follow()
    res = testapp.get("/sign_in_local", status=200)
    f = res.forms["sign-in"]
    f.set("user_name", user)
    f.set("password", password)
    return f.submit("submit", status=302).follow()


def user_remove(testapp: TestApp, user_id: UUID) -> TestResponse:
    sign_in(testapp, "admin", "admin")
    res = testapp.get(f"/users/{user_id}/delete", status=200)
    f = res.forms["user-remove"]
    f.set("confirm", True)
    return f.submit("submit", status=200)
