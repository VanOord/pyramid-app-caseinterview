"""Sel value API"""

from pyramid.view import view_config

from pyramid_app_caseinterview.models import Depthseries, Timeseries

from . import View


class API(View):
    """API endpoints"""

    @view_config(
        route_name="timeseries",
        permission="read",
        renderer="json",
        request_method="GET",
    )
    def timeseries_api(self):
        query = self.session.query(Timeseries)
        return [
            {
                "id": str(q.id),
                "datetime": q.datetime,
                "value": q.value,
            }
            for q in query.all()
        ]

    @view_config(
        route_name="depthseries",
        permission="read",
        renderer="json",
        request_method="GET",
    )
    def depthseries_api(self):
        query = self.session.query(Depthseries)
        return [
            {
                "id": str(q.id),
                "depth": q.depth,
                "value": q.value,
            }
            for q in query.all()
        ]
