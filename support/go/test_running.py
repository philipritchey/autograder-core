'''
methods for running tests for go programs
'''

import subprocess
from os import remove
from os.path import exists as path_exists
from time import time
import difflib

from attributes import Attributes
from results import PartialTestResult
from config import TIMEOUT_MSSG
from test_types import UnsupportedTestException

def communicate_with_subprocess(p: subprocess.Popen[bytes], timeout: float, input_data: str = '') -> tuple[str, str]:
    '''
    Send input to a subprocess through stdin and get stdout and stderr.

    Args:
        p (subprocess.Popen[bytes]): subprocess with which to communicate
        timeout (float): time limit on subprocess
        input_data (str, optional): data to send. Defaults to ''.

    Returns:
        tuple[str, str]: contents of stdout, stderr
    '''
    output, error = p.communicate(input_data.encode('utf-8'), timeout=timeout)
    return (
        output.decode(encoding = 'utf-8', errors = 'backslashreplace'),
        error.decode(encoding = 'utf-8', errors = 'backslashreplace')
    )

def run_unit_test(timeout: float, targets: str) -> tuple[bool,str]:
    '''
    run a unit test

    Args:
        timeout (float): how long to wait before the test times out

    Returns:
        tuple[bool,str]: exited-with-code-0, output
    '''
    try:
        result = subprocess.run(['go', 'test', 'unittest.go'] + targets.split(' '), capture_output=True, text=False, check=True, timeout=timeout)
    except subprocess.CalledProcessError as err:
        # non-zero exit code
        output = err.stdout.decode(encoding = 'utf-8', errors = 'backslashreplace')
        error = err.stderr.decode(encoding = 'utf-8', errors = 'backslashreplace')
        ret = err.returncode
        if ret not in (0, 1):
            error += '\n' + f"Program exited with status {ret}."
        return False, output + '\n' + error
    except subprocess.TimeoutExpired:
        return False, TIMEOUT_MSSG

    output = result.stdout.decode(encoding = 'utf-8', errors = 'backslashreplace')
    error = result.stderr.decode(encoding = 'utf-8', errors = 'backslashreplace')
    return True, output

def remove_end_of_line_whitespace(s: str) -> str:
    '''
    remove whitespace from the end of a line (or lines).
    turns "hello  \n world \n" -> "hello\n world\n"

    Args:
        s (str): line(s) from which to remove end of line whitespace

    Returns:
        str: line without end of line whitespace
    '''
    lines = s.split('\n')
    lines = [line.rstrip() for line in lines]
    return '\n'.join(lines)

def run_io_test(timeout: float) -> tuple[bool,str]:
    '''
    run an i/o test.

    Args:
        timeout (float): how long to wait before test times out

    Returns:
        tuple[bool,str]: exited-with-code-0, output
    '''
    with open('input.txt', 'r', encoding='utf-8') as file:
        input_data = file.read()
    try:
        result = subprocess.run(
            ['./io_test'],
            input=input_data.encode('utf-8'),
            capture_output=True,
            text=False,
            check=True,
            timeout=timeout)
    except subprocess.CalledProcessError as err:
        # non-zero exit code
        output = err.stdout.decode(encoding = 'utf-8', errors = 'backslashreplace')
        error = err.stderr.decode(encoding = 'utf-8', errors = 'backslashreplace')
        ret = err.returncode
        if ret not in (0, 1):
            error += '\n' + f"Program exited with status {ret}."
        return False, output + '\n' + error
    except subprocess.TimeoutExpired as err:
        # why does TimeoutExpired allow stdout and stderr to be None?!
        if err.stdout is None:
            err.stdout = b''
        if err.stderr is None:
            err.stderr = b''
        output = err.stdout.decode(encoding = 'utf-8', errors = 'backslashreplace')
        error = err.stderr.decode(encoding = 'utf-8', errors = 'backslashreplace')
        return False, output + '\n' + error + '\n' + TIMEOUT_MSSG

    output = result.stdout.decode(encoding = 'utf-8', errors = 'backslashreplace')
    error = result.stderr.decode(encoding = 'utf-8', errors = 'backslashreplace')

    with open('output.txt', 'r', encoding='utf-8') as file:
        reference_output = file.read()

    if output == reference_output:
        return True, 'Actual output matches expected output.'
    diff = ''.join(difflib.Differ().compare(reference_output.splitlines(True), output.splitlines(True)))
    return False, f"Actual output differs from expected output.\n\nThe input:\n{input_data}\n\nThe differences between expected and actual:\n{diff}\n\n"

