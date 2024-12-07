#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Do-nothing script for making a release

This idea comes from here: 
https://blog.danslimmon.com/2019/07/15/do-nothing-scripting-the-key-to-gradual-automation/

Author: Gertjan van den Burg
Date: 2019-07-23

"""

import abc
import os
import re
import subprocess
import sys
import tempfile
import webbrowser

from pathlib import Path

from typing import Optional

import colorama

URLS = {
    "RTD": "https://readthedocs.org/projects/clevercsv/builds/",
    "CI": "https://github.com/alan-turing-institute/CleverCSV/actions",
    "dummy": "https://github.com/alan-turing-institute/CleverCSV-pre-commit",
    "tags": "https://github.com/alan-turing-institute/CleverCSV/tags",
}
BRANCH_NAME = "master"
CHANGELOG_FILENAME = "CHANGELOG.md"
MAN_DIRECTORY = "./man"
PACKAGE_NICE_NAME = "CleverCSV"


def color_text(
    msg: str,
    color: Optional[str] = None,
    style: Optional[str] = None,
) -> str:
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


def color_print(msg, color=None, style=None):
    print(color_text(msg, color=color, style=style))


def wait_for_enter():
    input(color_text("\nPress Enter to continue", style="dim"))
    print()


def get_package_name():
    with open("./setup.py", "r") as fp:
        nameline = next(
            (line.strip() for line in fp if line.startswith("NAME = ")), None
        )
        return nameline.split("=")[-1].strip().strip('"')


def get_package_version(pkgname):
    ctx = {}
    with open(f"{pkgname.lower()}/__version__.py", "r") as fp:
        exec(fp.read(), ctx)
    return ctx["__version__"]


def get_last_version_tag():
    output = ""
    with subprocess.Popen(
        "git tag -l", shell=True, stdout=subprocess.PIPE, text=True, bufsize=1
    ) as p:
        for line in p.stdout:
            output += line
    tags = output.rstrip().split()
    version_tags = [
        t for t in tags if re.match(r"v\d+\.\d+\.\d+$", t) is not None
    ]
    versions = [v.lstrip(".") for v in version_tags]
    versions.sort()
    return versions[-1]


def get_last_release_candidate_tag(version: str):
    output = ""
    with subprocess.Popen(
        "git tag -l", shell=True, stdout=subprocess.PIPE, text=True, bufsize=1
    ) as p:
        for line in p.stdout:
            output += line
    tags = output.rstrip().split()
    version_tags = [
        t
        for t in tags
        if re.match(r"v" + version + r"-rc\.\d+", t) is not None
    ]
    versions = [v.lstrip(".") for v in version_tags]
    versions.sort()
    if not versions:
        return None
    return versions[-1]


def build_release_message(context, commit: bool = False) -> str:
    prefix = "bump: " if commit else ""
    message = (
        f"{prefix}{context['pkgname'].capitalize()} Release "
        f"{context['next_version']}"
    )
    message += "\n"
    message += "\n"
    message += context["changelog_update"]
    return message


class Step(metaclass=abc.ABCMeta):
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
            color_print("\nInterrupted.", color="red")
            raise SystemExit(1)

    def instruct(self, msg):
        color_print(msg, color="green")

    def print_command(self, msg):
        color_print("Run:", color="cyan", style="bright")
        color_print("\t" + msg, color="cyan", style="bright")

    def system(self, cmd: str):
        os.system(cmd)

    def execute(
        self, cmd: str, silent: bool = False, confirm: bool = True
    ) -> str:
        if not silent:
            color_print(f"Running: {cmd}", color="magenta", style="bright")
        if confirm:
            wait_for_enter()
        stdout = ""
        with subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            text=True,
            bufsize=1,
        ) as p:
            for line in p.stdout:
                stdout += line
                if not silent:
                    print(line, end="")
        if p.returncode:
            print("--- begin stdout ---")
            print(stdout)
            print("--- end stdout ---")
            raise subprocess.CalledProcessError(
                p.returncode, p.args, stdout, p.stderr
            )
        return stdout.rstrip()

    @abc.abstractmethod
    def action(self, context):
        """Action to perform for the step"""


class GitToMaster(Step):
    def action(self, context):
        self.instruct(f"Ensuring that you're on the {BRANCH_NAME} branch")
        branch = self.execute(
            "git rev-parse --abbrev-ref HEAD", silent=True, confirm=False
        )
        if not branch == BRANCH_NAME:
            print(f"ERROR: not on {BRANCH_NAME} branch.", file=sys.stderr)
            raise SystemExit(1)

    def post(self, context):
        print("")


class UpdateChangelog(Step):
    def action(self, context):
        self.instruct(f"Update change log for version {context['version']}")
        self.print_run("vi CHANGELOG.md")


class UpdateReadme(Step):
    def action(self, context):
        self.instruct("Update readme if necessary")
        self.print_command("vi README.md")


class RunTests(Step):
    def action(self, context):
        self.instruct("Running the unit tests")
        self.execute("make test")


class BumpVersionPackage(Step):
    def action(self, context):
        self.instruct("Update __version__.py with new version")
        self.system(f"vi {context['pkgname']}/__version__.py")

    def post(self, context):
        wait_for_enter()
        context["next_version"] = get_package_version(context["pkgname"])


class MakeClean(Step):
    def action(self, context):
        self.execute("make clean")


class MakeDocs(Step):
    def action(self, context):
        self.execute("make docs")


class MakeMan(Step):
    def action(self, context):
        self.execute("make man")


class InstallFromTestPyPI(Step):
    def action(self, context):
        tmpvenv = tempfile.mkdtemp(prefix="ccsv_venv_")
        parent = str(Path(tmpvenv).parent)
        self.execute(
            f"cd {parent} && python -m venv {tmpvenv} && source {tmpvenv}"
            "/bin/activate && pip install --no-cache-dir --index-url "
            "https://test.pypi.org/simple/ --extra-index-url "
            f"https://pypi.org/simple {context['pkgname']}=="
            f"{context['next_version']}"
        )
        context["tmpvenv"] = tmpvenv


class TestPackage(Step):
    def action(self, context):
        self.instruct(
            f"Ensuring that the package has version {context['next_version']}"
        )
        version = self.execute(
            f"source {context['tmpvenv']}/bin/activate && veld -V",
            silent=True,
            confirm=False,
        )
        if not version == context["next_version"]:
            print(
                "ERROR: version installed from TestPyPI doesn't match "
                "expected version."
            )

    def post(self, context):
        print("")


class RemoveVenv(Step):
    def action(self, context):
        self.execute(
            f"rm -rf {context['tmpvenv']}", confirm=False, silent=True
        )

    def post(self, context):
        print("")


class GitTagVersion(Step):
    def action(self, context):
        tag_message = build_release_message(context, commit=False)
        with open("./tag_message.tmp", "w") as fileobj:
            fileobj.write(tag_message)
        self.instruct("Going to tag with the following message:")
        print("--- BEGIN TAG MESSAGE ---")
        print(tag_message)
        print("--- END TAG MESSAGE ---")
        self.execute(
            f"git tag -F ./tag_message.tmp v{context['next_version']}"
        )
        os.unlink("./tag_message.tmp")


class GitTagPreRelease(Step):
    def action(self, context):
        last_rc_tag = get_last_release_candidate_tag(context["next_version"])
        rc_count = (
            1 if last_rc_tag is None else int(last_rc_tag.split(".")[-1]) + 1
        )
        context["rc_count"] = rc_count
        self.instruct("Tagging version as a pre-release")
        self.execute(
            f'git tag -m "{PACKAGE_NICE_NAME} Release v'
            f"{context['next_version']} (release candidate {rc_count})\" v"
            f"{context['next_version']}-rc.{rc_count}"
        )


class GitAdd(Step):
    def action(self, context):
        self.instruct("Commit any final changes for release to git")
        self.print_command("git gui")


class GitAddVersionAndMan(Step):
    def action(self, context):
        self.instruct("Add version and man pages to git and commit")
        self.execute(
            f"git add {context['pkgname']}/__version__.py", confirm=False
        )
        self.execute(f"git add {MAN_DIRECTORY}", confirm=False)
        # TODO: Fail gracefully if `git diff --cached --exit-code` is 0
        self.execute("git commit -m 'bump: update version and manpages'")


class GitAddRelease(Step):
    def action(self, context):
        self.instruct("Add Changelog & Readme to git")
        self.execute("git add CHANGELOG.md", confirm=False)
        self.execute("git add README.md", confirm=False)
        self.instruct("Going to commit with the following message:")

        commit_message = build_release_message(context, commit=True)
        print("--- BEGIN COMMIT MESSAGE ---")
        print(commit_message)
        print("--- END COMMIT MESSAGE ---")
        with open("./commit_message.tmp", "w") as fileobj:
            fileobj.write(commit_message)
        self.execute("git commit --file ./commit_message.tmp")
        os.unlink("./commit_message.tmp")


class PushToGitHub(Step):
    def action(self, context):
        self.execute(f"git push -u --tags origin {BRANCH_NAME}")


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


class GitHubRelease(Step):
    def action(self, context):
        webbrowser.open(URLS["tags"])
        self.instruct("Create release from tag and embed release notes")


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
        ("clean1", MakeClean()),
        ("docs1", MakeDocs()),
        ("man1", MakeMan()),
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
        ("man2", MakeMan()),
        ("install", InstallFromTestPyPI()),
        ("testpkg", TestPackage()),
        ("remove_venv", RemoveVenv()),
        ("addrelease", GitAddRelease()),
        ("tagfinal", GitTagVersion()),
        # triggers Travis to build with cibw and push to PyPI
        ("push3", PushToGitHub()),
        ("ci3", WaitForCI()),
        ("gh_release", GitHubRelease()),
        ("pre-commit", UpdatePreCommitDummy()),
    ]
    context = {}
    context["pkgname"] = get_package_name()
    context["prev_version_tag"] = get_last_version_tag()
    context["next_version"] = get_package_version(context["pkgname"])
    skip = True if target else False
    for name, step in procedure:
        if not name == target and skip:
            continue
        skip = False
        step.run(context)
    color_print("\nDone!", color="yellow", style="bright")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    main(target=target)
