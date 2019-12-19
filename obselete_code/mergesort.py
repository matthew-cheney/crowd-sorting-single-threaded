from crowdsorting.app_resources.sorting_algorithms.selectionalgorithm import *


class mergeSort(SelectionAlgorithm):
    @staticmethod
    def get_pair(allDocs, allJudgments):
        for doc in allDocs:
            print(doc)
            print('harder', list(doc.judgments_harder))
            print('easier', list(doc.judgments_easier))
        return 'no docs to compare'

    @staticmethod
    def get_sorted(allFiles, allJudgments):
        pass
