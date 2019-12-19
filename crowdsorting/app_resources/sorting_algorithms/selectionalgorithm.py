from abc import ABC, abstractmethod


class SelectionAlgorithm(ABC):

    @abstractmethod
    def get_pair(self, allDocs, allJudgments):
        pass

    @abstractmethod
    def get_sorted(self, allFiles, allJudgments):
        pass

    @abstractmethod
    def get_confidence(self):
        pass
