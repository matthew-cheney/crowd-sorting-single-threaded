from __future__ import division
import random
import os
import numpy as np
import pickle
import datetime
import json


class Decision(object):
    def __init__(self, pair, result, reviewer, time):
        self.pair = pair
        self.result = result
        self.reviewer = reviewer
        self.time = time

    def dict(self):
        return {'Pair': [str(self.pair[0]), str(self.pair[1])],
                'Result': str(self.result), 'reviewer': str(self.reviewer),
                'time': str(self.time)}


def ACJ(data, maxRounds, noOfChoices=1, logPath=None, optionNames=["Choice"]):
    if noOfChoices < 2:
        return UniACJ(data, maxRounds, logPath, optionNames)
    else:
        return MultiACJ(data, maxRounds, noOfChoices, logPath, optionNames)


class MultiACJ(object):
    '''Holds multiple ACJ objects for running comparisons with multiple choices.
    The first element of the list of acj objects keeps track of the used pairs.'''

    def __init__(self, data, maxRounds, noOfChoices, logPath=None,
                 optionNames=None):
        self.data = list(data)
        self.n = len(data)
        self.round = 0
        self.step = 0
        self.noOfChoices = noOfChoices
        self.acjs = [ACJ(data, maxRounds) for _ in range(noOfChoices)]
        self.logPath = logPath
        if optionNames == None:
            self.optionNames = [str(i) for i in range(noOfChoices)]
        else:
            self.optionNames = optionNames
            self.nextRound()

    def getScript(self, ID):
        '''Gets script with ID'''
        return self.acjs[0].getScript(ID)

    def getID(self, script):
        """Gets ID of script"""
        return self.acjs[0].getID(script)

    def infoPairs(self):
        '''Returns pairs based on summed selection arrays from Progressive Adaptive Comparitive Judgement
        Politt(2012) + Barrada, Olea, Ponsoda, and Abad (2010)'''
        pairs = []
        # Create
        sA = np.zeros((self.n, self.n))
        for acj in self.acjs:
            sA = sA + acj.selectionArray()
        while (np.max(sA) > 0):
            iA, iB = np.unravel_index(sA.argmax(), sA.shape)
            pairs.append([self.data[iA], self.data[iB]])
            sA[iA, :] = 0
            sA[iB, :] = 0
            sA[:, iA] = 0
            sA[:, iB] = 0
        return pairs

    def nextRound(self):
        '''Returns next round of pairs'''
        roundList = self.infoPairs()
        for acj in self.acjs:
            acj.nextRound(roundList)
            acj.step = 0
        self.round = self.acjs[0].round
        self.step = self.acjs[0].step
        return self.acjs[0].roundList

    def nextPair(self):
        '''gets next pair from main acj'''
        p = self.acjs[0].nextPair(startNext=False)
        if p == -1:
            if self.nextRound() != None:
                p = self.acjs[0].nextPair(startNext=False)
            else:
                return None
        self.step = self.acjs[0].step
        return p

    def nextIDPair(self):
        '''Gets ID of next pair'''
        pair = self.nextPair()
        if pair == None:
            return None
        idPair = []
        for p in pair:
            idPair.append(self.getID(p))
        return idPair

    def WMS(self):
        ret = []
        for acj in self.acjs:
            ret.append(acj.WMS())
        return ret

    def comp(self, pair, result=None, update=None, reviewer='Unknown', time=0):
        '''Adds in a result between a and b where true is a wins and False is b wins'''
        if result == None:
            result = [True for _ in range(self.noOfChoices)]
        if self.noOfChoices != len(result):
            raise StandardError(
                'Results list needs to be noOfChoices in length')
        for i in range(self.noOfChoices):
            self.acjs[i].comp(pair, result[i], update, reviewer, time)
        if self.logPath != None:
            self.log(self.logPath, pair, result, reviewer, time)

    def IDComp(self, idPair, result=None, update=None, reviewer='Unknown',
               time=0):
        '''Adds in a result between a and b where true is a wins and False is b wins. Uses IDs'''
        pair = []
        for p in idPair:
            pair.append(self.getScript(p))
        self.comp(pair, result, update, reviewer, time)

    def rankings(self, value=True):
        '''Returns current rankings
        Default is by value but score can be used'''
        rank = []
        for acj in self.acjs:
            rank.append(acj.rankings(value))
        return rank

    def reliability(self):
        '''Calculates reliability'''
        rel = []
        for acj in self.acjs:
            rel.append(acj.reliability()[0])
        return rel

    def log(self, path, pair, result, reviewer='Unknown', time=0):
        '''Writes out a log of a comparison'''
        timestamp = datetime.datetime.now().strftime('_%Y_%m_%d_%H_%M_%S_%f')
        with open(path + os.sep + str(reviewer) + timestamp + ".log",
                  'w+') as file:
            file.write("Reviewer:%s\n" % str(reviewer))
            file.write("A:%s\n" % str(pair[0]))
            file.write("B:%s\n" % str(pair[1]))
            for i in range(len(result)):
                file.write("Winner of %s:%s\n" % (
                self.optionNames[i], "A" if result[i] else "B"))
            file.write("Time:%s\n" % str(time))

    def JSONLog(self):
        '''Write acjs states to JSON files'''
        for acj in self.acjs:
            acj.JSONLog()

    def percentReturned(self):
        return self.acjs[0].percentReturned()

    def results(self):
        '''Prints a list of scripts and thier value scaled between 0 and 100'''
        rank = []
        for r in self.rankings():
            rank.append(list(zip(r[0], (r[1] - r[1].min()) * 100 / (
                        r[1].max() - r[1].min()))))
        return rank

    def decisionCount(self, reviewer):
        return self.acjs[0].decisionCount(reviewer)


