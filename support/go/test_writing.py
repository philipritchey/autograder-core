'''
Write an autograder test in Go.
'''

from attributes import Attributes
from test_types import UnsupportedTestException

def write_unit_test(test: Attributes) -> None:
    '''
    Write a unit test.

    Args:
        test (Attributes): information about the test
    '''
    # go ignores files named *_test.go
    with open('unittest.go', 'wt', encoding='utf-8') as f:
        f.write('package main\n\n')

        if test['include']:
            f.write('import (\n')
            for include in test['include'].split():
                f.write(f"\t\"{include}\"\n")
            f.write(')\n\n')

        # f.write('func main() {\n')
        # f.write('\t{}\n'.format('\n\t'.join(test['code'].splitlines())))
        # f.write('}\n')
        f.write(test['code'])

# Writes out the input and output strings
def write_io_test(test: Attributes) -> None:
    '''
    Write an io test.

    Args:
        test (Attributes): information about the test
    '''
    with open('input.txt', 'wt', encoding='utf-8') as f:
        f.write(test['expected_input'])
    with open('output.txt', 'wt', encoding='utf-8') as f:
        f.write(test['expected_output'])

def write_script_test(test: Attributes) -> None:
    '''
    Write a script test.

    Args:
        test (Attributes): information about the test
    '''
    with open('script.sh', 'wt', encoding='utf-8') as f:
        f.write(test['script_content'])

def write_approved_includes_test(test: Attributes) -> None:
    '''
    Write an approved includes test.

    Args:
        test (Attributes): information about the test
    '''
    test['script_content'] = f"./approved_includes.sh {test['target']} {' '.join(test['approved_includes'])}"
    write_script_test(test)

def write_coverage_test(test: Attributes) -> None:
    '''
    Write a coverage test.

    Args:
        test (Attributes): information about the test
    '''
    test['script_content'] = f"./coverage.sh {test['target']} {test['include']} {' '.join(test['approved_includes'])}"
    write_script_test(test)

def write_compile_test(test: Attributes) -> None:
    '''
    Write a comple test.

    Args:
        test (Attributes): information about the test
    '''
    test['script_content'] = f"./compiles.sh {' '.join(test['approved_includes'])}"
    write_script_test(test)

def write_test(test: Attributes) -> None:
    '''
    Write a test to be run by the autograder.

    Args:
        test (Attributes): details about the test to write

    Raises:
        UnsupportedTestException: If the type of test is not supported
    '''
    if test['type'] == 'unit':
        write_unit_test(test)
    elif test['type'] == 'i/o':
        write_io_test(test)
    elif test['type'] == 'approved_includes':
        write_approved_includes_test(test)
    elif test['type'] == 'coverage':
        write_coverage_test(test)
    elif test['type'] == 'compile':
        write_compile_test(test)
    elif test['type'] == 'script':
        write_script_test(test)
    else:
        # don't try to write an unsupported test
        raise UnsupportedTestException(test['type'])
