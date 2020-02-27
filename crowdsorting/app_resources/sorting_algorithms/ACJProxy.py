import _pickle as pickle
import os
import shutil

import numpy as np
from datetime import datetime

from crowdsorting.app_resources.docpair import DocPair
from crowdsorting.app_resources.sorting_algorithms.ACJ import ACJ

# Note - this algorithm takes 0.5*n^2 - 5*(x/10) comparisons to complete,
# where n is the number of documents in data

class ACJProxy:
    def __init__(self, project_name):
        self.acj = None
        self.number_of_docs = 0
        self.rounds = 0
        self.no_more_pairs = False
        self.project_name = project_name
        self.logPath = f"crowdsorting/ACJ_Logs/{self.project_name}"
        self.remaining_in_round = []
        self.served_not_returned = []
        self.finished = False
        self.total_comparisons = 0

    @staticmethod
    def get_algorithm_name():
        return "Adaptive Comparative Judgment"

    def initialize_selector(self, data, rounds=15, maxRounds=10, noOfChoices=1,
                   logPath=None, optionNames=None, fossilIncrement=10):
        if optionNames is None:
            optionNames = ["Choice"]
        if not logPath is None:
            self.logPath = logPath
        if not os.path.isdir(self.logPath):
            os.mkdir(self.logPath)
        if not os.path.isdir(f'{self.logPath}/logs'):
            os.mkdir(f'{self.logPath}/logs')
        if not os.path.isdir(f'{self.logPath}/fossils'):
            os.mkdir(f'{self.logPath}/fossils')
        print("creating acj")
        self.fossilIncrement = fossilIncrement
        self.fossilIncrementCounter = 0
        self.number_of_docs = len(data)
        self.total_comparisons = 0.5*(self.number_of_docs**2) - 5*(self.number_of_docs / 10)
        self.rounds = rounds
        dat = np.asarray(data)
        np.random.shuffle(dat)
        self.acj = ACJ(dat, maxRounds, noOfChoices, f'{self.logPath}/logs', optionNames)
        self.no_more_pairs = False
        with open(f"crowdsorting/app_resources/sorter_instances/{self.project_name}.pkl", "wb") as output_file:  # noqa: E501
            pickle.dump(self, output_file)
        self.fossilize_self()

    def pickle_acj(self):
        # print("pickling acj")
        with open(f"crowdsorting/app_resources/sorter_instances/{self.project_name}.pkl", "wb") as f:  # noqa: E501
            pickle.dump(self, f)

    def get_pair(self, number_of_docs, allDocs):
        if self.no_more_pairs:
            return "no good pair found"
        try:
            if isinstance(self.acj, type(None)):
                # self.unpickle_acj(number_of_docs)
                return "no acj created yet"
        except FileNotFoundError:
            return False

        acj_pair = self.acj.nextIDPair()
        if isinstance(acj_pair, type(None)):
            self.no_more_pairs = True
            return "no pair available"
        doc_one_name = self.acj.getScript(acj_pair[0])
        doc_two_name = self.acj.getScript(acj_pair[1])
        if acj_pair is None:
            return "no good pair found"
        doc_one = False
        doc_two = False
        for doc in allDocs:
            if doc.name == doc_one_name:
                doc_one = doc
            if doc.name == doc_two_name:
                doc_two = doc
            if doc_one and doc_two:
                break
        doc_pair = DocPair(doc_one, doc_two)
        if not doc_one or not doc_two:
            return "no pair available"
        self.served_not_returned.append([doc_one, doc_two])
        return doc_pair

    def make_judgment(self, easier_doc_name, harder_doc_name, duration,
                      judge_name='Unknown'):
        easier_doc_id = self.acj.getID(easier_doc_name.name)
        harder_doc_id = self.acj.getID(harder_doc_name.name)
        pair = (easier_doc_id, harder_doc_id)
        self.acj.IDComp(pair, False, reviewer=judge_name, time=duration)
        if [easier_doc_name, harder_doc_name] in self.served_not_returned:
            self.served_not_returned.remove([easier_doc_name, harder_doc_name])
        elif [harder_doc_name, easier_doc_name] in self.served_not_returned:
            self.served_not_returned.remove([harder_doc_name, easier_doc_name])
        self.pickle_acj()
        self.fossilIncrementCounter += 1
        if self.fossilIncrementCounter == self.fossilIncrement:
            self.fossilize_self()
            self.fossilIncrementCounter = 0

    def get_sorted(self, allDocs, allJudgments):
        # if isinstance(self.acj, type(None)):
        #     self.unpickle_acj(len(allDocs))
        # if len(allDocs) < 1:
        #     return "No files in database"
        sortedFiles = [x[0] for x in self.acj.results()[0]]
        return sortedFiles

    def get_possible_judgments_count(self):
        total = int(self.rounds * (self.number_of_docs / 2))
        if total < 1:
            total = 1
        print(f'returning number of pairs: {total}')
        return total

    def get_confidence(self):
        return self.acj.reliability()[0]

    def get_number_comparisons_made(self):
        return self.acj.getComparisonsMade()

    def get_total_comparisons_left(self):
        return self.total_comparisons - self.acj.getComparisonsMade()

    def unpickle_acj(self, param):
        pass

    def fossilize_self(self):
        timestamp = datetime.now().strftime('_%Y_%m_%d_%H_%M_%S_%f')
        with open(f'{self.logPath}/fossils/{self.project_name}{timestamp}.pkl', 'wb') as f:
            pickle.dump(self, f)

    def delete_self(self):
        print(f"deleting {self.acj} pickles")
        if os.path.exists(f"crowdsorting/app_resources/sorter_instances/{self.project_name}.pkl"):
            os.remove(f"crowdsorting/app_resources/sorter_instances/{self.project_name}.pkl")
        if os.path.exists(self.logPath):
            shutil.rmtree(self.logPath)

    def get_round_list(self):
        return self.acj.unservedRoundList

    def finished(self):
        return self.no_more_pairs
