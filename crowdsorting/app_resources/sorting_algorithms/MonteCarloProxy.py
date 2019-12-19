import _pickle as pickle

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

    @staticmethod
    def get_algorithm_name():
        return "Monte Carlo Sorting"

    def create_mc(self, data, rounds=15, maxRounds=10, noOfChoices=1,
                  logPath="crowdsorting/ACJ_Log/", optionNames=None):
        if optionNames is None:
            optionNames = ["Choice"]
        print("creating mc")
        self.number_of_docs = len(data)
        self.rounds = rounds
        dat = np.asarray(data)
        np.random.shuffle(dat)
        self.mc = MC(dat, epsilon=10)
        self.no_more_pairs = False
        with open(f"crowdsorting/app_resources/sorter_instances/{self.project_name}.pkl", "wb") as output_file:  # noqa: E501
            pickle.dump(self, output_file)

    def pickle_mc(self):
        print("pickling mc")
        with open(f"crowdsorting/app_resources/sorter_instances/{self.project_name}.pkl", "wb") as f:  # noqa: E501
            pickle.dump(self, f)

    def get_pair(self, number_of_docs, allDocs):
        if self.no_more_pairs:
            return "no good pair found"
        try:
            if isinstance(self.mc, type(None)):
                # self.unpickle_mc(number_of_docs)
                return "no mc created yet"
        except FileNotFoundError:
            return False

        mc_pair = self.mc.next_pair()
        if isinstance(mc_pair, type(None)):
            self.no_more_pairs = True
            return "no pair available"
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
            return "no pair available"
        return doc_pair

    def make_judgment(self, easier_doc_name, harder_doc_name,
                      judge_name='Unknown'):
        easier_doc_id = self.mc.get_ID(easier_doc_name.name)
        harder_doc_id = self.mc.get_ID(harder_doc_name.name)
        pair = (easier_doc_id, harder_doc_id)
        self.mc.compare(pair, False)  #, reviewer=judge_name, time=datetime.now())
        self.pickle_mc()

    def get_sorted(self, allDocs, allJudgments):
        if isinstance(self.mc, type(None)):
            self.unpickle_mc(len(allDocs))
        if len(allDocs) < 1:
            return "No files in database"
        sortedFiles = self.mc.get_sorted()
        return sortedFiles

    def get_possible_judgments_count(self):
        print(f'returning number of pairs: 9001')
        return "9001"

    def get_confidence(self):
        return self.mc.get_confidence()

    def get_number_comparisons_made(self):
        return self.mc.get_comparisons_made()

    def unpickle_mc(self, param):
        pass
