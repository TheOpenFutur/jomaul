# Import web server utilities
from flask import Flask, render_template, g, Blueprint, request
# Import jomaul utilities
from jomaul.job import JobHandler
# Import general utilities
import argparse, json

# Parse arguments
parser = argparse.ArgumentParser(description='Build a jomaul server.')
parser.add_argument("config_file", help="The path of the config")
args = parser.parse_args()

# Load config
with open(args.config_file, "r") as config_file:
    config = json.load(config_file)
# Build handler objects
if 'server_type' in config:
    if config['server_type'] == 'job':
        job_handler = JobHandler(config)

# Define job views
job_views = Blueprint('jobs', __name__, url_prefix='/jobs')
@job_views.route('/', methods=['GET'])
def get_jobs():
    return job_handler.list_jobs()

@job_views.route('/', methods=['POST'])
def create_jobs():
    configs = request.json
    # TODO: ADD CONFIG VALIDATION
    return job_handler.create_jobs(configs=configs)

@job_views.route('/<job_id>', methods=['GET'])
def get_job(job_id):
    return job_handler.get_job(int(job_id))

@job_views.route('/<job_id>', methods=['POST'])
def update_job(job_id):
    config = request.json
    config['id'] = int(job_id)
    # TODO: ADD CONFIG VALIDATION
    return job_handler.update_job(config)

@job_views.route('/<job_id>/run', methods=['GET'])
def run_job(job_id):
    content = request.json
    parameters = None
    if 'parameters' in content.keys():
        parameters = content['parameters']
    # TODO: VALIDATE PARAMETERS
    results = job_handler.run_job(int(job_id),parameters=parameters)
    return results

@job_views.route('/<job_id>', methods=['DELETE'])
def delete_job(job_id):
    return job_handler.delete_job(int(job_id))

app = Flask(__name__)
if 'server_type' in config:
    if config['server_type'] == 'job':
        app.register_blueprint(job_views)
        # Run server
        app.run(host=config['job']['ip_address'], port=config['job']['port'])
else:
    print("No server type supplied, cannot run")
