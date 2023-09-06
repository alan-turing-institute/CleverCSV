# -*- coding: utf-8 -*-

"""Code for dealing with optional dependencies

The functionality in this file is largely based on similar functionality in the 
Pandas library.

Author: G.J.J van den Burg
Copyright: 2020, The Alan Turing Institute
License: See LICENSE file.

"""

import importlib

from types import ModuleType

from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional

from packaging.version import Version


class OptionalDependency(NamedTuple):
    import_name: str
    package_name: str
    min_version: str


# update this when changing setup.py
OPTIONAL_DEPENDENCIES: List[OptionalDependency] = [
    OptionalDependency("tabview", "tabview", "1.4"),
    OptionalDependency("pandas", "pandas", "0.24.1"),
    OptionalDependency("cchardet", "faust-cchardet", "2.1.18"),
    OptionalDependency("wilderness", "wilderness", "0.1.5"),
]


def import_optional_dependency(
    name: str, raise_on_missing: bool = True
) -> Optional[ModuleType]:
    """
    Import an optional dependency.

    This function is modelled on a similar function in the Pandas library.

    Parameters
    ----------
    name : str
        Name of the module to import

    raise_on_missing : bool
        Whether to raise an error when the package is missing or to simply
        return None.

    Returns
    -------
    module : module
        The module if importing was successful, None if
        :attr:`raise_on_missing` is False.

    Raises
    ------
    ImportError
        When a module can't be imported and :attr:`raise_on_missing` is True.

    """
    msg = (
        f"\nOptional dependency '{name}' is missing. You can install it using "
        "pip or conda, or you can install CleverCSV with all of its optional "
        "dependencies by running: pip install clevercsv[full]"
    )
    try:
        module = importlib.import_module(name)
    except ImportError:
        if raise_on_missing:
            raise ImportError(msg) from None
        else:
            return None

    opt_dependencies: Dict[str, OptionalDependency] = {
        d.import_name: d for d in OPTIONAL_DEPENDENCIES
    }

    dependency = opt_dependencies.get(name)
    if dependency is None:
        raise ImportError(f"No known optional dependency with name: {name}")

    version = getattr(module, "__version__", None)
    if version is None:
        return module

    if Version(version) < Version(dependency.min_version):
        msg = (
            f"CleverCSV requires version '{dependency.min_version}' or newer "
            f"for optional dependency '{dependency.package_name}'. Please "
            "update the package or install CleverCSV with all its optional "
            "dependencies using: pip install clevercsv[full]"
        )
        raise ImportError(msg)

    return module
