import ast
import json
import pathlib
import subprocess
import time
from glob import glob

from bokeh.client import pull_session
from bokeh.embed import server_document
from flask import Flask, request
from flask_cors import CORS, cross_origin

app = Flask(__name__)


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
            ["./test/server_run_colocalisation_test.py", json.dumps(config)]
        )
        
        return config


@app.route('/colocalisation/<job_id>/<parameter>/')
def get_colocalisation_logs(job_id, parameter):
    log = get_log(job_id, parameter)
    
    return log


@app.route('/segment/gui/<threshold_mehtod>/')
def run_segment_gui(threshold_mehtod: str):
    parameters = request.args
    subprocess.run(
        [
            "./array_tomography_api/segment_gui_api.py", 
            threshold_mehtod, 
            parameters
        ]

    )
    script = server_document("http://localhost:5006/interactive_plot")
    url = script.split('"')[3]
    script_id = url.split("=")[1].split("&")[0]
    obj = {"url": url, "script_id": script_id}
    
    return obj


@app.route('/segment/list_files/')
def get_segment_file_list():
    file_path = request.args
    file_list = {"file_list": glob(f"{file_path}/*")}
    
    return json.loads(file_list)


if __name__ == '__main__':
    CORS(app, support_credentials=True)
    app.run()
