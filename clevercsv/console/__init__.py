# -*- coding: utf-8 -*-

from .application import build_application


def main() -> int:
    app = build_application()
    return app.run()
