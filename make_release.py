#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Do-nothing script for making a release

This idea comes from here: 
https://blog.danslimmon.com/2019/07/15/do-nothing-scripting-the-key-to-gradual-automation/

Author: Gertjan van den Burg
Date: 2019-07-23

"""

import os
import sys
import tempfile
import webbrowser

import colorama

URLS = {
    "RTD": "https://readthedocs.org/projects/clevercsv/builds/",
    "CI": "https://github.com/alan-turing-institute/CleverCSV/actions",
    "dummy": "https://github.com/alan-turing-institute/CleverCSV-pre-commit",
}


def colored(msg, color=None, style=None):
    colors = {
        "red": colorama.Fore.RED,
        "green": colorama.Fore.GREEN,
        "cyan": colorama.Fore.CYAN,
        "yellow": colorama.Fore.YELLOW,
        "magenta": colorama.Fore.MAGENTA,
        None: "",
    }
    styles = {
        "bright": colorama.Style.BRIGHT,
        "dim": colorama.Style.DIM,
        None: "",
    }
    pre = colors[color] + styles[style]
    post = colorama.Style.RESET_ALL
    return f"{pre}{msg}{post}"


def cprint(msg, color=None, style=None):
    print(colored(msg, color=color, style=style))


def wait_for_enter():
    input(colored("\nPress Enter to continue", style="dim"))
    print()


def get_package_name():
    with open("./setup.py", "r") as fp:
        nameline = next(
            (l.strip() for l in fp if l.startswith("NAME = ")), None
        )
        return nameline.split("=")[-1].strip().strip('"')


def get_package_version(pkgname):
    ctx = {}
    with open(f"{pkgname.lower()}/__version__.py", "r") as fp:
        exec(fp.read(), ctx)
    return ctx["__version__"]


class Step:
    def pre(self, context):
        pass

    def post(self, context):
        wait_for_enter()

    def run(self, context):
        try:
            self.pre(context)
            self.action(context)
            self.post(context)
        except KeyboardInterrupt:
            cprint("\nInterrupted.", color="red")
            raise SystemExit(1)

    def instruct(self, msg):
        cprint(msg, color="green")

    def print_run(self, msg):
        cprint("Run:", color="cyan", style="bright")
        self.print_cmd(msg)

    def print_cmd(self, msg):
        cprint("\t" + msg, color="cyan", style="bright")

    def do_cmd(self, cmd):
        cprint(f"Going to run: {cmd}", color="magenta", style="bright")
        wait_for_enter()
        os.system(cmd)


class GitToMaster(Step):
    def action(self, context):
        self.instruct("Make sure you're on master and changes are merged in")
        self.print_run("git checkout master")


class UpdateChangelog(Step):
    def action(self, context):
        self.instruct(f"Update change log for version {context['version']}")
        self.print_run("vi CHANGELOG.md")


class UpdateReadme(Step):
    def action(self, context):
        self.instruct("Update readme if necessary")
        self.print_run("vi README.md")


class RunTests(Step):
    def action(self, context):
        self.do_cmd("make test")


class BumpVersionPackage(Step):
    def action(self, context):
        self.instruct("Update __version__.py with new version")
        self.do_cmd(f"vi {context['pkgname']}/__version__.py")

    def post(self, context):
        wait_for_enter()
        context["version"] = self._get_version(context)

    def _get_version(self, context):
        # Get the version from the version file
        return get_package_version(context["pkgname"])


class MakeClean(Step):
    def action(self, context):
        self.do_cmd("make clean")


class MakeDocs(Step):
    def action(self, context):
        self.do_cmd("make docs")


class InstallFromTestPyPI(Step):
    def action(self, context):
        tmpvenv = tempfile.mkdtemp(prefix="p2r_venv_")
        self.do_cmd(
            f"python -m venv {tmpvenv} && source {tmpvenv}/bin/activate && "
            "pip install --no-cache-dir --index-url "
            "https://test.pypi.org/simple/ "
            "--extra-index-url https://pypi.org/simple "
            f"{context['pkgname']}[full]=={context['version']}"
        )
        context["tmpvenv"] = tmpvenv


class TestPackage(Step):
    def action(self, context):
        self.instruct(
            f"Ensure that the following command gives version {context['version']}"
        )
        self.do_cmd(
            f"source {context['tmpvenv']}/bin/activate && {context['pkgname']} -V"
        )


class RemoveVenv(Step):
    def action(self, context):
        self.do_cmd(f"rm -rf {context['tmpvenv']}")


class GitTagVersion(Step):
    def action(self, context):
        self.do_cmd(f"git tag v{context['version']}")


class GitTagPreRelease(Step):
    def action(self, context):
        self.instruct("Tag version as a pre-release (increment as needed)")
        self.print_run(f"git tag v{context['version']}-rc.1")


class GitAdd(Step):
    def action(self, context):
        self.instruct("Add everything to git and commit")
        self.print_run("git gui")


class GitAddRelease(Step):
    def action(self, context):
        self.instruct("Add Changelog & Readme to git")
        self.instruct(
            f"Commit with title: {context['pkgname']} Release {context['version']}"
        )
        self.instruct("Embed changelog in body commit message")
        self.print_run("git gui")


class PushToPyPI(Step):
    def action(self, context):
        self.do_cmd("twine upload dist/*")


class PushToGitHub(Step):
    def action(self, context):
        self.do_cmd("git push -u --tags origin master")


class WaitForCI(Step):
    def action(self, context):
        webbrowser.open(URLS["CI"])
        self.instruct("Wait for CI to complete and verify that its successful")


class WaitForRTD(Step):
    def action(self, context):
        webbrowser.open(URLS["RTD"])
        self.instruct(
            "Wait for ReadTheDocs to complete and verify that its successful"
        )


class UpdatePreCommitDummy(Step):
    def action(self, context):
        self.instruct(
            f"Update the pre-commit dummy package ({URLS['dummy']}) "
            "by running ``make release`` there"
        )


def main(target=None):
    colorama.init()
    procedure = [
        ("gittomaster", GitToMaster()),
        ("gitadd1", GitAdd()),
        ("clean1", MakeClean()),
        ("docs1", MakeDocs()),
        ("runtests", RunTests()),
        # trigger CI to run tests on all platforms
        ("push1", PushToGitHub()),
        ("ci1", WaitForCI()),
        ("waitrtd", WaitForRTD()),
        ("bumpversion", BumpVersionPackage()),
        ("gitadd2", GitAdd()),
        ("gittagpre", GitTagPreRelease()),
        # trigger CI to run tests using cibuildwheel
        ("push2", PushToGitHub()),
        ("ci2", WaitForCI()),
        ("changelog", UpdateChangelog()),
        ("readme", UpdateReadme()),
        ("clean2", MakeClean()),
        ("docs2", MakeDocs()),
        ("install", InstallFromTestPyPI()),
        ("testpkg", TestPackage()),
        ("remove_venv", RemoveVenv()),
        ("addrelease", GitAddRelease()),
        ("tagfinal", GitTagVersion()),
        # triggers Travis to build with cibw and push to PyPI
        ("push3", PushToGitHub()),
        ("ci3", WaitForCI()),
        ("pre-commit", UpdatePreCommitDummy()),
    ]
    context = {}
    context["pkgname"] = get_package_name()
    context["version"] = get_package_version(context["pkgname"])
    skip = True if target else False
    for name, step in procedure:
        if not name == target and skip:
            continue
        skip = False
        step.run(context)
    cprint("\nDone!", color="yellow", style="bright")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    main(target=target)
