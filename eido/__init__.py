"""
Project configuration
"""

from ._version import __version__
from .const import *
from .eido import *

__all__ = ["validate_project", "validate_sample"]

logmuse.init_logger(PKG_NAME)
