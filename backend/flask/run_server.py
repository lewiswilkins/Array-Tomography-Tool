import ast
import json
import pathlib
import subprocess
import time
from glob import glob

from bokeh.client import pull_session
from bokeh.embed import server_document
from flask import Flask, request, session
from flask_cors import CORS, cross_origin

from array_tomography_lib import segment

app = Flask(__name__)

running_bokeh_process = None

def get_log(job_id: str, parameter: str) -> str: 
    try:
        return pathlib.Path(f"/tmp/{job_id}/{parameter}.out").read_text()
        
    except FileNotFoundError:
        return "..."


@app.route('/colocalisation/', methods=["POST", "GET"])
def run_colocalisation():
    if request.method == "POST":
        config = request.json
        subprocess.run(
            ["./array_tomography_api/colocalisation_api.py", json.dumps(config)]
        )
        
        return config


@app.route('/colocalisation/<job_id>/<parameter>/')
def get_colocalisation_logs(job_id, parameter):
    log = get_log(job_id, parameter)
    
    return log


@app.route('/segment/gui/<threshold_method>/')
def run_segment_gui(threshold_method: str):
    if app.running_bokeh_process:
        app.running_bokeh_process.kill()

    threshold_method_gui = {
        "autolocal": "segment_autolocal_bokeh",
        "fixed": "segment_fixed_gui"
    }
    file_name = request.args.get("fileName")
    app.running_bokeh_process = subprocess.Popen(
        [
            "bokeh", 
            "serve",  
            "--allow-websocket-origin=*",
            "--log-level=debug", 
            f"bokeh/{threshold_method_gui[threshold_method]}.py",
            "--args",
            f"{file_name}"
            ]
        )
    script = server_document(f"http://localhost:5006/{threshold_method_gui[threshold_method]}")
    url = script.split('"')[3]
    script_id = url.split("=")[1].split("&")[0]
    obj = {"url": url, "script_id": script_id}
    
    return obj


@app.route('/segment/')
def run_segment(threshold_method: str):
    config = request.json
    if request.method == "POST":
        subprocess.Popen(
            ["./array_tomography_api/segment_api.py", json.dumps(config)]
        )

        return config



@app.route('/segment/list_files/')
def get_segment_file_list():
    file_path = request.args.get('directory')
    file_list = {"file_list": glob(f"{file_path}/*")}

    return file_list


@app.route('/segment/list_threshold_methods/')
def get_segment_threshold_methods():
    threshold_methods = {"threshold_methods": list(segment.segment_methods.keys())}

    return json.dumps(threshold_methods)


if __name__ == '__main__':
    CORS(app, support_credentials=True)
    app.running_bokeh_process = None
    app.run()
