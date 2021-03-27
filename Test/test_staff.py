from unittest import TestCase

import unittest
from staff import Staff


class MyTestCase(unittest.TestCase):
    def test_get_work_years(self):  # test the method get_work_years() in Staff object
        # Behaviour Driven Development (BDD) example
        # Given - setup
        staff = Staff()
        staff.set_start_year("2011")

        # When
        result = staff.get_work_years()

        # Then
        self.assertEqual(result, 10)  # pass
        # self.assertNotEqual(result, 20)  # pass
        # self.assertEqual(result, 20)  # failed


if __name__ == '__main__':
    unittest.main()

