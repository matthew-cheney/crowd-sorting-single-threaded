import _pickle as pickle

import numpy as np
from datetime import datetime

from crowdsorting.app_resources.docpair import DocPair
from crowdsorting.app_resources.sorting_algorithms.ACJ import ACJ


class ACJProxy:
    def __init__(self, project_name):
        self.acj = None
        self.number_of_docs = 0
        self.rounds = 0
        self.no_more_pairs = False
        self.project_name = project_name

    def create_acj(self, data, rounds=15, maxRounds=10, noOfChoices=1, logPath="crowdsorting/ACJ_Log/", optionNames=["Choice"]):
        print("creating acj")
        self.number_of_docs = len(data)
        self.rounds = rounds
        dat = np.asarray(data)
        np.random.shuffle(dat)
        self.acj = ACJ(dat, maxRounds, noOfChoices, logPath, optionNames)
        self.no_more_pairs = False
        with open(f"crowdsorting/app_resources/sorter_instances/{self.project_name}.pkl", "wb") as output_file:
            pickle.dump(self, output_file)
        # del (self.acj)
        # with open(f"crowdsorting/app_resources/sorter_instances/{self.project_name}.pkl", "rb") as input_file:
        #     self.acj = pickle.load(input_file)

    # def unpickle_acj(self, length):
    #     print("unpickling acj")
    #     with open(f"crowdsorting/app_resources/sorter_instances/{self.project_name}.pkl", "rb") as input_file:
    #         self.acj = pickle.load(input_file)

    def pickle_acj(self):
        print("pickling acj")
        with open(f"crowdsorting/app_resources/sorter_instances/{self.project_name}.pkl", "wb") as f:
            pickle.dump(self, f)

    def getPair(self, number_of_docs, allDocs):
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
        if acj_pair == None:
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

    def makeJudgment(self, easier_doc_name, harder_doc_name, judge_name='Unknown'):
        easier_doc_id = self.acj.getID(easier_doc_name.name)
        harder_doc_id = self.acj.getID(harder_doc_name.name)
        pair = (easier_doc_id, harder_doc_id)
        self.acj.IDComp(pair, False, reviewer=judge_name, time=datetime.now())
        self.pickle_acj()

    def getSorted(self, allDocs, allJudgments):
        if isinstance(self.acj, type(None)):
            self.unpickle_acj(len(allDocs))
        if len(allDocs) < 1:
            return "No files in database"
        sortedFiles = [x[0] for x in self.acj.results()[0]]
        return sortedFiles

    def getPossibleJudgmentsCount(self):
        total = int(self.rounds * (self.number_of_docs / 2))
        if total < 1:
            total = 1
        print(f'returning number of pairs: {total}')
        return total

    def getConfidence(self):
        return self.acj.reliability()[0]

    def getNumberComparisonsMade(self):
        return self.acj.getComparisonsMade()
