from .selection_algorithm import *

class pairall(selection_algorithm):

    def getPair(self, allDocs, allJudgments):
        if len(allDocs) < 2:
            return "Not enough docs to compare"
        # Remove docs that are currently checked out from consideration
        '''toRemove = []
        for doc in allDocs:
            if doc.checked_out:
                toRemove.append(doc)
        for doc in toRemove:
            allDocs.remove(doc)
        if len(allDocs) < 2:
            return "All docs are checked out"
'''
        allDocs.sort(key=lambda x: self.getNumCompares(x))

        while len(allDocs) > 1:
            doc1 = allDocs[0]
            doc2 = self.getCompareDoc(allDocs[1:], allJudgments, doc1)

            if type(doc2) == type(doc1):
                print('found a pair')
                return DocPair(doc1, doc2)
            allDocs = allDocs[1:]
        return "no good pair found"



    def getNumCompares(self, doc):
        return len(list(doc.judgments_harder)) + len(list(doc.judgments_easier))

    def isInHarder(self, base_doc, query_doc):
        self.visited_docs = []
        return self.isInHarderRecurse(base_doc, query_doc)

    def isInHarderRecurse(self, current_doc, query_doc):
        if current_doc in self.visited_docs:
            return False
        toReturn = False
        self.visited_docs.append(current_doc)
        for judgment in current_doc.judgments_easier:
            if query_doc.id == judgment.doc_harder.id:
                print(f"found harder one: {query_doc.name}")
                return True
            print(f"calling hard_R on {judgment.doc_harder.name}")
            toReturn = (toReturn + self.isInHarderRecurse(judgment.doc_harder, query_doc))
        return toReturn

    def isInEasier(self, base_doc, query_doc):
        self.visited_docs = []
        return self.isInEasierRecurse(base_doc, query_doc)

    def isInEasierRecurse(self, current_doc, query_doc):
        if current_doc == query_doc:
            return True
        if current_doc in self.visited_docs:
            return False
        toReturn = False
        self.visited_docs.append(current_doc)
        for judgment in current_doc.judgments_harder:
            if query_doc.id == judgment.doc_easier.id:
                print(f"found easier one: {query_doc.name}")
                return True
            print(f"calling easy_R on {judgment.doc_easier.name}")
            toReturn = (toReturn + self.isInEasierRecurse(judgment.doc_easier, query_doc))
        return toReturn

    def getCompareDoc(self, allDocs, allJudgments, doc1):
        if len(allJudgments) < 1:
            print('judgments', allJudgments)
            return allDocs[0]
        for doc in allDocs:
            if not self.isInHarder(doc1, doc):
                print('not in harder tree')
                if not self.isInEasier(doc1, doc):
                    print('not in easier tree')
                    print(f"returning {doc}")
                    return doc
        return "No comparisons available"

    def getSorted(self, allDocs, allJudgments):
        if len(allDocs) < 1:
            return "No files in database"
        filesAndScores = {file.name: 0 for file in allDocs}
        for judgment in allJudgments:
            filesAndScores[judgment.doc_harder.name] += 1
            filesAndScores[judgment.doc_easier.name] -= 1
        files = sorted(filesAndScores.items(), key=operator.itemgetter(1))
        sortedFiles = [x[0] for x in files]
        if len(allDocs) > 1:
            confidence = len(allJudgments) / (len(allDocs) * (len(allDocs) - 1) * .5)
        else:
            confidence = 0
        return sortedFiles, confidence
