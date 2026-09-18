"""discover-swiss-mcp — Swiss tourism data from the discover.swiss Infocenter Open.

The version is read from the installed distribution metadata, which is built
from ``pyproject.toml``. A value nobody has to remember to bump cannot drift
away from the packaged one — which is exactly how a User-Agent ends up
announcing a release that was never cut.
"""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _distribution_version

try:
    __version__ = _distribution_version("discover-swiss-mcp")
except PackageNotFoundError:
    # Running from a bare source tree without an install. Deliberately not a
    # plausible-looking number: an obviously non-release marker is better than
    # a wrong version in the User-Agent.
    __version__ = "0.0.0+source"

__all__ = ["__version__"]
