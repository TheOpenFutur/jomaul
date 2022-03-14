# Import utilities
import os
import importlib
from datetime import datetime
# Import Jomaul modules
from jomaul.Schedule import Schedule
from jomaul.Job import Job
from jomaul.Trigger import TriggerHandler, TriggerSet

class JobManager:
    def __init__(self, config={}):
        # Configure the jobs directory
        if 'jobs_directory' in config.keys():
            self.__jobs_directory = config['jobs_directory']
        else:
            self.__jobs_directory = "Jobs"
        # Configure the Schedule object
        if 'schedule' in config.keys():
            self.__schedule = Schedule(config['schedule'])
        else:
            self.__schedule = Schedule()
        # Configure the TriggerHandler object
        if 'trigger_handler' in config.keys():
            self.__trigger_handler = TriggerHandler(config['trigger_handler'])
        else:
            self.__trigger_handler = TriggerHandler()
        # Build dictionary containing the configuration of each Job object
        self.__jobs = {}
        # Iterates through each file in the configured jobs directory
        for job_file in os.listdir(self.__jobs_directory):
            # Only looks for python files and ignores __init__.py
            if job_file.endswith('.py') == True and job_file != '__init__.py':
                # Loads the individual Job module
                job = self.load_job(job_file)
                # Clean up job name
                job_name = job_file[:-3]
                # Adds job schedule to
                self.__jobs[job_name] = job
        # Updates schedule data
        self.__schedule.update_schedule(self.__jobs)

    # Saves the schedule to disk
    def save_to_disk(self):
        self.__schedule.save_to_disk()
        self.__trigger_handler.save_to_disk()

    # Runs a job with the specified name, along with its dependent jobs
    def run_job(self, job_name, parent_job_result=None):
        job = self.load_job("{}.py".format(job_name))
        run_result = job.run(parent_job_result=parent_job_result)
        self.__schedule.set_run_data(job_name, {
            "status":"waiting",
            "last_run":datetime.now().isoformat(),
            "success":run_result[0],
            "last_run_result":run_result[1]
        })
        dependent_jobs = self.__schedule.get_dependent_jobs(job_name)
        for dependent_job_name in dependent_jobs.keys():
            dependent_job_schedule = dependent_jobs[dependent_job_name]
            if "success" in dependent_job_schedule.keys() and "result" in dependent_job_schedule.keys():
                if dependent_job_schedule['success'] == run_result[0] and dependent_job_schedule['result'] == run_result[1]:
                    self.run_job(dependent_job_name, parent_job_result=run_result)
            elif "success" in dependent_job_schedule.keys():
                if dependent_job_schedule['success'] == run_result[0]:
                    self.run_job(dependent_job_name, parent_job_result=run_result)
            elif "result" in dependent_job_schedule.keys():
                if dependent_job_schedule['result'] == run_result[1]:
                    self.run_job(dependent_job_name, parent_job_result=run_result)
            else:
                self.run_job(dependent_job_name, parent_job_result=run_result)

    # Returns a list containing the run result for each job
    def run_pending_jobs(self):
        # Runs all jobs in schedule that have a pending status
        schedule = self.__schedule.get_schedule()
        for job_name in schedule.keys():
            if schedule[job_name]['run_data']['status'] == 'pending':
                self.run_job(job_name)

    # Loads the Job object from the targeted file
    def load_job(self, job_file):
        # Grab job module from file
        spec = importlib.util.spec_from_file_location("module.name", "{}/{}".format(self.__jobs_directory, job_file))
        job_module = importlib.util.module_from_spec(spec)
        # Import job module into memory
        spec.loader.exec_module(job_module)
        # Load job
        return eval("job_module.{}()".format(job_file[:-3]))

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
