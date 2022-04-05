# Import utilities
import os
import importlib.util
from datetime import datetime
import json
# Import Jomaul modules
from jomaul.jomaul_core.Job import Job
from jomaul.jomaul_core.Trigger import TriggerHandler, TriggerSet

class JobManager:
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


    # # Saves the schedule to disk
    # def save_to_disk(self):
    #     self.__trigger_handler.save_to_disk()

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

    def set_trigger_states(self, trigger_states):
        # Build an empty list of jobs associated with specified triggers
        cumulative_job_list = []
        # Iterate through each specified trigger
        for trigger_name in trigger_states.keys():
            # Sets the state for the specified trigger
            self.__trigger_handler.set(trigger_name, trigger_states[trigger_name])
            # Get a list of jobs associated with the specified trigger
            associated_jobs = self.__schedule.get_triggered_jobs(trigger_name)
            # Append triggered_job to cumulative_job_list if it does not already exist
            for job in associated_jobs:
                job_exists = False
                for existing_job in cumulative_job_list:
                    if job[0] == existing_job[0]:
                        job_exists = True
                        pass
                if job_exists == False: cumulative_job_list.append(job)
        # Evaluate the trigger set of each associated job and run jobs that have been successfully triggered
        for job in cumulative_job_list:
            if job[1].evaluate(self.__trigger_handler):
                self.run_job(job[0])
