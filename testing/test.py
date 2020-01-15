import unittest

class Template(unittest.TestCase):

    def setUp(self):
        pass

    def test_basic(self):
        self.assertTrue(True)
        self.assertFalse(False)

    def tearDown(self):
        pass
