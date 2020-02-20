import unittest

from crowdsorting.app_resources.sorting_algorithms.ACJProxy import ACJProxy

class ACJ_Proxy_Tester(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_ACJProxy(self):
        acjp1 = ACJProxy('project one')
        data = ['a' for x in range(20)]
        acjp1.initialize_selector(data)

"""
To test:

Creating and removing logs
Number of judgments needed
    Incl. out of order judgments

"""

