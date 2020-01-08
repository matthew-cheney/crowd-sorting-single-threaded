"""
An implementation of the 'Discrete Adiabatic' Monte Carlo Sorting Algorithm
    (Smith 2016)

Algorithm citation: https://arxiv.org/pdf/1612.08555.pdf
"""
import json
import os

"""
TO DO:
Make all internal calculations based on the ID, NOT the name of each script
"""


import random
from copy import copy, deepcopy
import datetime
import collections
from pprint import pprint


class MonteCarlo:

    def __init__(self, data, p=.999, N=None, epsilon=1, per_round=25, logPath=None):
        self.original_data = data  # Data (scripts to be sorted) as entered
        self.data_dictionary = dict(zip(range(len(data)), data))
        self.data = list(self.data_dictionary.keys())  # Keys are now ids
        data = data
        if p <= 0:
            p = .001
        self.p = p
        self.prob = (1 - self.p) / self.p
        self.length = len(self.data)
        if N is None:
            N = len(data) // 2  # Come back to this number, it's probably bad
        self.N = N  # Candidate lists
        self.N_array = dict(list())
        self.N_dictionaries = {x: dict() for x in range(0, len(self.N_array))}
        self.all_same = False
        self.data_n_disputes = {x: 0 for x in self.data}
        self.data_i_have_beaten = {x: set() for x in self.data}
        self.epsilon = epsilon  # 0 < epsilon << 1, lower is more accurate
        self.per_round = per_round
        for i in range(N):
            success = False
            while not success:
                new_list = random.sample(self.data, len(self.data))
                success = True
                for each in self.N_array:
                    if new_list == self.N_array[each]:
                        success = False
            self.N_array[i] = new_list
        self.N_changed = [True for x in self.N_array]
        self._N_array_to_dictionary()
        self.comparisons_made = 0
        self.logPath = logPath

    def next_pair(self, allDocs):
        allDocs_IDs = [self.get_ID(x) for x in allDocs]
        self._N_array_to_dictionary()
        return self._get_ij(allDocs_IDs)

    def _get_ij(self, allDocs_IDs):
        uncertain_list = []
        min_Nij_minus_Nji = 999999999999999999  # There's probably a more elegant way of doing this
        for i in self.data:
            for j in self.data:
                if i == j:
                    continue
                if i not in allDocs_IDs:
                    continue
                if j not in allDocs_IDs:
                    continue
                new_min = self._get_Nij_minus_Nji(i, j)
                if new_min < min_Nij_minus_Nji:
                    min_Nij_minus_Nji = new_min
                    uncertain_list = []
                if new_min == min_Nij_minus_Nji:
                    uncertain_list.append((i, j))
        try:
            if len(uncertain_list) == 0:
                return None
            else:
                indexer = random.randint(0, len(uncertain_list) - 1)
            pair = uncertain_list[indexer]
        except IndexError:
            print("list:", uncertain_list)
            print("indexer:", indexer)
            exit()
        return pair[0], pair[1]

    def _get_Nij_minus_Nji(self, i, j):
        Nij = 0
        Nji = 0
        for list_i, each in enumerate(self.N_array.values()):
            # if each.index(i) < each.index(j):
            if self.N_dictionaries[list_i][i] < self.N_dictionaries[list_i][j]:
                Nij += 1
            else:
                Nji += 1
        return (Nij - Nji) ** 2

    def _is_i_less_than_j(self, i, j, list_id):
        # if target_list.index(i) < target_list.index(j):
        if self.N_dictionaries[list_id][i] < self.N_dictionaries[list_id][j]:
            return True
        else:
            return False

    def get_script(self, id):
        try:
            return self.data_dictionary[id]
        except KeyError:
            return "Script not found"

    def get_ID(self, script_name):
        if script_name not in self.data_dictionary.values():
            return "Script not found"
        for key in self.data_dictionary:
            if self.data_dictionary[key] == script_name:
                return key
        return "Script not found"

    def _N_array_to_dictionary(self):
        for i, changed in enumerate(self.N_changed):
            if changed:
                self.N_dictionaries[i] = self._create_index_dictionary(deepcopy(self.N_array[i]))
                self.N_changed[i] = False

    def _create_index_dictionary(self, a_list):
        return {e: i for i, e in enumerate(a_list)}
    """
    Potentially add this for better computational efficiency:
    { e: i for i, e in enumerate(a_list) }
    """

    def compare_id(self, pair, higher, reviewer="Unknown", time="0"):
        # for higher: True = 0th higher, False = 1st higher
        self.comparisons_made += 1
        if self.logPath != None:
            self._log_comparison(self.logPath, pair, higher, reviewer, time)
        if higher:
            self._process_compare(pair[0], pair[1])
        else:
            self._process_compare(pair[1], pair[0])
        if self._check_list_unity():
            self.get_sorted_builder()
            self.all_same = True

    def _log_comparison(self, path, pair, result, reviewer='Unknown', time=0):
        '''Writes out a log of a comparison'''

        timestamp = datetime.datetime.now().strftime('_%Y_%m_%d_%H_%M_%S_%f')
        comparisonDict = {"Reviewer": reviewer,
                          "Winner": (self.data_dictionary[pair[0]] if result else self.data_dictionary[pair[1]]),
                          "Loser": (self.data_dictionary[pair[1]] if result else self.data_dictionary[pair[0]]),
                          "Time": time}
        with open(path + os.sep + str(reviewer) + timestamp + ".log",
                  'w+') as file:
            json.dump(comparisonDict, file, indent=4)



        """timestamp = datetime.datetime.now().strftime('_%Y_%m_%d_%H_%M_%S_%f')
        with open(path + os.sep + str(reviewer) + timestamp + ".log",
                  'w+') as file:
            file.write("Reviewer:%s\n" % str(reviewer))
            file.write("A:%s\n" % str(self.data_dictionary[pair[0]]))
            file.write("B:%s\n" % str(self.data_dictionary[pair[1]]))
            file.write("Winner:%s\n" % ("A" if result else "B"))
            file.write("Time:%s\n" % str(time))"""

    def _process_compare(self, higher, lower):
        # higher_name = self.get_script(higher)
        # lower_name = self.get_script(lower)

        self.data_n_disputes[lower] += 1  # 12/20 - changed higher to lower
        self.data_i_have_beaten[higher].add(lower)  # 12/20 - changed 1st lower to higher
        for list_id in self.N_array:
            if self._is_i_less_than_j(lower, higher, list_id):
                continue
            else:
                self._process_mismatch(higher, lower, list_id)

    def _process_mismatch(self, higher, lower, list_id):
        if self._decision(self.prob):
            return
        else:
            # self._max_element_sampling(higher, lower, list_id)
            self._max_element_refactored(higher, lower, list_id)
            self.N_changed[list_id] = True

    def _max_element_sampling(self, higher, lower, list_id):  # Random shuffle is placeholder - come back and flush out
        lower_index = self.N_array[list_id].index(lower)
        higher_index = self.N_array[list_id].index(higher)
        lower_list = deepcopy(self.N_array[list_id][:higher_index])
        higher_list = deepcopy(self.N_array[list_id][lower_index + 1:])
        middle_list = deepcopy(self.N_array[list_id][higher_index:lower_index + 1])
        new_list = list()
        local_n_dispute = deepcopy(self.data_n_disputes)
        tries = 0
        while len(middle_list) > 1:
            tries = 0
            # "Select a single random element e_max uniformly from the list"
            e_max = middle_list[random.randint(0, len(middle_list) - 1)]
            # Accept e_max as the largest element w/ prob: ((1 - p) / p)**n_dispute
            prob = ((1 - self.p) / self.p) ** local_n_dispute[e_max]
            if self._decision(prob):
                tries = 0
                new_list.append(e_max)
                middle_list.remove(e_max)
                for lower_dat in self.data_i_have_beaten[e_max]:
                    if lower_dat in middle_list:
                        local_n_dispute[lower_dat] -= 1
            else:
                tries += 1
                # print(f"reject: {tries}", end='\r', flush=True)
        new_list.append(middle_list[0])

        new_list.reverse()

        self.N_array[list_id] = lower_list + new_list + higher_list


        """lower_index = self.N_array[list_id].index(lower)
        higher_index = self.N_array[list_id].index(higher)
        lower_list = self.N_array[list_id][:higher_index]
        higher_list = self.N_array[list_id][lower_index + 1:]
        middle_list = self.N_array[list_id][higher_index:lower_index + 1]
        while middle_list.index(higher) < middle_list.index(lower):
            random.shuffle(middle_list)
        new_list = lower_list + middle_list + higher_list
        self.N_array[list_id] = new_list"""

    def _max_element_refactored(self, higher, lower, list_id):
        lower_index = self.N_array[list_id].index(lower)
        higher_index = self.N_array[list_id].index(higher)
        lower_list = deepcopy(self.N_array[list_id][:higher_index])
        higher_list = deepcopy(self.N_array[list_id][lower_index + 1:])
        middle_list = deepcopy(
            self.N_array[list_id][higher_index:lower_index + 1])
        new_list = list()

        while len(middle_list) > 1:
            w = 0
            i = 0
            sigma = random.random()

            beta_list = list()
            for element in middle_list:
                beta = ((1 - self.p) / self.p) ** self.data_n_disputes[element]
                beta_list.append(beta)

            Z = sum(beta_list)
            if Z == 0:
                Z = .0000000001

            accepted_element = False

            if Z == 0:
                pass

            while not accepted_element:
                if i >= len(beta_list):
                    i = 0
                gamma = beta_list[i] / Z
                if sigma < w + gamma:
                    new_list.append(middle_list[i])
                    accepted_element = True
                else:
                    w = w + gamma
                    i += 1
            middle_list.remove(middle_list[i])
        if (len(middle_list) == 1):
            new_list.append(middle_list[0])
        new_list.reverse()
        self.N_array[list_id] = lower_list + new_list + higher_list

    def _check_list_unity(self):
        if self.epsilon == 1:
            unified = True
            zero_list = self.N_array[0]
            for each in self.N_array.values():
                if not zero_list == each:
                    unified = False
                    break
            return unified
        else:
            all_lists = [tuple(x) for x in self.N_array.values()]
            counter = collections.Counter(all_lists)
            most_common_list, most_common_int = counter.most_common(1)[0]
            f = most_common_int / self.N
            if f > 1 - self.epsilon:
                return True
            else:
                return False

    def _decision(self, probability):
        return random.random() < probability

    def get_sorted(self):
        target_N = self.N_array[random.randint(0, self.N - 1)]
        toReturn = list()
        for x_id in target_N:
            toReturn.append(self.data_dictionary[x_id])
        # return self.N_array[random.randint(0, self.N - 1)]
        return toReturn

    def get_sorted_builder(self):
        # For each doc, give it score of sum of indeces across N_array
        # sorted_list is docs sorted by score
        index_dict = dict()
        for x in range(self.length):
            index_dict[x] = 0
        for N_list in self.N_array.values():
            for i, x in enumerate(N_list):
                index_dict[x] += i
        sorted_list = sorted(index_dict.items(), key=lambda kv: kv[1])
        sorted_list = [x[0] for x in sorted_list]
        toReturn = list()
        for x_id in sorted_list:
            toReturn.append(self.data_dictionary[x_id])
        basic_sorted = self.get_sorted()
        return toReturn

    def get_confidence(self):
        return 42

    def get_comparisons_made(self):
        return self.comparisons_made
