# when consoleless launcher for Windows

import sys, os, subprocess
from .when import main

def run_bg():
    if sys.platform.startswith("win"):
        if os.path.basename(sys.argv[0]) != os.path.basename(sys.executable):
            pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
            args = [
                "cmd.exe", "/c", "start", '', "/B",
                pythonw, "-m", "when.when",
            ] + list(sys.argv[1:])
            subprocess.run(args)
    else:
        main()

# end.