class UniACJ(object):
    '''Base object to hold comparison data and run algorithm
        script is used to refer to anything that is being ranked with ACJ
        Dat is an array to hold the scripts with rows being [id, script, score, quality, trials]
        Track is an array with each value representing number of times a winner (dim 0) has beaten the loser (dim 1)
        Decisions keeps track of all the descisions madein descision objects
    '''

    def __init__(self, data, maxRounds, logPath=None, optionNames=None):
        self.reviewers = []
        self.optionNames = optionNames
        self.noOfChoices = 1
        self.round = 0
        self.maxRounds = maxRounds
        self.update = False
        self.data = list(data)
        self.dat = np.zeros((5, len(data)))
        self.dat[0] = np.asarray(range(len(data)))
        # self.dat[1] = np.asarray(data)
        # self.dat[2] = np.zeros(len(data), dtype=float)
        # self.dat[3] = np.zeros(len(data), dtype=float)
        # self.dat[4] = np.zeros(len(data), dtype=float)
        self.track = np.zeros((len(data), len(data)))
        self.n = len(data)
        self.swis = 5
        self.roundList = []
        self.unservedRoundList = []
        self.step = -1
        self.decay = 1
        self.returned = []
        self.logPath = logPath
        self.decisions = []
        self.comparisonsMade = 0

    def nextRound(self, extRoundList=None):
        '''Returns next round of pairs'''
        # print(f"Round: {self.round}")
        self.round = self.round + 1
        self.step = 0
        if self.round > self.maxRounds:
            self.maxRounds = self.round
        # print(self.round)
        if self.round > 1:
            self.updateAll()
        if extRoundList == None:
            self.roundList = self.infoPairs()
        else:
            self.roundList = extRoundList
        self.unservedRoundList = self.roundList.copy()
        self.returned = [False for i in range(len(self.roundList))]
        return self.roundList

    def polittNextRound(self):
        self.round = self.round + 1
        if self.round > self.maxRounds:
            self.roundList = None
        elif self.round < 2:
            self.roundList = self.randomPairs()
        elif self.round < 2 + self.swis:
            self.updateAll()
            self.roundList = self.scorePairs()
        else:
            # if self.round == 1+swis:
            # self.dat[3] = (1/self.dat[1].size)*self.dat[2][:]
            self.updateAll()
            self.roundList = self.valuePairs()
        return self.roundList
        # return self.scorePairs()

    def getID(self, script):
        '''Gets ID of script'''
        return self.data.index(script)

    def getScript(self, ID):
        '''Gets script with ID'''
        return self.data[ID]

    def nextPair(self, startNext=True):
        '''Returns next pair. Will start new rounds automatically if startNext is true'''
        self.step = self.step + 1
        if self.step >= len(self.roundList):
            if all(self.returned):
                if (startNext):
                    self.nextRound()
                    # self.polittNextRound()
                    if self.roundList == None or self.roundList == []:
                        return None
                else:
                    return -1
            else:
                o = [p for p in self.roundList if
                     not self.returned[self.roundList.index(p)]]
                return random.choice(o)
        self.unservedRoundList[self.step] = None
        return self.roundList[self.step]

    def nextIDPair(self, startNext=True):
        '''Returns ID of next pair'''
        pair = self.nextPair()
        if pair == None:
            return None
        idPair = []
        for p in pair:
            idPair.append(self.getID(p))
        return idPair

    def singleProb(self, iA, iB):
        prob = np.exp(self.dat[3][iA] - self.dat[3][iB]) / (
                    1 + np.exp(self.dat[3][iA] - self.dat[3][iB]))
        return prob

    def prob(self, iA):
        '''Returns a numpy array of the probability of A beating other values
        Based on the Bradley-Terry-Luce model (Bradley and Terry 1952; Luce 1959)'''
        probs = np.exp(self.dat[3][iA] - self.dat[3]) / (
                    1 + np.exp(self.dat[3][iA] - self.dat[3]))
        return probs

    def fullProb(self):
        '''Returns a 2D array of all probabilities of x beating y'''
        pr = np.zeros((self.n, self.n))
        for i in range(self.n):
            pr[i] = self.dat[3][i]
        return np.exp(pr - self.dat[3]) / (1 + np.exp(pr - self.dat[3]))

    def fisher(self):
        '''returns fisher info array'''
        prob = self.fullProb()
        return ((prob ** 2) * (1 - prob) ** 2) + (
                    (prob.T ** 2) * (1 - prob.T) ** 2)

    def selectionArray(self):
        '''Returns a selection array based on Progressive Adaptive Comparitive Judgement
        Politt(2012) + Barrada, Olea, Ponsoda, and Abad (2010)'''
        F = self.fisher() * np.logical_not(np.identity(self.n))
        ran = np.random.rand(self.n, self.n) * np.max(F)
        a = 0
        b = 0
        # Create array from fisher mixed with noise
        for i in range(1, self.round + 1):
            a = a + (i - 1) ** self.decay
        for i in range(1, self.maxRounds + 1):
            b = b + (i - 1) ** self.decay
        W = a / b
        S = ((1 - W) * ran) + (W * F)
        # Remove i=j and already compared scripts
        return S * np.logical_not(np.identity(self.n)) * np.logical_not(
            self.track + self.track.T)

    def updateValue(self, iA):
        '''Updates the value of script A using Newton's Method'''
        iA = int(iA)
        scoreA = self.dat[2][iA]
        valA = self.dat[3][iA]
        probA = self.prob(iA)
        x = np.sum(probA) - 0.5  # Subtract where i = a
        y = np.sum(probA * (1 - probA)) - 0.25  # Subtract where i = a
        if x == 0:
            exit()
        # print(self.dat[3])
        return self.dat[3][iA] + ((self.dat[2][iA] - x) / y)
        # print(self.dat[3][iA])
        # print("--------")

    def updateAll(self):
        '''Updates the value of all scripts using Newton's Method'''
        newDat = np.zeros(self.dat[3].size)
        for i in self.dat[0]:
            i = int(i)
            newDat[i] = self.updateValue(i)
        self.dat[3] = newDat[:]

    def randomPairs(self, dat=None):
        '''Returns a list of random pairs from dat'''
        if dat == None:
            dat = self.data
        shufDat = np.array(dat, copy=True)
        ranPairs = []
        while len(shufDat) > 1:
            a = shufDat[0]
            b = shufDat[1]
            shufDat = shufDat[2:]
            ranPairs.append([a, b])
        return ranPairs

    def scorePairs(self, dat=None, scores=None):
        '''Returns random pairs with matching scores or close if no match'''
        if dat == None:
            dat = self.dat
        shuf = np.array(dat[:3], copy=True)
        np.random.shuffle(shuf.T)
        shuf.T
        shuf = shuf[:, np.argsort(shuf[2])]
        pairs = []
        i = 0

        # Pairs matching scores
        while i < (shuf[0].size - 1):
            aID = shuf[0][i]
            bID = shuf[0][i + 1]
            if (self.track[aID][bID] + self.track[bID][aID]) == 0 and shuf[2][
                i] == shuf[2][i + 1]:
                pairs.append(
                    [self.data[shuf[0][i]], self.data[shuf[0][i + 1]]])
                shuf = np.delete(shuf, [i, i + 1], 1)
            else:
                i = i + 1

        # Add on closest score couplings of unmatched scores
        i = 0
        while i < shuf[0].size - 1:
            aID = shuf[0][i]
            j = i + 1
            while j < shuf[0].size:
                bID = shuf[0][j]
                if (self.track[aID][bID] + self.track[bID][aID]) == 0:
                    pairs.append(
                        [self.data[shuf[0][i]], self.data[shuf[0][j]]])
                    shuf = np.delete(shuf, [i, j], 1)
                    break
                else:
                    j = j + 1
                if j == shuf[0].size:
                    i = i + 1

        return pairs

    def valuePairs(self):
        '''Returns pairs matched by close values Politt(2012)'''
        shuf = np.array(self.dat,
                        copy=True)  # Transpose to shuffle columns rather than rows
        np.random.shuffle(shuf.T)
        shuf.T
        pairs = []
        i = 0
        while i < shuf[0].size - 1:
            aID = shuf[0][i]
            newShuf = shuf[:, np.argsort(np.abs(shuf[3] - shuf[3][i]))]
            j = 0
            while j < newShuf[0].size:
                bID = newShuf[0][j]
                if (self.track[aID][bID] + self.track[bID][aID]) == 0 and \
                        self.data[aID] != self.data[bID]:
                    pairs.append(
                        [self.data[shuf[0][i]], self.data[newShuf[0][j]]])
                    iJ = np.where(shuf[0] == newShuf[0][j])[0][0]
                    shuf = np.delete(shuf, [i, iJ], 1)
                    break
                else:
                    j = j + 1
                if j == shuf[0].size:
                    i = i + 1
        return pairs

    def infoPairs(self):
        '''Returns pairs based on selection array from Progressive Adaptive Comparitive Judgement
        Politt(2012) + Barrada, Olea, Ponsoda, and Abad (2010)'''
        pairs = []
        # Create
        sA = self.selectionArray()
        while (np.max(sA) > 0):
            iA, iB = np.unravel_index(sA.argmax(), sA.shape)
            pairs.append([self.data[iA], self.data[iB]])
            sA[iA, :] = 0
            sA[iB, :] = 0
            sA[:, iA] = 0
            sA[:, iB] = 0
        return pairs

    def rmse(self):
        '''Calculate rmse'''
        prob = self.fullProb()
        y = 1 / np.sqrt(np.sum(prob * (1 - prob), axis=1) - 0.25)
        return np.sqrt(np.mean(np.square(y)))

    def trueSD(self):
        '''Calculate true standard deviation'''
        sd = np.std(self.dat[3])
        return ((sd ** 2) / (self.rmse() ** 2)) ** (0.5)

    def reliability(self):
        '''Calculates reliability'''
        G = self.trueSD() / self.rmse()
        return [(G ** 2) / (1 + (G ** 2))]

    def SR(self, pair, result):
        '''Calculates the Squared Residual and weight of a decision'''
        p = [self.getID(a) for a in pair]
        if result:
            prob = self.singleProb(p[0], p[1])
        else:
            prob = self.singleProb(p[1], p[0])
        res = 1 - prob
        weight = prob * (1 - prob)

        SR = (res ** 2)
        return SR, weight

    def addDecision(self, pair, result, reviewer, time=0):
        '''Adds an SSR to the SSR array'''
        self.decisions.append(Decision(pair, result, reviewer, time))
        self.comparisonsMade += 1

    def revID(self, reviewer):
        return self.reviewers.index(reviewer)

    def WMS(self, decisions=None):
        '''Builds data lists:
        [reviewer] [sum of SR, sum of weights]
        and uses it to make dict reviewer: WMS
        WMS = Sum SR/Sum weights
        also returns mean and std div'''
        if decisions == None:
            decisions = self.decisions
        self.reviewers = []
        SRs = []
        weights = []
        for dec in decisions:
            if dec.reviewer not in self.reviewers:
                self.reviewers.append(dec.reviewer)
                SRs.append(0)
                weights.append(0)
            SR, weight = self.SR(dec.pair, dec.result)
            revID = self.reviewers.index(dec.reviewer)
            SRs[revID] = SRs[revID] + SR
            weights[revID] = weights[revID] + weight

        WMSs = []
        WMSDict = {}
        for i in range(len(self.reviewers)):
            WMS = SRs[i] / weights[i]
            WMSs.append(WMS)
            WMSDict[self.reviewers[i]] = WMS
        return WMSDict, np.mean(WMSs), np.std(WMSs)

    def comp(self, pair, result=True, update=None, reviewer='Unknown', time=0):
        '''Adds in a result between a and b where true is a wins and False is b wins'''
        self.addDecision(pair, result, reviewer, time)
        if pair[::-1] in self.roundList:
            pair = pair[::-1]
            result = not result
        if pair in self.roundList:
            self.returned[self.roundList.index(pair)] = True
        a = pair[0]
        b = pair[1]
        if update == None:
            update = self.update
        iA = self.data.index(a)
        iB = self.data.index(b)
        if result:
            self.track[iA, iB] = 1
            self.track[iB, iA] = 0
        else:
            self.track[iA, iB] = 0
            self.track[iB, iA] = 1
        self.dat[2, iA] = np.sum(self.track[iA, :])
        self.dat[2, iB] = np.sum(self.track[iB, :])
        self.dat[4, iA] = self.dat[4][iA] + 1
        self.dat[4, iB] = self.dat[4][iB] + 1
        if self.logPath != None:
            self.log(self.logPath, pair, result, reviewer, time)

    def IDComp(self, idPair, result=True, update=None, reviewer='Unknown',
               time=0):
        '''Adds in a result between a and b where true is a wins and False is b wins, Uses IDs'''
        pair = []
        for p in idPair:
            pair.append(self.getScript(p))
        self.comp(pair, result, update, reviewer, time)

    def percentReturned(self):
        if len(self.returned) == 0:
            return 0
        return (sum(self.returned) / len(self.returned)) * 100

    def log(self, path, pair, result, reviewer='Unknown', time=0):
        '''Writes out a log of a comparison'''
        timestamp = datetime.datetime.now().strftime('_%Y_%m_%d_%H_%M_%S_%f')
        comparisonDict = {"Reviewer": reviewer,
                          "Winner": (pair[0] if result else pair[1]),
                          "Loser": (pair[1] if result else pair[0]),
                          "Time": time}
        with open(path + os.sep + str(reviewer) + timestamp + ".log",
                  'w+') as file:
            json.dump(comparisonDict, file, indent=4)


        """timestamp = datetime.datetime.now().strftime('_%Y_%m_%d_%H_%M_%S_%f')
        with open(path + os.sep + str(reviewer) + timestamp + ".log",
                  'w+') as file:
            file.write("Reviewer:%s\n" % str(reviewer))
            file.write("A:%s\n" % str(pair[0]))
            file.write("B:%s\n" % str(pair[1]))
            file.write("Winner:%s\n" % ("A" if result else "B"))
            file.write("Time:%s\n" % str(time))"""

    def JSONLog(self, path=None):
        '''Writes out a JSON containing data from ACJ'''
        if path == None:
            path = self.logPath
        choice = self.optionNames[0].replace(" ", "_")
        ACJDict = {"Criteria": choice, "Scripts": self.scriptDict(),
                   "Reviewers": self.reviewerDict(),
                   "Decisions": self.decisionList()}
        with open(path + os.sep + "ACJ_" + choice + ".json", 'w+') as file:
            json.dump(ACJDict, file, indent=4)

    def decisionCount(self, reviewer):
        c = 0
        for dec in self.decisions:
            if (dec.reviewer == reviewer):
                c = c + 1
        return c

    def reviewerDict(self):
        revs = {}
        WMSs, _, _ = self.WMS()
        for rev in self.reviewers:
            revDict = {'decisions': self.decisionCount(rev), 'WMS': WMSs[rev]}
            revs[str(rev)] = revDict
        print(len(revs))
        return revs

    def scriptDict(self):
        scr = {}
        r = self.results()[0]
        for i in range(len(r)):
            scrDict = {"Score": r[i][1]}
            scr[str(r[i][0])] = scrDict
        return scr

    def decisionList(self):
        dec = []
        for d in self.decisions:
            dec.append(d.dict())
        return dec

    def rankings(self, value=True):
        '''Returns current rankings
        Default is by value but score can be used'''
        if value:
            return [np.asarray(self.data)[np.argsort(self.dat[3])],
                    self.dat[3][np.argsort(self.dat[3])]]
        else:
            return self.data[np.argsort(self.dat[2])]

    def results(self):
        '''Prints a list of scripts and thier value scaled between 0 and 100'''
        r = self.rankings()
        rank = list(
            zip(r[0], (r[1] - r[1].min()) * 100 / (r[1].max() - r[1].min())))
        return [rank]

    def getComparisonsMade(self):
        return self.comparisonsMade
