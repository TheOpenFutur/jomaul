# Import web server utilities
from flask import Flask, render_template, g, Blueprint
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
@job_views.route('/')
def get_jobs():
    return job_handler.list_jobs()

@job_views.route('/<job_id>')
def get_job(job_id):
    return job_handler.get_job(int(job_id))

app = Flask(__name__)
if 'server_type' in config:
    if config['server_type'] == 'job':
        app.register_blueprint(job_views)
        # Run server
        app.run(host=config['job']['ip_address'], port=config['job']['port'])
else:
    print("No server type supplied, cannot run")
