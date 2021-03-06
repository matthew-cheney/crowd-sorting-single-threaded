import _pickle as pickle
import os
import shutil

import numpy as np
from datetime import datetime

from crowdsorting.app_resources.docpair import DocPair
from crowdsorting.app_resources.sorting_algorithms.MonteCarlo import MonteCarlo as MC


class MonteCarloProxy:
    def __init__(self, project_name):
        self.mc = None
        self.number_of_docs = 0
        self.rounds = 0
        self.no_more_pairs = False
        self.project_name = project_name
        self.logPath = f"crowdsorting/MC_Logs/{self.project_name}"

    @staticmethod
    def get_algorithm_name():
        return "Monte Carlo Sorting"

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
        print("creating mc")
        self.fossilIncrement = fossilIncrement
        self.fossilIncrementCounter = 0
        self.number_of_docs = len(data)
        self.rounds = rounds
        dat = np.asarray(data)
        np.random.shuffle(dat)
        self.mc = MC(dat, epsilon=10, logPath=f'{self.logPath}/logs')
        self.no_more_pairs = False
        with open(f"crowdsorting/app_resources/sorter_instances/{self.project_name}.pkl", "wb") as output_file:  # noqa: E501
            pickle.dump(self, output_file)

    def pickle_mc(self):
        print("pickling mc")
        with open(f"crowdsorting/app_resources/sorter_instances/{self.project_name}.pkl", "wb") as f:  # noqa: E501
            pickle.dump(self, f)

    def get_pair(self, number_of_docs, allDocs):
        # if self.no_more_pairs:
        #     return "no good pair found"
        try:
            if isinstance(self.mc, type(None)):
                # self.unpickle_mc(number_of_docs)
                return "no mc created yet"
        except FileNotFoundError:
            return False

        allDocs_names = [x.name for x in allDocs]

        mc_pair = self.mc.next_pair(allDocs_names)
        if isinstance(mc_pair, type(None)):
            self.no_more_pairs = True
            return "no pair available now"
        doc_one_name = self.mc.get_script(mc_pair[0])
        doc_two_name = self.mc.get_script(mc_pair[1])
        if mc_pair is None:
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
            return "no pair available here"
        return doc_pair

    def make_judgment(self, easier_doc_name, harder_doc_name, duration,
                      judge_name='Unknown'):
        easier_doc_id = self.mc.get_ID(easier_doc_name.name)
        harder_doc_id = self.mc.get_ID(harder_doc_name.name)
        pair = (easier_doc_id, harder_doc_id)
        self.mc.compare_id(pair, False, reviewer=judge_name, time=duration)  #, reviewer=judge_name, time=datetime.now())
        self.pickle_mc()
        self.fossilIncrementCounter += 1
        if self.fossilIncrementCounter == self.fossilIncrement:
            self.fossilize_self()
            self.fossilIncrementCounter = 0

    def get_sorted(self, allDocs, allJudgments):
        # if isinstance(self.mc, type(None)):
        #     self.unpickle_mc(len(allDocs))
        # if len(allDocs) < 1:
        #     return "No files in database"
        # Built sorted more intelligently averages all N candidate lists
        # sortedFiles = self.mc.get_sorted()
        builtSorted = self.mc.get_sorted_builder()
        return builtSorted

    def get_possible_judgments_count(self):
        print(f'returning number of pairs: 9001')
        return "9001"

    def get_confidence(self):
        if self.mc.all_same:
            return 1
        return self.mc.get_confidence()

    def get_number_comparisons_made(self):
        return self.mc.get_comparisons_made()

    def unpickle_mc(self, param):
        pass

    def fossilize_self(self):
        timestamp = datetime.now().strftime('_%Y_%m_%d_%H_%M_%S_%f')
        with open(f'{self.logPath}/fossils/{self.project_name}{timestamp}', 'wb') as f:
            pickle.dump(self, f)

    def delete_self(self):
        print(f"deleting {self.mc} pickles")
        if os.path.exists(f"crowdsorting/app_resources/sorter_instances/{self.project_name}.pkl"):
            os.remove(f"crowdsorting/app_resources/sorter_instances/{self.project_name}.pkl")
        if os.path.exists(self.logPath):
            shutil.rmtree(self.logPath)

    def get_round_list(self):
        return []

    def finished(self):
        return self.no_more_pairs