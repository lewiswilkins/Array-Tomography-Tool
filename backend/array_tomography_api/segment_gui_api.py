#!/usr/bin/env python
import subprocess
import sys


threshold_method_gui = {
    "autolocal": "segmemt_autolocal_gui.py",
    "fixed": "segment_fixed_gui.py"
    }


if __name__ == "__main__":
    threshold_method = sys.argv[1]
    parameters = sys.argv[2]
    
    subprocess.run(
        [
            "bokeh", 
            "serve", 
            "--show",  
            "--allow-websocket-origin='*'", 
            f"../bokeh/{threshold_method_gui[threshold_method]}", 
            "--args",
            parameters
            ]
        )
