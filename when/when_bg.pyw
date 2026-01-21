# when consoleless launcher for Windows

import sys, os, subprocess
from .when import main


def run_bg() -> None:
    if sys.platform.startswith("win"):
        if os.path.basename(sys.argv[0]) != os.path.basename(sys.executable):
            pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
            args = [
                "cmd.exe",
                "/c",
                "start",
                "",
                "/B",
                "/min",
                pythonw,
                "-m",
                "when.when",
            ] + list(sys.argv[1:])
            si = subprocess.STARTUPINFO(wShowWindow=0)
            subprocess.run(args, startupinfo=si)
    else:
        main()


# end.
