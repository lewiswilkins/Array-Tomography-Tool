import ast
import json
import pathlib
import subprocess
import time
from glob import glob
from pathlib import Path
import os

from bokeh.client import pull_session
from bokeh.embed import server_document
from flask import Flask, request, session
from flask_cors import CORS, cross_origin

from lib import segmentation, utils

app = Flask(__name__)


def get_log(job_id: str, parameter: str) -> str: 
    try:
        return pathlib.Path(f"/tmp/{job_id}/{parameter}.out").read_text()
        
    except FileNotFoundError:
        print("no filesssss")
        return "..."


@app.route('/colocalisation/', methods=["POST", "GET"])
def run_colocalisation():
    if request.method == "POST":
        config = request.json
        job_id = config['job_id']
        utils.mkdir(f"/tmp/{job_id}/")
        with open(f"/tmp/{job_id}/colocalisation.out", "w") as log:
            app.colocalisation_jobs[job_id] = subprocess.Popen(
                    ["../api/colocalisation_api.py", json.dumps(config)],
                    stdout=log, stderr=log
                )
        
        print(app.colocalisation_jobs)
        return config


@app.route('/colocalisation/<job_id>/<parameter>/')
def get_colocalisation_logs(job_id, parameter):
    log = get_log(job_id, parameter)
    
    return log

@app.route('/colocalisation/<job_id>/')
def kill_job(job_id):
    app.colocalisation_jobs[int(job_id)].kill()

    return job_id

@app.route('/segment/gui/<threshold_method>/')
def run_segment_gui(threshold_method: str):
    if app.running_bokeh_process:
        app.running_bokeh_process.kill()

    threshold_method_gui = {
        "autolocal": "segment_autolocal_bokeh",
        "fixed": "segment_fixed_bokeh"
    }
    file_name = request.args.get("fileName")
    os.system("ls -l")
    os.system("pwd")
    app.running_bokeh_process = subprocess.Popen(
        [
            "bokeh", 
            "serve",  
            "--address",
            "0.0.0.0",
            "--allow-websocket-origin=*",
            "--log-level=debug", 
            f"../bokeh/{threshold_method_gui[threshold_method]}.py",
            "--args",
            f"{file_name}"
            ]
        )
    script = server_document(f"http://localhost:5006/{threshold_method_gui[threshold_method]}")
    url = script.split('"')[3]
    script_id = url.split("=")[1].split("&")[0]
    obj = {"url": url, "script_id": script_id}
    
    return obj


@app.route('/segmentation/', methods=["POST", "GET"])
def run_segment():
    config = request.json
    if request.method == "POST":
        utils.mkdir(f"/tmp/{config['job_id']}/")
        print(config['job_id'])
        with open(f"/tmp/{config['job_id']}/segmentation.out", "w") as log:
            subprocess.Popen(
                ["../api/segment_api.py", json.dumps(config), ],
                stdout=log, stderr=log
            )

        return config


@app.route('/segment/list_files/')
def get_segment_file_list():
    file_path = request.args.get('directory')
    file_list = {"file_list": glob(f"{file_path}/*")}

    return file_list


@app.route('/segment/list_threshold_methods/')
def get_segment_threshold_methods():
    threshold_methods = {"threshold_methods": list(segmentation.segment_methods.keys())}

    return json.dumps(threshold_methods)

@app.route('/alignment/', methods=["POST", "GET"])
def run_alignment():
    if request.method == "POST":
        config = request.json
        t_message = """lots 
        of
        words
        on 
        different
        lines"""
        Path(f"/tmp/{config['job_id']}/").mkdir()
        Path(f"/tmp/{config['job_id']}/test.out").write_text(t_message)
        
        return config


if __name__ == '__main__':
    CORS(app, support_credentials=True)
    app.running_bokeh_process = None
    app.colocalisation_jobs = {}
    app.run(host='0.0.0.0')
