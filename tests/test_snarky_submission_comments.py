"""
tests for snarky_comment_about_number_of_submissions 
"""
import unittest

from snarky_submission_comments import snarky_comment_about_number_of_submissions

class TestSnarkyComments(unittest.TestCase):
    """
    tests for snarky_comment_about_number_of_submissions 
    """
    def test_snarky_comments(self):
        """
        tests for snarky_comment_about_number_of_submissions 
        """
        self.assertTrue(snarky_comment_about_number_of_submissions(1).startswith('That\'s OK.'))
        self.assertTrue(snarky_comment_about_number_of_submissions(3).startswith('That\'s OK.'))
        self.assertTrue(
            snarky_comment_about_number_of_submissions(4).startswith('You should take some time'))
        self.assertEqual(
            snarky_comment_about_number_of_submissions(99),
            'Your number of submissions to this assignment is too damn high.\n'
            )
        self.assertEqual(
            snarky_comment_about_number_of_submissions(100),
            'I\'m not even mad, that\'s amazing.\n'
        )
