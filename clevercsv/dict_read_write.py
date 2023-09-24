# -*- coding: utf-8 -*-

"""
DictReader and DictWriter.

This code is entirely copied from the Python csv module. The only exception is
that it uses the `reader` and `writer` classes from our package.

Author: Gertjan van den Burg

"""

from __future__ import annotations

import warnings

from collections import OrderedDict
from collections.abc import Collection

from typing import TYPE_CHECKING
from typing import Any
from typing import Generic
from typing import Iterable
from typing import Iterator
from typing import Literal
from typing import Mapping
from typing import Optional
from typing import Sequence
from typing import TypeVar
from typing import Union
from typing import cast

from clevercsv.read import reader
from clevercsv.write import writer

if TYPE_CHECKING:
    from clevercsv._types import SupportsWrite
    from clevercsv._types import _DialectLike
    from clevercsv._types import _DictReadMapping

_T = TypeVar("_T")


class DictReader(
    Generic[_T], Iterator["_DictReadMapping[Union[_T, Any], Union[str, Any]]"]
):
    def __init__(
        self,
        f: Iterable[str],
        fieldnames: Optional[Sequence[_T]] = None,
        restkey: Optional[str] = None,
        restval: Optional[str] = None,
        dialect: "_DialectLike" = "excel",
        *args: Any,
        **kwds: Any,
    ) -> None:
        self._fieldnames = fieldnames
        self.restkey = restkey
        self.restval = restval
        self.reader: reader = reader(f, dialect, *args, **kwds)
        self.dialect = dialect
        self.line_num = 0

    def __iter__(self) -> "DictReader[_T]":
        return self

    @property
    def fieldnames(self) -> Sequence[_T]:
        if self._fieldnames is None:
            try:
                fieldnames = next(self.reader)
                self._fieldnames = [cast(_T, f) for f in fieldnames]
            except StopIteration:
                pass

        assert self._fieldnames is not None

        # Note: this was added because I don't think it's expected that Python
        # simply drops information if there are duplicate headers. There is
        # discussion on this issue in the Python bug tracker here:
        # https://bugs.python.org/issue17537 (see linked thread therein). A
        # warning is easy enough to suppress and should ensure that the user
        # is at least aware of this behavior.
        if not len(self._fieldnames) == len(set(self._fieldnames)):
            warnings.warn(
                "fieldnames are not unique, some columns will be dropped."
            )

        self.line_num = self.reader.line_num
        return self._fieldnames

    @fieldnames.setter
    def fieldnames(self, value: Sequence[_T]) -> None:
        self._fieldnames = value

    def __next__(self) -> "_DictReadMapping[Union[_T, Any], Union[str, Any]]":
        if self.line_num == 0:
            self.fieldnames
        row = next(self.reader)
        self.line_num = self.reader.line_num

        while row == []:
            row = next(self.reader)

        d: _DictReadMapping = OrderedDict(zip(self.fieldnames, row))
        lf = len(self.fieldnames)
        lr = len(row)
        if lf < lr:
            d[self.restkey] = row[lf:]
        elif lf > lr:
            for key in self.fieldnames[lr:]:
                d[key] = self.restval
        return d


class DictWriter(Generic[_T]):
    def __init__(
        self,
        f: SupportsWrite[str],
        fieldnames: Collection[_T],
        restval: Optional[Any] = "",
        extrasaction: Literal["raise", "ignore"] = "raise",
        dialect: "_DialectLike" = "excel",
        *args: Any,
        **kwds: Any,
    ):
        self.fieldnames = fieldnames
        self.restval = restval
        if extrasaction.lower() not in ("raise", "ignore"):
            raise ValueError(
                "extrasaction (%s) must be 'raise' or 'ignore'" % extrasaction
            )
        self.extrasaction = extrasaction
        self.writer = writer(f, dialect, *args, **kwds)

    def writeheader(self) -> Any:
        header = dict(zip(self.fieldnames, self.fieldnames))
        return self.writerow(header)

    def _dict_to_list(self, rowdict: Mapping[_T, Any]) -> Iterator[Any]:
        if self.extrasaction == "raise":
            wrong_fields = rowdict.keys() - self.fieldnames
            if wrong_fields:
                raise ValueError(
                    "dict contains fields not in fieldnames: "
                    + ", ".join([repr(x) for x in wrong_fields])
                )
        return (rowdict.get(key, self.restval) for key in self.fieldnames)

    def writerow(self, rowdict: Mapping[_T, Any]) -> Any:
        return self.writer.writerow(self._dict_to_list(rowdict))

    def writerows(self, rowdicts: Iterable[Mapping[_T, Any]]) -> None:
        return self.writer.writerows(map(self._dict_to_list, rowdicts))
