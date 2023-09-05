# -*- coding: utf-8 -*-

from typing import Optional

def base_abstraction(
    data: str,
    delimiter: Optional[str],
    quotechar: Optional[str],
    escapechar: Optional[str],
) -> str: ...
def c_merge_with_quotechar(data: str) -> str: ...
