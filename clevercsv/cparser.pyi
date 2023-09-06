# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Final
from typing import Generic
from typing import Iterable
from typing import List
from typing import Literal
from typing import Optional
from typing import Tuple
from typing import TypeVar
from typing import overload

_T = TypeVar("_T")

class Parser(Generic[_T]):
    _return_quoted: Final[bool]

    @overload
    def __init__(
        self: Parser[List[Tuple[str, bool]]],
        delimiter: Optional[str] = "",
        quotechar: Optional[str] = "",
        escapechar: Optional[str] = "",
        field_limit: Optional[int] = 128 * 1024,
        strict: Optional[bool] = False,
        return_quoted: Literal[True] = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: Parser[List[str]],
        delimiter: Optional[str] = "",
        quotechar: Optional[str] = "",
        escapechar: Optional[str] = "",
        field_limit: Optional[int] = 128 * 1024,
        strict: Optional[bool] = False,
        return_quoted: Literal[False] = ...,
    ) -> None: ...
    @overload
    def __init__(
        self,
        data: Iterable[str],
        delimiter: Optional[str] = "",
        quotechar: Optional[str] = "",
        escapechar: Optional[str] = "",
        field_limit: Optional[int] = 128 * 1024,
        strict: Optional[bool] = False,
        return_quoted: bool = ...,
    ) -> None: ...
    def __iter__(self) -> "Parser": ...
    def __next__(self) -> _T: ...

class Error(Exception): ...
