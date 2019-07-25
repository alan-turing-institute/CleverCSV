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


def wait_for_enter():
    input(
        colorama.Style.DIM
        + "\nPress Enter to continue"
        + colorama.Style.RESET_ALL
    )
    print()


class Step:
    def pre(self):
        pass

    def post(self):
        wait_for_enter()

    def run(self):
        try:
            self.pre()
            self.action()
            self.post()
        except KeyboardInterrupt:
            print(colorama.Fore.RED + "\nInterrupted." + 
                    colorama.Style.RESET_ALL)
            raise SystemExit(1)

    def instruct(self, msg):
        print(colorama.Fore.GREEN + msg + colorama.Style.RESET_ALL)

    def print_run(self, msg):
        print(
            colorama.Fore.CYAN
            + colorama.Style.BRIGHT
            + "Run:"
            + colorama.Style.RESET_ALL
        )
        self.print_cmd(msg)

    def print_cmd(self, msg):
        print(
            colorama.Fore.CYAN
            + colorama.Style.BRIGHT
            + "\t"
            + msg
            + colorama.Style.RESET_ALL
        )


class GitToMaster(Step):
    def action(self):
        self.print_run("git checkout master")


class UpdateChangelog(Step):
    def action(self):
        self.print_run("vi CHANGELOG.md")


class RunTests(Step):
    def action(self):
        self.print_run("make test")


class BumpVersionPoetry(Step):
    def action(self):
        self.instruct("Bump poetry version (<version> = patch/minor/major)")
        self.print_run("poetry version <version>")


class BumpVersionPackage(Step):
    def action(self):
        self.instruct("Update package version")
        self.print_run("vi clevercsv/__version__.py")


class MakeClean(Step):
    def action(self):
        self.print_run("make clean")


class MakeDocs(Step):
    def action(self):
        self.print_run("make docs")


class MakeDist(Step):
    def action(self):
        self.print_run("make dist")


class PushToTestPyPI(Step):
    def action(self):
        self.print_run(
            "twine upload --repository-url https://test.pypi.org/legacy/ dist/*"
        )


class InstallFromTestPyPI(Step):
    def action(self):
        self.print_run("cd /tmp/")
        self.print_cmd("rm -rf ./venv")
        self.print_cmd("virtualenv ./venv")
        self.print_cmd("cd ./venv")
        self.print_cmd("source bin/activate")
        self.print_cmd(
            "pip install --index-url https://test.pypi.org/simple/ "
            + "--extra-index-url https://pypi.org/simple clevercsv"
        )


class TestCleverCSV(Step):
    def action(self):
        self.print_run("clevercsv help")


class DeactivateVenv(Step):
    def action(self):
        self.print_run("deactivate")
        self.print_cmd("cd /path/to/clevercsv")


class GitTagVersion(Step):
    def action(self):
        self.print_run("git tag <version>")


class GitAdd(Step):
    def action(self):
        self.instruct("Add everything to git")
        self.print_run("git gui")


class PushToPyPI(Step):
    def action(self):
        self.print_run("twine upload dist/*")


class PushToGitHub(Step):
    def action(self):
        self.print_run("git push -u --tags origin master")


class WaitForTravis(Step):
    def action(self):
        self.instruct(
            "Wait for Travis to complete and verify that its successful"
        )


class WaitForRTD(Step):
    def action(self):
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
    for step in procedure:
        step.run()


if __name__ == "__main__":
    main()
