import unittest
from manager import Manager


class TestManager(unittest.TestCase):

    def setUp(self):
        print("setUp")
        self.__manager = Manager()
        self.__manager.set_bonus(100)  # set bonus to £100
        self.__manager.set_contract(30000)  # set Contract object with pay £30000

    def test_get_total_pay(self):
        result = self.__manager.get_total_pay()
        self.assertEqual(result, 30100)

    def tearDown(self):
        print("tearDown")
        del self.__manager


if __name__ == '__main__':
    unittest.main()

