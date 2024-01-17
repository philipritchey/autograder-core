from os.path import exists as path_exists
from os import remove
import subprocess
from time import time
from typing import Tuple
from attributes import Attributes

from config import JAVA_CLASSPATH, TIMEOUT_MSSG
from results import PartialTestResult
from test_types import UnsupportedTestException


def remove_end_of_line_whitespace(s: str) -> str:
    lines = s.split('\n')
    lines = [line.rstrip() for line in lines]
    return '\n'.join(lines)

def class_name(filename):
    # convert "Code.java" -> "Code"
    return filename[:-5]

def run_code(class_name: str, timeout: float) -> Tuple[bool,str]:
    run_cmd = ["python3", class_name]
    p = subprocess.Popen(run_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        _, output_err = p.communicate(timeout=timeout)
        output = output_err.decode('utf-8')
    except subprocess.TimeoutExpired as e:
        output = TIMEOUT_MSSG
    except Exception as e:
        output = str(e)
    ret = p.returncode
    return ret == 0, output

def run_unit_test(timeout: float) -> Tuple[bool,str]:
    return run_code('UnitTest.py', timeout)

def run_performance_test(timeout: float) -> Tuple[bool,str]:
    return run_code('PerformanceTest', timeout)

def run_io_test(timeout: float, main: str) -> Tuple[bool,str]:
    run_cmd = ["python3", main]
    with open('input.txt', 'r') as file:
        input_data = file.read()
    p = subprocess.Popen(run_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    output_str = ""
    gt_string = ""
    message_to_student = ""

    try:
        output, _ = p.communicate(input_data.encode('utf-8'), timeout=timeout)
        output_str = output.decode('utf-8').rstrip()

        with open('output.txt', 'r') as file:
            gt_string = file.read().replace('\r', '').rstrip()

        gt_string = remove_end_of_line_whitespace(gt_string)
        output_str = remove_end_of_line_whitespace(output_str)

        message_to_student += f"The input:\n{input_data.rstrip()}\n\n"
        message_to_student += f"Your output:\n{output_str}\n\n"
        message_to_student += f"Expected output:\n{gt_string}\n\n"

    except subprocess.TimeoutExpired as e:
        output_str = TIMEOUT_MSSG
        message_to_student += output_str
    except Exception as e:
        output_str = str(e)
        message_to_student += output_str

    return (output_str == gt_string), message_to_student

def run_script_test(timeout: float, args: str = '') -> Tuple[bool,str,float]:

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
            with open('./OUTPUT', 'r') as file:
                output_string = file.read()
        else:
            print('[FATAL]: OUTPUT does not exist.')
            return False, "test failed to run", 0

        if path_exists('./DEBUG'):
            with open('./DEBUG', 'r') as file:
                debug_string = "Debug:\n" + file.read()

        score = float(output_string)
    except subprocess.TimeoutExpired as e:
        debug_string = TIMEOUT_MSSG
    except UnicodeDecodeError as e:
        debug_string = "Malformed output is unreadable, check for non-utf-8 characters\n"

    return (score > 0.0), debug_string, score

def run_approved_includes_test(timeout: float) -> Tuple[bool,str,float]:
    return run_script_test(timeout)

def run_coverage_test(timeout: float) -> Tuple[bool,str,float]:
    return run_script_test(timeout)

def run_compile_test(timeout: float) -> Tuple[bool,str,float]:
    return run_script_test(timeout)

def run_style_test(timeout: float) -> Tuple[bool,str,float]:
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
        runs, run_output = run_unit_test(timeout)
    elif test['type'] == 'i/o':
        runs, run_output = run_io_test(timeout, test['target'])
    elif test['type'] == 'script':
        runs, run_output, point_multiplier = run_script_test(timeout, test['script_args'])
    elif test['type'] == 'performance':
        runs, run_output = run_performance_test(timeout)
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
    elif test['type'] == 'style':
        runs, run_output, point_multiplier = run_style_test(timeout)
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