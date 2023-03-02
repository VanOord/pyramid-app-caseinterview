"""Set up testing as in this example.
http://docs.pylonsproject.org/projects/pyramid/en/latest/tutorials/wiki2/tests.html
"""
import re

from sqlalchemy import func
from sqlalchemy.orm.session import Session


class TestDatabase:
    def test_version(self, session_tm: Session) -> None:
        v = session_tm.query(func.version()).one()[0]
        assert re.match(r"PostgreSQL 1(0|1|2|3|4)\.", v)


class TestApp:
    def test_home(self, testapp) -> None:
        res = testapp.get("/", status=200)
        assert b"<h1>{{cookiecutter.project_title}}</h1>" in res.body
        res = testapp.get("/users/create", status=302).follow()

    def test_home_admin(self, testapp, as_admin) -> None:
        res = testapp.get("/", status=200)
        assert b"User Management" in res.body
        res = testapp.get("/users/create", status=200)
