"""All html pages should subclass View."""

import importlib
import os
from operator import itemgetter
from typing import List

from pyramid.decorator import reify
from typing_extensions import TypedDict

StaticRequirement = TypedDict(
    "StaticRequirement", {"name": str, "priority": int, "url": str}
)


class BaseView(object):
    """Base class for building views."""

    resource_path = os.path.join(os.path.dirname(__file__), "templates")
    """Link to resources for this view."""

    page_title = None
    project_name = "Project name"
    include_security = False
    signed_in = False

    css_requirements_general: List[StaticRequirement] = [
        {
            "name": "Bootstrap",
            "priority": 100,
            "url": "https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css",
        },  # noqa
        {
            "name": "Font Awesome",
            "priority": 101,
            "url": "https://use.fontawesome.com/releases/v5.8.1/css/all.css",
        },  # noqa
        {
            "name": "style",
            "priority": 102,
            "url": "pyramid_mod_baseview:css/style.css",
        },  # noqa
    ]
    """Add css dependencies that needs to be loaded on every view.

    Load order is made explicit by the priority tag, lowest number loads first.

    Priorities below <1000 are loaded in the header. Priorities >=1000 are
    loaded at the end of the html document

    Format as follows:

        {'name': 'A local file',
         'priority': 100,
         'url': 'package:some_file.css'},
        {'name': 'An external css dependency',
         'priority': 101,
         'url': 'https://some_external/file.css'},
    ]
    """

    js_requirements_general: List[StaticRequirement] = [
        {
            "name": "JQuery",
            "priority": 100,
            "url": "https://code.jquery.com/jquery-2.2.4.min.js",
        },
        {
            "name": "Bootstrap",
            "priority": 101,
            "url": "https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js",
        },  # noqa
    ]
    """Add css dependencies that needs to be loaded on every view.

    Use same format as css_requirements_general property
    """

    logo = ""
    """The logo that is in the template."""

    favicon = ""
    """The page favicon."""

    package_dependencies = ["pyramid_mod_baseview", "pyramid_mod_email"]

    def __init__(self, request):
        """Instantiate view."""
        self.request = request
        self.session = getattr(request, "session", None)
        self.user = getattr(request, "user", None)
        if self.user:
            self.signed_in = True
        self.css_requirements_specific: List[StaticRequirement] = []
        self.js_requirements_specific: List[StaticRequirement] = []

    def absolute(self, url):
        """Convert relative urls (defined as 'package:resource') to absolute.

        Absolute urls are left as is
        """
        if url.startswith(("https://", "http://", "//")):
            return url
        else:
            return self.request.static_url(url)

    @reify
    def css_requirements_header(self) -> List[StaticRequirement]:
        """Return the css dependencies of the view."""
        combined = self.css_requirements_general + self.css_requirements_specific
        items = [i for i in combined if i["priority"] < 1000]
        return sorted(items, key=itemgetter("priority"))

    @reify
    def js_requirements_header(self) -> List[StaticRequirement]:
        """Return the js dependencies of the view."""
        combined = self.js_requirements_general + self.js_requirements_specific
        items = [i for i in combined if i["priority"] < 1000]
        return sorted(items, key=itemgetter("priority"))

    @reify
    def css_requirements_footer(self) -> List[StaticRequirement]:
        """Return the css dependencies of the view."""
        combined = self.css_requirements_general + self.css_requirements_specific
        items = [i for i in combined if i["priority"] >= 1000]
        return sorted(items, key=itemgetter("priority"))

    @reify
    def js_requirements_footer(self) -> List[StaticRequirement]:
        """Return the js dependencies of the view."""
        combined = self.js_requirements_general + self.js_requirements_specific
        items = [i for i in combined if i["priority"] >= 1000]
        return sorted(items, key=itemgetter("priority"))

    def home(self):
        """Generate home page."""
        return {"user": self.user, "projectname": self.project_name}

    @reify
    def version_info(self):
        """Return version info of package dependencies."""

        def import_from(module, name):
            module = importlib.__import__(module, fromlist=[name])
            return getattr(module, name)

        version_info = []
        for d in self.package_dependencies:
            try:
                version = import_from(d, "__version__")
                version_info.append(f"{d}: {version}")
            except ImportError:
                version_info.append(f"{d}: Not installed")
            except AttributeError:
                version_info.append(f"{d}: Undefined")
        return version_info


class View(BaseView):
    """All html pages should subclass View."""

    pass
