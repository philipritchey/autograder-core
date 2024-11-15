'''
configuration for snarky comments about the number of submissions
'''

# the comment to make when the number of submissions exceeds all threshholds
ULTIMATE_COMMENT = "I'm not even mad, that's amazing."

# try to keep this in increasing order of threshhold
# but if you mess it up, there is a sort at the end which will fix it for you
SNARKY_SUBMISSION_COMMENTS = [
    # upper submission threshhold, comment
    (
        4,
        ("That's OK.  Make sure that you reflect on the feedback and think before you code.  "
         "Before making another submission, write test cases to reproduce the errors and then "
         "use your favorite debugging technique to isolate and fix the errors.  You can do it!")
    ),
    (
        7,
        ("You should take some time before your next submission to think about the errors and "
         "how to fix them.  Start by reproducing the errors with test cases locally.")
    ),
    (
        10,
        ("Why don't you take a break, take a walk, take nap, and come back to this "
         "after you've had a chance to think a bit more.  "
         "Remember: start by reproducing the error, then isolate it and fix it.")
    ),
    (
        15,
        ("It looks like you're having difficulty finding and fixing your errors.  "
         "You should come to office hours.  We can help you.")
    ),
    (
        20,
        ("If you haven't gone to office hours yet, you really should.  "
         "We want to help you.  How's your coverage?  You can't test what you don't cover.")
    ),
    (
        30,
        ("Did you know that you can not only compile locally, but you can also test locally?  "
         "You should try it.")
    ),
    (
        40,
        ("literally nobody: \n"
         "             you: autograder go brrr.")
    ),
    (
        50,
        ("I'm almost out of snarky ways to comment on how many submissions you've made.  "
         "That's how many submissions you've made.")
    ),
    (
        75,
        ("Big yikes.  No cap, fam, take several seats.  This ain't it, chief.  "
         "Your code and development process are sus AF.  Periodt.")
    ),
    (
        100,
        "Your number of submissions to this assignment is too damn high."
    )
    ]

# sort the entries by ascending threshhold (just in case)
SNARKY_SUBMISSION_COMMENTS.sort(key=lambda t : t[0])

def snarky_comment_about_number_of_submissions(num_submissions: int) -> str:
    """make a snarky comment based on their number of submissions

    Args:
        num_submissions (int): the number of submissions (i.e. the number of this submission)

    Returns:
        str: a (snarky) comment about the number of submissions
    """
    for submission_threshhold, comment in SNARKY_SUBMISSION_COMMENTS:
        if num_submissions < submission_threshhold:
            return comment + '\n'
    return ULTIMATE_COMMENT + '\n'
