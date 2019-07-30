#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Do-nothing script for making a release

This idea comes from here: 
https://blog.danslimmon.com/2019/07/15/do-nothing-scripting-the-key-to-gradual-automation/

Author: Gertjan van den Burg
Date: 2019-07-23

"""

import colorama
import os


def colored(msg, color=None, style=None):
    colors = {
        "red": colorama.Fore.RED,
        "green": colorama.Fore.GREEN,
        "cyan": colorama.Fore.CYAN,
        "yellow": colorama.Fore.YELLOW,
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
        cprint(f"Going to run: {cmd}", color="cyan", style="bright")
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


class RunTests(Step):
    def action(self, context):
        self.do_cmd("make test")


class BumpVersionPoetry(Step):
    def action(self, context):
        self.instruct("Bump poetry version (<version> = patch/minor/major)")
        self.print_run("poetry version <version>")

    def post(self, context):
        wait_for_enter()
        context["version"] = self._get_version()

    def _get_version(self):
        # Get the version from pyproject.toml
        with open("./pyproject.toml", "r") as fp:
            versionline = next(
                (l.strip() for l in fp if l.startswith("version")), None
            )
        version = versionline.split("=")[-1].strip().strip('"')
        return version


class BumpVersionPackage(Step):
    def action(self, context):
        self.instruct(
            f"Update __version__.py with version: {context['version']}"
        )
        self.print_run("vi clevercsv/__version__.py")


class MakeClean(Step):
    def action(self, context):
        self.do_cmd("make clean")


class MakeDocs(Step):
    def action(self, context):
        self.do_cmd("make docs")


class MakeDist(Step):
    def action(self, context):
        self.do_cmd("make dist")


class PushToTestPyPI(Step):
    def action(self, context):
        self.do_cmd(
            "twine upload --repository-url https://test.pypi.org/legacy/ dist/*"
        )


class InstallFromTestPyPI(Step):
    def action(self, context):
        self.print_run("cd /tmp/")
        self.print_cmd("rm -rf ./venv")
        self.print_cmd("virtualenv ./venv")
        self.print_cmd("cd ./venv")
        self.print_cmd("source bin/activate")
        self.print_cmd(
            "pip install --index-url https://test.pypi.org/simple/ "
            + f"--extra-index-url https://pypi.org/simple clevercsv=={context['version']}"
        )


class TestCleverCSV(Step):
    def action(self, context):
        self.instruct(
            f"Ensure that the following command gives version {context['version']}"
        )
        self.print_run("clevercsv -V")


class DeactivateVenv(Step):
    def action(self, context):
        self.print_run("deactivate")
        self.print_cmd("cd /path/to/clevercsv")


class GitTagVersion(Step):
    def action(self, context):
        self.print_run(f"git tag v{context['version']}")


class GitAdd(Step):
    def action(self, context):
        self.instruct("Add everything to git")
        self.print_run("git gui")


class PushToPyPI(Step):
    def action(self, context):
        self.do_cmd("twine upload dist/*")


class PushToGitHub(Step):
    def action(self, context):
        self.print_run("git push -u --tags origin master")


class WaitForTravis(Step):
    def action(self, context):
        self.instruct(
            "Wait for Travis to complete and verify that its successful"
        )


class WaitForRTD(Step):
    def action(self, context):
        self.instruct(
            "Wait for ReadTheDocs to complete and verify that its successful"
        )


def main():
    colorama.init()
    procedure = [
        GitToMaster(),
        GitAdd(),
        PushToGitHub(),
        WaitForTravis(),
        WaitForRTD(),
        BumpVersionPoetry(),
        BumpVersionPackage(),
        UpdateChangelog(),
        MakeClean(),
        RunTests(),
        MakeDocs(),
        MakeDist(),
        PushToTestPyPI(),
        InstallFromTestPyPI(),
        TestCleverCSV(),
        DeactivateVenv(),
        GitAdd(),
        PushToPyPI(),
        GitTagVersion(),
        PushToGitHub(),
    ]
    context = {}
    for step in procedure:
        step.run(context)
    cprint("\nDone!", color="yellow", style="bright")


if __name__ == "__main__":
    main()
