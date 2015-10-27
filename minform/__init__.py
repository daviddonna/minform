# -*- coding: utf-8 -*-
# flake8: noqa

__author__ = 'David Donna'
__email__ = 'davidadonna@gmail.com'
__version__ = '0.1.0'

from .core import *
from .basic import *
from .compound import *

# This stanza is a hack to make Sphinx document the constants cleanly as
# direct members of the minform package.
FIXED = FIXED  #:
AUTOMATIC = AUTOMATIC  #:
EXPLICIT = EXPLICIT  #:
NATIVE = NATIVE  #:
LITTLE_ENDIAN = LITTLE_ENDIAN  #:
BIG_ENDIAN = BIG_ENDIAN  #:
NETWORK = NETWORK  #:
