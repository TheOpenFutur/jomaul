# Import utilities
import os
import importlib.util
from datetime import datetime
import json

class JobHandler:
    def __init__(self, config={}):
        # Load config
        with open('config.json') as json_file:
            config = json.load(json_file)
        # Set local properties
        self.__job_file = config['job']['job_file']
        self.__modules_directory = config['modules_directory']
        # Build dictionary containing the configuration of each Job object
        if os.path.exists(self.__job_file):
            with open(self.__job_file, 'r') as job_file:
                self.__jobs = json.load(job_file)['jobs']
                for job_name in self.__jobs.keys():
                    self.__jobs[job_name] = Job(config = self.__jobs[job_name])
        else:
            self.__jobs = {}


    # Saves jobs to disk
    def save_to_disk(self):
        # Get job file contents
        with open(self.__job_file, 'r') as job_file:
            file_contents = json.load(job_file)
        # Modify the file contents to contains the most recent job information
        for job_name in self.__jobs.keys():
            file_contents['jobs'][job_name] = self.__jobs[job_name].get_config()
        # Update the job file
        with open(self.__job_file, 'w') as job_file:
            json.dump(file_contents, job_file, indent=4)

    # Runs a job with the specified name, along with its dependent jobs
    def run_job(self, job_name, parameters=None):
        job_path = self.__jobs[job_name].get_path()
        job = self.load_job("{}.py".format(job_path), config=self.__jobs[job_name].get_config())
        if parameters != None:
            return job.run(parameters=parameters)
        else:
            return job.run()


    # Loads the Job object from the targeted file
    def load_job(self, job_file, config):
        # Grab job module from file
        spec = importlib.util.spec_from_file_location("module.name", "{}/{}".format(self.__modules_directory, job_file))
        job_module = importlib.util.module_from_spec(spec)
        # Import job module into memory
        spec.loader.exec_module(job_module)
        # Load job
        return eval("job_module.{}({})".format(config['job_name'],config))

class Job:
    # Default initializer
    def __init__(self, config={}):
        self.__config = config
        self.__job_path = self.__config['job_path']
        if 'parameters' in self.__config.keys():
            self.parameters = self.__config['parameters']
        else:
            self.parameters = {}
        if 'required_parameters' in self.__config.keys():
            self.__required_parameters = self.__config['required_parameters']
        else:
            self.__required_parameters = {}

    # Returns the parameters for the targeted Job object
    def get_parameters(self):
        return self.parameters

    def get_path(self):
        return self.__job_path

    def get_config(self):
        return self.__config

    # Runs the main portion of the job, according to the configurations set above
    def run(self, parameters = {}):
        # Adds the new parameters to the parameters dictionary
        for parameter in parameters.keys():
            self.parameters[parameter] = parameters[parameter]
        # Validates required parameters
        for required_parameter in self.__required_parameters.keys():
            if required_parameter not in self.parameters.keys():
                return [False, "The following required parameter is missing: {}".format(required_parameter)]
            if self.__required_parameters[required_parameter] != None and type(self.parameters[required_parameter]) != self.__required_parameters[required_parameter]:
                return [False, "The following parameter is a {}, when it should be a {}: {}".format(type(self.parameters[required_parameter]), self.__required_parameters[required_parameter], required_parameter)]
