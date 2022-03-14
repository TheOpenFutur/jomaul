class Job:
    # Default initializer
    def __init__(self, config={}):
        # Configure the job schedule
        if 'schedule' in config.keys():
            self.__schedule = config['schedule']
        else:
            self.__schedule = {"schedule_type":"interval", "unit":"seconds", "frequency":86400}

    # Returns the schedule for the targeted Job object
    def get_schedule(self):
        return self.__schedule

    # Runs the main portion of the job, according to the configurations set above
    def run(self, parent_job_result = None):
        # Place job functionality here.
        return [True,""]
