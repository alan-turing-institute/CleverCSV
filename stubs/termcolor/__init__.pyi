from typing import Any

__ALL__: Any
VERSION: Any
ATTRIBUTES: Any
HIGHLIGHTS: Any
COLORS: Any
RESET: str

def colored(
    text,
    color: Any | None = ...,
    on_color: Any | None = ...,
    attrs: Any | None = ...,
): ...
def cprint(
    text,
    color: Any | None = ...,
    on_color: Any | None = ...,
    attrs: Any | None = ...,
    **kwargs
) -> None: ...
