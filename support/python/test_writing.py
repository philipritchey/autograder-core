from attributes import Attributes
from test_types import UnsupportedTestException

def write_unit_test(test: Attributes) -> None:
    with open('UnitTest.py', 'wt') as f:
        f.write('import unittest\n')
        f.write('from ' + test['target'][:-3] + ' import *\n')

        if 'include' in test.keys():
            if len(test['include']) > 0:
                for include in test['include'].split():
                    f.write('from ' + include + ' import *\n')

        f.write('class UnitTest(unittest.TestCase):\n')
        f.write('    def test_1(self):\n')
        lines = test['code'].split('\n')
        for l in lines:
            f.write('        ' + l + '\n')
        f.write("if __name__ == '__main__':\n")
        f.write('    unittest.main()\n\n')


# Writes out the input and output strings
def write_io_test(test: Attributes) -> None:
    with open('input.txt', 'wt') as f:
        f.write(test['expected_input'])
        f.write("\n")
    with open('output.txt', 'wt') as f:
        f.write(test['expected_output'])

def write_script_test(test: Attributes) -> None:
    with open('script.sh', 'wt') as f:
        f.write(test['script_content'])

def write_test(test: Attributes) -> None:
    if test['type'] == 'unit':
        write_unit_test(test)
    elif test['type'] == 'i/o':
        write_io_test(test)
    elif test['type'] == 'script':
        write_script_test(test)
    else:
        # don't try to write an unsupported test
        raise UnsupportedTestException(test['type'])