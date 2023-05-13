BEGIN_TEST_DELIMITER = '<test>'
END_TEST_DELIMITER = '</test>'
EMPTY_TEST_BLOCK = '<test/>'

DEFAULT_POINTS = 0.0
DEFAULT_TIMEOUT = 10.0
DEFAULT_SHOW_OUTPUT = 'false'
DEFAULT_NUMBER = ''
DEFAULT_TARGET = ''
DEFAULT_VISIBILITY = 'visible'
DEFAULT_STDOUT_VISIBILITY = 'visible'

TIMEOUT_MSSG = 'Timeout during test execution, check for an infinite loop\n'
OCTOTHORPE_LINE = '#'*27
OCTOTHORPE_WALL = '#'+' '*25+'#'
INFO_UNSUPPORTED_TEST = '[INFO] Unsupported Test'

# cpp compilation config
CXX = 'g++'
CXX_FLAGS = '-std=c++17 -g'

# java compilation config
JAVA_CLASSPATH = ".:./lib/hamcrest-2.2.jar:./lib/junit-4.13.2.jar"
JAVAC = 'javac'
JAVA_FLAGS = '-Xlint -g -cp ' + JAVA_CLASSPATH