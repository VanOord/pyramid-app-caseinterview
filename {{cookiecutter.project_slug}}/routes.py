"""Route configuration."""


def includeme(config):
    """Include in the config if this module is loaded."""
    config.add_static_view(name="static_deform", path="deform:static")
    config.add_static_view(
        name="static", path="{{cookiecutter.project_slug}}:static", cache_max_age=3600
    )
    config.add_route("home", "/")
