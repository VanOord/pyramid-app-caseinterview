"""All html pages should subclass View."""

from pyramid.decorator import reify

from pyramid_mod_huisstijl import BaseView


@reify
def menu(self):
    """Return menu dict.

    Menu can be made dynamic, e.g. depending on user view permissions
    """
    menu = [
        {"title": "Home", "href": self.request.route_url("home"), "icon": "fa fa-home"}
    ]

    if self.user and self.user.has_admin:
        menu.append(
            {
                "title": "User Management",
                "icon": "fa fa-users",
                "dropdown": [
                    {
                        "title": "User Overview",
                        "href": self.request.route_url(
                            "users",
                            ext="html",
                            _query={
                                "renderer": "datatable",
                                "options": "serverside-columnsearch",
                            },
                        ),
                        "icon": "fa fa-users",
                    },
                    {
                        "title": "Add User",
                        "href": self.request.route_url("user_create"),
                        "icon": "fa fa-user-plus",
                    },
                ],
            }
        )

    return menu


BaseView.project_name = "{{cookiecutter.project_title}}"
BaseView.include_security = True
BaseView.menu = menu


class View(BaseView):
    """All html pages should subclass View."""

    pass
