"""Set up testing as in this example.
http://docs.pylonsproject.org/projects/pyramid/en/latest/tutorials/wiki2/tests.html
"""

import re

from sqlalchemy import func
from sqlalchemy.orm.session import Session


class TestDatabase:
    def test_version(self, session_tm: Session) -> None:
        v = session_tm.query(func.version()).one()[0]
        assert re.match(r"PostgreSQL 1(3|4|5|6)\.", v)


class TestApp:
    def test_home(self, testapp) -> None:
        res = testapp.get("/", status=200)
        assert b"<h1>caseinterview</h1>" in res.body
