import subprocess
from time import time
from typing import Tuple
from attributes import Attributes

from config import TIMEOUT_MSSG
from results import PartialTestResult
from test_types import UnsupportedTestException


def remove_end_of_line_whitespace(s: str) -> str:
    lines = s.split('\n')
    lines = [line.rstrip() for line in lines]
    return '\n'.join(lines)

def run_code(class_name: str, timeout: float) -> Tuple[bool,str]:
    run_cmd = ["python3", class_name]
    p = subprocess.Popen(run_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        _, output_err = p.communicate(timeout=timeout)
        output = output_err.decode(encoding = 'utf-8', errors = 'backslashreplace')
    except subprocess.TimeoutExpired:
        output = TIMEOUT_MSSG
    except Exception as e:
        output = str(e)
    ret = p.returncode
    return ret == 0, output

def run_unit_test(timeout: float) -> Tuple[bool,str]:
    return run_code('UnitTest.py', timeout)


def run_io_test(timeout: float, main: str) -> Tuple[bool,str]:
    run_cmd = ["python3", main]
    with open('input.txt', 'r', encoding='utf-8', errors = 'backslashreplace') as file:
        input_data = file.read()
    p = subprocess.Popen(run_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    output_str = ""
    gt_string = ""
    message_to_student = ""

    try:
        output, _ = p.communicate(input_data.encode('utf-8'), timeout=timeout)
        output_str = output.decode(encoding = 'utf-8', errors = 'backslashreplace').rstrip()

        with open('output.txt', 'r', encoding='utf-8', errors = 'backslashreplace') as file:
            gt_string = file.read().replace('\r', '').rstrip()

        gt_string = remove_end_of_line_whitespace(gt_string)
        output_str = remove_end_of_line_whitespace(output_str)

        message_to_student += f"The input:\n{input_data.rstrip()}\n\n"
        message_to_student += f"Your output:\n{output_str}\n\n"
        message_to_student += f"Expected output:\n{gt_string}\n\n"

    except subprocess.TimeoutExpired:
        output_str = TIMEOUT_MSSG
        message_to_student += output_str
    except Exception as e:
        output_str = str(e)
        message_to_student += output_str

    return (output_str == gt_string), message_to_student

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