def run_script_test(timeout: float, args: str = '') -> tuple[bool,str,float]:
    '''
    run a scripted test.

    Args:
        timeout (float): how long to wait before test times out
        args (str, optional): arguments to script, if any. Defaults to ''.

    Returns:
        tuple[bool,str,float]: exited-with-code-0, output, score
    '''

    if path_exists('./DEBUG'):
        remove('./DEBUG')
    if path_exists('./OUTPUT'):
        remove('./OUTPUT')

    cmd = f'bash ./script.sh {args}'
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, shell=True)
    score = 0.0
    debug_string = ""
    output_string = "0"
    try:
        _, _ = p.communicate(timeout=timeout)

        if path_exists('./OUTPUT'):
            with open('./OUTPUT', 'r', encoding='utf-8', errors = 'backslashreplace') as file:
                output_string = file.read()
        else:
            print('[FATAL]: OUTPUT does not exist.')
            return False, "test failed to run", 0

        if path_exists('./DEBUG'):
            with open('./DEBUG', 'r', encoding='utf-8', errors = 'backslashreplace') as file:
                debug_string = "Debug:\n" + file.read()

        score = float(output_string)
    except subprocess.TimeoutExpired:
        debug_string = TIMEOUT_MSSG

    return (score > 0.0), debug_string, score

def run_approved_includes_test(timeout: float) -> tuple[bool,str,float]:
    return run_script_test(timeout)

def run_coverage_test(timeout: float) -> tuple[bool,str,float]:
    return run_script_test(timeout)

def run_compile_test(timeout: float) -> tuple[bool,str,float]:
    return run_script_test(timeout)

def run_test(test: Attributes) -> PartialTestResult:
    max_points = float(test['points'])
    runs = True
    point_multiplier = 100.0
    unapproved_includes = False
    sufficient_coverage = True
    timeout = float(test['timeout'])
    time_start = time()
    if test['type'] == 'unit':
        runs, run_output = run_unit_test(timeout, test['target'])
    elif test['type'] == 'i/o':
        runs, run_output = run_io_test(timeout)
    elif test['type'] == 'script':
        runs, run_output, point_multiplier = run_script_test(timeout, test['script_args'])
    elif test['type'] == 'approved_includes':
        runs, run_output, point_multiplier = run_approved_includes_test(timeout)
        if not runs:
            unapproved_includes = True
    elif test['type'] == 'coverage':
        runs, run_output, point_multiplier = run_coverage_test(timeout)
        if not runs:
            sufficient_coverage = False
    elif test['type'] == 'compile':
        runs, run_output, point_multiplier = run_compile_test(timeout)
    else:
        # don't try to run an unsupported test
        raise UnsupportedTestException(test['type'])
    time_end = time()
    run_time = time_end - time_start

    if runs:
        if point_multiplier < 100.0:
            print(f"[PARTIAL PASS] ran partially correct and recieved {point_multiplier:0.2f}% partial credit\n")
        else:
            print('[PASS] ran correctly\n')
        points = max_points * (point_multiplier / 100.0)
    else:
        if point_multiplier < 0:
            # this is a penalty -> deduct points
            print('[FAIL] penalty applied\n')
            points = point_multiplier
        else:
            print('[FAIL] incorrect behavior\n')
            points = 0

    result: PartialTestResult = {
        'run_output': run_output,
        'unapproved_includes': unapproved_includes,
        'sufficient_coverage': sufficient_coverage,
        'points': points,
        'run_time': run_time
    }
    return result
