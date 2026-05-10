from setuptools import Command
from setuptools import Extension
from setuptools import setup


class build_manpages(Command):
    description = "Generate manpages"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from wilderness import build_manpages

        from clevercsv.console import build_application

        build_manpages(build_application())


if __name__ == "__main__":
    setup(
        ext_modules=[
            Extension("clevercsv.cparser", sources=["src/cparser.c"]),
            Extension("clevercsv.cabstraction", sources=["src/abstraction.c"]),
        ],
        cmdclass={"build_manpages": build_manpages},
    )
