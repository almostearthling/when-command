#!/usr/bin/env python
# build html documentation using Sphinx (https://www.sphinx-doc.org/)

import os
import sys

import shutil
import subprocess


# set to True if the README.md file has to be added to the documentation
COPY_README = False



# utilities
def _write_stderr(msg, ty):
    cmd = os.path.basename(sys.argv[0])
    if cmd.endswith(".py"):
        cmd = cmd[:-3]
    elif cmd.endswith(".pyw") or cmd.endswith(".exe"):
        cmd = cmd[:-4]
    s = f"{cmd} {ty}: {msg}\n"
    sys.stderr.write(s)

def write_error(msg):
    _write_stderr(msg, "error")

def write_warning(msg):
    _write_stderr(msg, "warning")

def write_info(msg):
    _write_stderr(msg, "info")

def exit_error(msg, code=2):
    _write_stderr(msg, "fatal error")
    sys.exit(code)

def buildpath(*args):
    return os.path.normpath(os.path.join(*args))



# command-line utilities that are needed to build documentation
REQUIRED_COMMANDS = [
    "sphinx-build",
]

def check_requirements():
    for cmd in REQUIRED_COMMANDS:
        if not shutil.which(cmd):
            return False
    return True



# paths
THIS_PATH = os.path.dirname(sys.argv[0])
BASE_PATH = buildpath(THIS_PATH, "..")
SOURCE_PATH = buildpath(BASE_PATH, "support/docs")
DEST_PATH = buildpath(BASE_PATH, "_scratch/docs")



# convert the README.md file to index.md in the source directory
def copy_readme():
    try:
        src = buildpath(BASE_PATH, "README.md")
        dest = buildpath(SOURCE_PATH, "README.md")
        with open(src, encoding='utf-8') as f:
            txt = f.read()
        txt = txt.replace("support/docs/", "")
        with open(dest, 'w', encoding='utf-8') as f:
            f.write(txt)
    except Exception as e:
        exit_error(f"README copy failed: {e}")



# main program
def main():
    if not check_requirements():
        exit_error("requirements not met")
    if not os.path.isdir(DEST_PATH):
        os.makedirs(DEST_PATH)
    if COPY_README:
        copy_readme()
    command = "sphinx-build"
    args = [
        SOURCE_PATH,
        DEST_PATH,
    ]
    try:
        run = [command] + args
        subprocess.run(run)
    except Exception as e:
        exit_error(f"error running `{command}`: {e}")
    return 0



# main entry point
if __name__ == "__main__":
    main()


# end.
