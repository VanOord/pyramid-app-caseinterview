"""Route configuration."""


def includeme(config):
    """Include in the config if this module is loaded."""
    config.add_static_view(name="static_deform", path="deform:static")
    config.add_static_view(
        name="static", path="pyramid_app_caseinterview:static", cache_max_age=3600
    )
    config.add_route("home", "/")
    config.add_route("timeseries", "/api/v1/timeseries")
    config.add_route("depthseries", "/api/v1/depthseries")
    config.add_route("activity", "/api/v1/activity")
