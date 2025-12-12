'''
Constants that are more-or-less configurable.
'''

# delimiters
BEGIN_MULTILINE_COMMENT_DELIMITER = '/*'
END_MULTILINE_COMMENT_DELIMITER = '*/'
BEGIN_TEST_DELIMITER = '<test>'
END_TEST_DELIMITER = '</test>'
EMPTY_TEST_BLOCK = '<test/>'

# visibility options
# hidden: test case will never be shown to students
# after_due_date: test case will be shown after the assignment's due date has passed. If late
#                 submission is allowed, then test will be shown only after the late due date.
# after_published: test case will be shown only when the assignment is explicitly published from
#                  the "Review Grades" page
# visible: test case will always be shown
HIDDEN = 'hidden'
AFTER_DUE_DATE = 'after_due_date'
AFTER_PUBLISHED = 'after_published'
VISIBLE = 'visible'
VISIBILITY_OPTIONS = [HIDDEN, AFTER_DUE_DATE, AFTER_PUBLISHED, VISIBLE]

# defaults
DEFAULT_POINTS = 0.0
DEFAULT_TIMEOUT = 10.0
DEFAULT_SHOW_OUTPUT = 'false'
DEFAULT_NUMBER = ''
DEFAULT_TARGET = ''
DEFAULT_VISIBILITY = VISIBLE
DEFAULT_STDOUT_VISIBILITY = VISIBLE

# output
TIMEOUT_MSSG = 'Timeout during test execution\n'
OCTOTHORPE_LINE = '#'*27
OCTOTHORPE_WALL = '#'+' '*25+'#'
INFO_UNSUPPORTED_TEST = '[INFO] Unsupported Test'

# snarky comment control
SNARKY_SUBMISSION_SCORE_THRESHHOLD = 0.9  # be snarky when score < 90%

# cpp compilation config
CXX = 'g++'
CXX_FLAGS = '-std=c++23 -g'

# java compilation config
JAVA_CLASSPATH = ".:./lib/hamcrest-2.2.jar:./lib/junit-4.13.2.jar"
JAVAC = 'javac'
JAVA_FLAGS = '-Xlint -g -cp ' + JAVA_CLASSPATH
