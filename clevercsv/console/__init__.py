# -*- coding: utf-8 -*-

from .application import build_application


def main():
    app = build_application()
    return app.run()
