from .selection_algorithm import *

class mergeSort(selection_algorithm):
    @staticmethod
    def getPair(allDocs, allJudgments):
        for doc in allDocs:
            print(doc)
            print('harder', list(doc.judgments_harder))
            print('easier', list(doc.judgments_easier))
        return 'no docs to compare'


    @staticmethod
    def getSorted(allFiles, allJudgments):
        pass
