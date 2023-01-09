# -*- coding: utf-8 -*-

"""Code for dealing with optional dependencies

The functionality in this file is largely based on similar functionality in the 
Pandas library.

Author: G.J.J van den Burg
Copyright: 2020, The Alan Turing Institute
License: See LICENSE file.

"""

import importlib

from packaging.version import Version

# update this when changing setup.py
VERSIONS = {
    "tabview": "1.4",
    "pandas": "0.24.1",
    "faust-cchardet": "2.1.14",
    "wilderness": "0.1.5",
}


def import_optional_dependency(name, raise_on_missing=True):
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

    min_version = VERSIONS.get(name)
    if not min_version:
        return module
    version = getattr(module, "__version__", None)
    if version is None:
        return
    if Version(version) < Version(min_version):
        msg = (
            f"CleverCSV requires version '{min_version}' or newer for "
            "optional dependency '{name}'. Please update the package "
            "or install CleverCSV with all its optional dependencies "
            "using: pip install clevercsv[full]"
        )
        raise ImportError(msg)

    return module
