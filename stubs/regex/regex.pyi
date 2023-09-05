from typing import Any

from regex._regex_core import VERSION0

def match(
    pattern,
    string,
    flags: int = ...,
    pos: Any | None = ...,
    endpos: Any | None = ...,
    partial: bool = ...,
    concurrent: Any | None = ...,
    timeout: Any | None = ...,
    ignore_unused: bool = ...,
    **kwargs
): ...
def fullmatch(
    pattern,
    string,
    flags: int = ...,
    pos: Any | None = ...,
    endpos: Any | None = ...,
    partial: bool = ...,
    concurrent: Any | None = ...,
    timeout: Any | None = ...,
    ignore_unused: bool = ...,
    **kwargs
): ...
def search(
    pattern,
    string,
    flags: int = ...,
    pos: Any | None = ...,
    endpos: Any | None = ...,
    partial: bool = ...,
    concurrent: Any | None = ...,
    timeout: Any | None = ...,
    ignore_unused: bool = ...,
    **kwargs
): ...
def sub(
    pattern,
    repl,
    string,
    count: int = ...,
    flags: int = ...,
    pos: Any | None = ...,
    endpos: Any | None = ...,
    concurrent: Any | None = ...,
    timeout: Any | None = ...,
    ignore_unused: bool = ...,
    **kwargs
): ...
def subf(
    pattern,
    format,
    string,
    count: int = ...,
    flags: int = ...,
    pos: Any | None = ...,
    endpos: Any | None = ...,
    concurrent: Any | None = ...,
    timeout: Any | None = ...,
    ignore_unused: bool = ...,
    **kwargs
): ...
def subn(
    pattern,
    repl,
    string,
    count: int = ...,
    flags: int = ...,
    pos: Any | None = ...,
    endpos: Any | None = ...,
    concurrent: Any | None = ...,
    timeout: Any | None = ...,
    ignore_unused: bool = ...,
    **kwargs
): ...
def subfn(
    pattern,
    format,
    string,
    count: int = ...,
    flags: int = ...,
    pos: Any | None = ...,
    endpos: Any | None = ...,
    concurrent: Any | None = ...,
    timeout: Any | None = ...,
    ignore_unused: bool = ...,
    **kwargs
): ...
def split(
    pattern,
    string,
    maxsplit: int = ...,
    flags: int = ...,
    concurrent: Any | None = ...,
    timeout: Any | None = ...,
    ignore_unused: bool = ...,
    **kwargs
): ...
def splititer(
    pattern,
    string,
    maxsplit: int = ...,
    flags: int = ...,
    concurrent: Any | None = ...,
    timeout: Any | None = ...,
    ignore_unused: bool = ...,
    **kwargs
): ...
def findall(
    pattern,
    string,
    flags: int = ...,
    pos: Any | None = ...,
    endpos: Any | None = ...,
    overlapped: bool = ...,
    concurrent: Any | None = ...,
    timeout: Any | None = ...,
    ignore_unused: bool = ...,
    **kwargs
): ...
def finditer(
    pattern,
    string,
    flags: int = ...,
    pos: Any | None = ...,
    endpos: Any | None = ...,
    overlapped: bool = ...,
    partial: bool = ...,
    concurrent: Any | None = ...,
    timeout: Any | None = ...,
    ignore_unused: bool = ...,
    **kwargs
): ...
def compile(
    pattern, flags: int = ..., ignore_unused: bool = ..., **kwargs
): ...
def purge() -> None: ...
def cache_all(value: bool = ...): ...
def template(pattern, flags: int = ...): ...
def escape(pattern, special_only: bool = ..., literal_spaces: bool = ...): ...

DEFAULT_VERSION = VERSION0
Pattern: Any
Match: Any
Regex = compile

# Names in __all__ with no definition:
#   A
#   ASCII
#   B
#   BESTMATCH
#   D
#   DEBUG
#   DOTALL
#   E
#   ENHANCEMATCH
#   F
#   FULLCASE
#   I
#   IGNORECASE
#   L
#   LOCALE
#   M
#   MULTILINE
#   P
#   POSIX
#   R
#   REVERSE
#   S
#   Scanner
#   T
#   TEMPLATE
#   U
#   UNICODE
#   V0
#   V1
#   VERBOSE
#   VERSION0
#   VERSION1
#   W
#   WORD
#   X
#   __doc__
#   __version__
#   error
