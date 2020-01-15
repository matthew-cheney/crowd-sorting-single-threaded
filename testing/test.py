import unittest
from selenium import webdriver

# PyTest

GECKO_DRIVER_PATH = '/home/matthew/ComparativeJudgment/crowd_sorting/testing/geckodriver'

class FindLink(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Firefox(executable_path=GECKO_DRIVER_PATH)

    def test_link(self):
        self.driver.get("https://micropyramid.com/")
        web_dev_link = self.driver.find_elements_by_partial_link_text(
            'Web Development')
        # Test atleast we have one link with name  "Web Development"
        self.assertIsNotNone(web_dev_link)

    def tearDown(self):
        self.driver.quit()


if __name__ == '__main__':
    unittest.main()