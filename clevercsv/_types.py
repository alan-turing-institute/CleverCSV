# -*- coding: utf-8 -*-

from __future__ import annotations

import csv
import os
import sys

from typing import TYPE_CHECKING
from typing import Any
from typing import Mapping
from typing import Type
from typing import TypeVar
from typing import Union

from clevercsv.dialect import SimpleDialect

AnyPath = Union[str, bytes, "os.PathLike[str]", "os.PathLike[bytes]"]
StrPath = Union[str, "os.PathLike[str]"]
_OpenFile = Union[AnyPath, int]
_DictRow = Mapping[str, Any]
_DialectLike = Union[str, csv.Dialect, Type[csv.Dialect], SimpleDialect]
_T = TypeVar("_T")

if sys.version_info >= (3, 8):
    from typing import Dict as _DictReadMapping
else:
    from collections import OrderedDict as _DictReadMapping


if TYPE_CHECKING:
    from _typeshed import FileDescriptorOrPath  # NOQA
    from _typeshed import SupportsIter  # NOQA
    from _typeshed import SupportsWrite  # NOQA

    __all__ = [
        "SupportsWrite",
        "SupportsIter",
        "FileDescriptorOrPath",
        "AnyPath",
        "_OpenFile",
        "_DictRow",
        "_DialectLike",
        "_DictReadMapping",
    ]
else:
    __all__ = [
        "AnyPath",
        "_OpenFile",
        "_DictRow",
        "_DialectLike",
        "_DictReadMapping",
    ]
