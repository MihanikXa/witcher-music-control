import copy
import unittest
from regional_selector_matrix import validate_groups


class MatrixControls(unittest.TestCase):
    def test_valid_long_transition_group(self):
        validate_groups([{'name':'outro','location_event':'verified_event','cases':['e-combat'],'duration':55}])

    def test_unsafe_empty_duplicate_or_short_groups_fail(self):
        good={'name':'outro','location_event':'verified_event','cases':['e-combat'],'duration':55}
        for field,value in [('name','../escape'),('duration',1),('cases',[]),('cases',['e-combat','e-combat'])]:
            row=copy.deepcopy(good);row[field]=value
            with self.assertRaises(ValueError):validate_groups([row])
        with self.assertRaises(ValueError):validate_groups([good,good])
        with self.assertRaises(ValueError):validate_groups([])
