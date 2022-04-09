import requests, json

class Test:
    # Tests job API endpoints
    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port
        self.status = True
        self.test_job = {
            "zsmith/Job2":{
                "job_name":"TriggeredJob",
                "job_path":"zsmith/Jobs/TriggeredJob",
                "parameters":{
                    "print_this":"Heyo for the first time!"
                }
            }
        }

    def run(self):
        # Runs tests and stores results in a dictionary
        test_results = {
            "List Jobs":self.get_job_list(),
            "Create Job":self.create_job(),
            "View Job":self.view_job(),
            "Run Job":self.run_job(),
            "Update Job":self.update_job(),
            "Run Updated Job":self.run_job(),
            "Delete Job":self.delete_job()
        }
        # Return test results
        return {"status":self.status,"results":test_results}

    def get_job_list(self):
        response = requests.get('http://{}:{}/jobs/'.format(self.ip_address, self.port))
        if response.ok:
            return True
        else:
            if self.status: self.status = False
            return False

    def create_job(self):
        response = requests.post('http://{}:{}/jobs/'.format(self.ip_address, self.port), json=self.test_job)
        if response.ok:
            return True
        else:
            if self.status: self.status = False
            return False

    def view_job(self):
        response = requests.get('http://{}:{}/jobs/1'.format(self.ip_address, self.port))
        self.test_job =  response.json()
        if response.ok:
            return True
        else:
            if self.status: self.status = False
            return False

    def update_job(self):
        self.test_job['parameters']['print_this'] = "Heyo for the second time!"
        response = requests.post('http://{}:{}/jobs/1'.format(self.ip_address, self.port), json=self.test_job)
        if response.ok:
            return True
        else:
            if self.status: self.status = False
            return False

    def run_job(self):
        response = requests.get('http://{}:{}/jobs/1/run'.format(self.ip_address, self.port), json={})
        if response.ok:
            return True
        else:
            if self.status: self.status = False
            return False

    def delete_job(self):
        response = requests.delete('http://{}:{}/jobs/1'.format(self.ip_address, self.port))
        if response.ok:
            return True
        else:
            if self.status: self.status = False
            return False
