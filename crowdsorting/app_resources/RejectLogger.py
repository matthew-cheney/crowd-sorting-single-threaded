import datetime
import json
import os


class RejectLogger:

    def __init__(self):
        self.folder_path = 'crowdsorting/Reject_Logs/'

    def log_reject(self, project_name, user, doc1, doc2, hard=True):
        project_name = project_name.replace(' ', '_')
        timestamp = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')
        if not os.path.exists(self.folder_path + project_name):
            os.makedirs(self.folder_path + project_name)
            os.makedirs(self.folder_path + project_name + '/too_hard')
            os.makedirs(self.folder_path + project_name + '/too_easy')

        log_dict = {"Reviewer": user,
                    "Doc1": doc1,
                    "Doc2": doc2,
                    "Reason Rejected": "unknown"}

        if hard:
            with open(f'{self.folder_path}{project_name}/too_hard/{user}_{timestamp}', 'w') as f:
                log_dict['Reason Rejected'] = 'Too Hard'
                self.log_json(log_dict, f)
        else:
            with open(f'{self.folder_path}{project_name}/too_easy/{user}_{timestamp}', 'w') as f:
                log_dict['Reason Rejected'] = 'Too Easy'
                self.log_json(log_dict, f)

    def log_json(self, log_dict, file):
        json.dump(log_dict, file, indent=4)