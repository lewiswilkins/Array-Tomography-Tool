#!/usr/bin/env python
import subprocess
import sys


threshold_method_gui = {
    "autolocal": "segment_autolocal_bokeh.py",
    "fixed": "segment_fixed_gui.py"
    }


if __name__ == "__main__":
    threshold_method = sys.argv[1]
    file_name = sys.argv[2]
    
    print(f"Starting boke server for {threshold_method}")
    subprocess.Popen(
        ["bokeh", "serve",  "--allow-websocket-origin='*'",
         threshold_method_gui[threshold_method], "--args", file_name]
        )
    print("let it run")

    exit()
