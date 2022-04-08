import requests, json
from jomaul.test import job

class Test:
    def __init__(self, ip_address, port, only_show_failed_results=True):
        self.ip_address = ip_address
        self.port = port
        self.only_show_failed_results = only_show_failed_results

    def run(self):
        # Generate test results
        test_results = {
            "Jobs":job.Test(self.ip_address, self.port).run()
        }
        # Display results
        for result in test_results.keys():
            print("{} - {}".format(result,test_results[result]['status']))
            print("----------------------")
            if self.only_show_failed_results == False:
                for single_result in test_results[result].keys():
                    print("| {} - {}".format(single_result, test_results[result][single_result]))
            else:
                for single_result in test_results[result]:
                    if test_results[result][single_result] == False:
                        print("| {} - {}".format(single_result, test_results[result][single_result]))
