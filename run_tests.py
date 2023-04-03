#! /usr/bin/env python3

'''
TODO(pcr):
* move configuration stuff to configuration file (and let it be assignment-specific)
* refine attribute requirements
* add command line option to run a specific test or set of tests
* use @target attribute for coverage tests and some other test(s) that don't use it but could/should
'''

from collections import namedtuple
from typing import List, Tuple, Dict, Any, TypedDict, Optional
from os import popen
import os
import subprocess
from sys import argv
from time import time
import json
import argparse

# TODO(pcr): move configuration stuff to configuration file (and let it be assignment-specific)
BEGIN_TEST_DELIMITER = '<test>'
END_TEST_DELIMITER = '</test>'
EMPTY_TEST_BLOCK = '<test/>'

DEFAULT_POINTS = 0.0
DEFAULT_TIMEOUT = 10.0
DEFAULT_SHOW_OUTPUT = 'false'

TIMEOUT_MSSG = 'Timeout during test execution, check for an infinite loop\n'
OCTOTHORPE_LINE = '#'*27
OCTOTHORPE_WALL = '#'+' '*25+'#'
INFO_UNSUPPORTED_TEST = '[INFO] Unsupported Test'

# file contents with position
class FilePosition:
    def __init__(self, index: int, lines: List[str], filename: str):
        self.index: int = index
        self.lines: List[str] = lines
        self.filename: str = filename

class Attributes(TypedDict):
    number: str
    name: str
    points: float
    type: str
    target: str
    show_output: str
    timeout: float
    include: str
    code: str
    expected_input: str
    expected_output: str
    script_content: str
    approved_includes: List[str]
    skip: bool
    script_args: str

def unexpected_end_of_input(fp: FilePosition) -> Exception:
    # filename lineno offset text
    return SyntaxError('unexpected end of input', (fp.filename, fp.index, fp.lines[-1]))

def goto_next_line(fp: FilePosition) -> str:
    fp.index += 1
    if fp.index >= len(fp.lines):
        raise unexpected_end_of_input(fp)

    # skip blank lines
    skip_blank_lines(fp)
    line = fp.lines[fp.index].strip()

    return line

def skip_blank_lines(fp: FilePosition) -> None:
    while fp.index < len(fp.lines) and not fp.lines[fp.index].strip():
        fp.index += 1

def eat_block_of_test(fp: FilePosition) -> str:
    # go to next line
    line = goto_next_line(fp)

    # expect start of test block
    if line == EMPTY_TEST_BLOCK:
        return line

    if line != BEGIN_TEST_DELIMITER:
        # filename lineno offset text
        raise SyntaxError(f'missing expected start of test block: "{BEGIN_TEST_DELIMITER}"', (fp.filename, fp.index+1, 1, line))

    # eat until end of test block
    while line != END_TEST_DELIMITER:
        # go to next line
        line = goto_next_line(fp)

    return line

def eat_empty_test_block(fp: FilePosition) -> str:
    # go to next line
    line = goto_next_line(fp)

    # expect empty test block
    if line == BEGIN_TEST_DELIMITER:
        line = goto_next_line(fp)
        if line != END_TEST_DELIMITER:
            raise SyntaxError(f'expected end of test: "{END_TEST_DELIMITER}"', (fp.filename, fp.index+1, 1, line))
        return line
    elif line != EMPTY_TEST_BLOCK:
        # filename lineno offset text
        raise SyntaxError(f'expected empty test block: "{EMPTY_TEST_BLOCK}"', (fp.filename, fp.index+1, 1, line))
    return line


def read_annotations(fp: FilePosition) -> Dict[str, Any]:
    # expect start of multiline comment
    line = fp.lines[fp.index].strip()
    if line != '/*':
        # filename lineno offset text
        raise SyntaxError('missing expected start of multiline comment: "/*"', (fp.filename, fp.index+1, 1, line))

    # go to next line
    line = goto_next_line(fp)

    attr_dict: Dict[str, Any] = dict()
    while line.startswith('@'):
        try:
            tag,value = line.split(sep=':', maxsplit=1)
        except ValueError:
            raise SyntaxError('missing attribute value? (attributes look like "@name: value")', (fp.filename, fp.index+1, 1, line))
        tag = tag.strip()[1:]
        value = value.strip()
        if tag in attr_dict:
            old_value = attr_dict[tag]
            print(f'[WARNING] ({fp.filename}:{fp.index+1}) tag "{tag}" already exists, old value will be overwritten: {old_value} --> {value}')
        if tag == "points":
            points = DEFAULT_POINTS
            try:
                points = float(value)
            except ValueError:
                print(f'[WARNING] ({fp.filename}:{fp.index+1}) points attribute has invalid value, using default value ({DEFAULT_POINTS})')
            attr_dict['points'] = points
        elif tag =='timeout':
            timeout = DEFAULT_TIMEOUT
            try:
                timeout = float(value)
                if timeout <= 0:
                    raise ValueError('timeout must be positive')
            except ValueError:
                print(f'[WARNING] ({fp.filename}:{fp.index+1}) timeout attribute has invalid value, using default value ({DEFAULT_TIMEOUT})')
            attr_dict['timeout'] = timeout
        else:
            attr_dict[tag] = value

        # go to next line
        line = goto_next_line(fp)

    # expect end of multiline comment
    if line != '*/':
        # filename lineno offset text
        raise SyntaxError('missing expected end of multiline comment: "*/"', (fp.filename, fp.index+1, 1, line))

    return attr_dict


def verify_required_annotations(annotations: Dict[str, Any], fp: FilePosition) -> None:
    # verify all required attributes are present
    required_attributes = ('name', 'points', 'type', 'target')
    for attribute in required_attributes:
        additonal_details = str()
        for attr in annotations:
            additonal_details += f'  {attr}: {annotations[attr]}\n'
        if attribute not in annotations and type != 'script':
            raise KeyError(f'({fp.filename}:{fp.index+1}) missing required attribute: {attribute}\n{additonal_details}')
        if annotations[attribute] == '':
            raise ValueError(f'({fp.filename}:{fp.index+1}) required attribute missing value: {attribute}\n{additonal_details}')



def apply_default_annotations(annotations: Dict[str, Any]) -> None:
    # set timeouts to default if not specified
    if 'timeout' not in annotations:
        annotations['timeout'] = DEFAULT_TIMEOUT

    # set show_output to default if not specified
    if 'show_output' not in annotations:
        if annotations['type'] == 'approved_includes' or annotations['type'] == 'performance' or annotations['type'] == 'coverage' or annotations['type'] == 'compile' or annotations['type'] == 'memory_errors':
            annotations['show_output'] = 'True'
        else:
            annotations['show_output'] = DEFAULT_SHOW_OUTPUT

    if 'include' not in annotations:
        annotations['include'] = ''

    if 'skip' in annotations and annotations['skip'].lower() == 'true':
        annotations['skip'] = True
    else:
        annotations['skip'] = False

def read_attributes(fp: FilePosition) -> Attributes:
    # skip blank lines
    skip_blank_lines(fp)
    if fp.index >= len(fp.lines):
        # at end of file
        empty_attr: Attributes = {
            'number': '',
            'name': '',
            'points': 0.0,
            'type': '',
            'target': '',
            'show_output': '',
            'timeout': 0.0,
            'include': '',
            'code': '',
            'expected_input':'',
            'expected_output': '',
            'script_content': '',
            'approved_includes': [],
            'skip': False,
            'script_args': ''
        }
        return empty_attr

    annotations = read_annotations(fp)
    verify_required_annotations(annotations, fp)
    apply_default_annotations(annotations)

    attributes: Attributes = {
        'number': annotations['number'],
        'name': annotations['name'],
        'points': annotations['points'],
        'type': annotations['type'],
        'target': annotations['target'],
        'show_output': annotations['show_output'],
        'timeout': annotations['timeout'],
        'include': annotations['include'],
        'code': '',
        'expected_input':'',
        'expected_output': '',
        'script_content': '',
        'approved_includes': [],
        'skip': annotations['skip'],
        'script_args': ''
        }

    return attributes

def read_block_of_test(fp: FilePosition) -> str:
    code = str()
    got_code = True
    while got_code:
        line = goto_next_line(fp)

        if line != END_TEST_DELIMITER:
            code += line + '\n'
        else:
            got_code = False

    return code

def read_unit_test(fp: FilePosition) -> str:
    # go to next line
    line = goto_next_line(fp)

    # expect start of test block
    if line != BEGIN_TEST_DELIMITER:
        # filename lineno offset text
        raise SyntaxError(f'missing expected start of test block: "{BEGIN_TEST_DELIMITER}"', (fp.filename, fp.index+1, 1, line))

    # expect next lines to be unit test code
    code = read_block_of_test(fp)
    return code

def read_io_test(fp: FilePosition) -> Tuple[str, str]:
    # go to next line
    line = goto_next_line(fp)
    if line != BEGIN_TEST_DELIMITER:
        # filename lineno offset text
        raise SyntaxError(f'missing expected start of test block: "{BEGIN_TEST_DELIMITER}"', (fp.filename, fp.index+1, 1, line))

    input_filename = None
    output_filename = None

    for _ in range(2):
        # go to next line
        line = goto_next_line(fp)

        try:
            tag, value = line.split(':')
        except ValueError:
            # filename lineno offset text
            raise SyntaxError('expected "tag: value" pair', (fp.filename, fp.index+1, 1, line))

        tag = tag.strip()
        value = value.strip()

        if tag == 'input':
            input_filename = value
        elif tag == 'output':
            output_filename = value
        else:
            # filename lineno offset text
            raise SyntaxError(f'unexpected tag ({tag}) in i/o test', (fp.filename, fp.index+1, 1, line))


    # go to next line
    line = goto_next_line(fp)

    if line != END_TEST_DELIMITER:
        # filename lineno offset text
        raise SyntaxError(f'missing expected end of test block: "{END_TEST_DELIMITER}"', (fp.filename, fp.index+1, 1, line))

    if not input_filename:
        raise SyntaxError('missing output filename in i/o test', (fp.filename, fp.index+1, 1, line))
    if not output_filename:
        raise SyntaxError('missing input filename in i/o test', (fp.filename, fp.index+1, 1, line))

    expected_input = None
    expected_output = None
    try:
        with open(input_filename, 'r') as f:
            expected_input = f.read()
    except FileNotFoundError:
        raise SyntaxError(f'input file not found: {input_filename}', (fp.filename, fp.index+1, 1, line))

    try:
        with open(output_filename, 'r') as f:
            expected_output = f.read()
    except FileNotFoundError:
        raise SyntaxError(f'output file not found: {output_filename}', (fp.filename, fp.index+1, 1, line))

    return expected_input, expected_output

def read_script_test(fp: FilePosition) -> Tuple[str, str]:
    # go to next line
    line = goto_next_line(fp)
    if line != BEGIN_TEST_DELIMITER:
        # filename lineno offset text
        raise SyntaxError(f'missing expected start of test block: "{BEGIN_TEST_DELIMITER}"', (fp.filename, fp.index+1, 1, line))

    # go to next line
    line = goto_next_line(fp)
    values = line.split(None, 1)
    script_args = str()
    script_content = str()
    if len(values) == 0:
            raise SyntaxError('missing expected name of script, e.g. scripts/example.sh', (fp.filename, fp.index+1, 1, line))
    elif len(values) == 1:
        # does not have args (only script path)
        script_filename_string = line
    else:
        # has args
        script_filename_string = values[0]
        script_args = values[1]

    # print("Script filename: " + script_filename_string)

    line = goto_next_line(fp)
    if line != END_TEST_DELIMITER:
        # filename lineno offset text
        raise SyntaxError(f'missing expected end of test block: "{END_TEST_DELIMITER}"', (fp.filename, fp.index+1, 1, line))

    try:
        with open(script_filename_string, 'r') as f:
            script_content = f.read()
    except FileNotFoundError:
        print(f'No such file or directory: \'{script_filename_string}\'')

    return script_args, script_content

def read_approved_includes(fp: FilePosition) -> List[str]:
     # go to next line
    line = goto_next_line(fp)

    # expect start of test block
    if line != BEGIN_TEST_DELIMITER:
        # filename lineno offset text
        raise SyntaxError(f'missing expected start of test block: "{BEGIN_TEST_DELIMITER}"', (fp.filename, fp.index+1, 1, line))

    # go to next line
    line = goto_next_line(fp)

    approved_includes = list()
    while line != END_TEST_DELIMITER:
        approved_includes.append(line)
        line = goto_next_line(fp)

    return approved_includes

def read_coverage_test(fp: FilePosition) -> Tuple[str, str, List[str]]:
    # go to next line
    line = goto_next_line(fp)

    # expect start of test block
    if line != BEGIN_TEST_DELIMITER:
        # filename lineno offset text
        raise SyntaxError(f'missing expected start of test block: "{BEGIN_TEST_DELIMITER}"', (fp.filename, fp.index+1, 1, line))

    source = list()
    target = str()
    main = str()

    # go to next line
    line = goto_next_line(fp)

    while line != END_TEST_DELIMITER:
        try:
            tag, values = line.split(':')
        except ValueError:
            # filename lineno offset text
            raise SyntaxError('expected "tag: value" pair', (fp.filename, fp.index+1, 1, line))

        tag = tag.strip()

        if tag == 'source':
            source = values.split()
        elif tag == 'target':
            target = values.strip()
        elif tag == 'main':
            main = values.strip()
        else:
            # filename lineno offset text
            raise SyntaxError(f'unexpected tag ({tag}) in coverage test', (fp.filename, fp.index+1, 1, line))

        # go to next line
        line = goto_next_line(fp)

    if not (target and main):
        # filename lineno offset text
        raise SyntaxError('missing expected main and/or target in coverage test', (fp.filename, fp.index+1, 1, line))

    return target, main, source


def read_tests(filename: str) -> List[Attributes]:
    with open(filename) as f:
        lines = f.readlines()
    # trim empty lines at end of file
    while lines[-1].strip() == '':
        del lines[-1]
    fp = FilePosition(0, lines, filename)
    tests = list()
    while fp.index < len(fp.lines):
        # expect next lines to be only attributes and values
        attributes = read_attributes(fp)

        if fp.index < 0:
            # at end of file
            break

        test_type = attributes['type']
        if test_type == 'unit' or test_type == 'performance':
            code = read_unit_test(fp)
            attributes['code'] = code
            tests.append(attributes)

        elif test_type == 'i/o':
            expected_input, expected_output = read_io_test(fp)
            attributes['expected_input'] = expected_input
            attributes['expected_output'] = expected_output
            tests.append(attributes)

        elif test_type == 'script':
            script_args, script_content = read_script_test(fp)
            attributes['script_args'] = script_args
            attributes['script_content'] = script_content
            tests.append(attributes)

        elif test_type == 'approved_includes' or test_type == 'compile' or test_type == 'memory_errors':
            approved_includes = read_approved_includes(fp)
            attributes['approved_includes'] = approved_includes
            tests.append(attributes)

        elif test_type == 'coverage':
            target, main, source = read_coverage_test(fp)
            attributes['target'] = target
            attributes['include'] = main
            attributes['approved_includes'] = source
            tests.append(attributes)

        else:
            print('WARNING: undefined test type: {}.  this one will be ignored: {}'.format(test_type, attributes['name']))
            _ = eat_block_of_test(fp)

        fp.index += 1

    return tests

def write_unit_test(test: Attributes) -> None:
    with open('unit_test.cpp', 'wt') as f:
        f.write(f"#include \"{test['target']}\"\n\n")
        if len(test['include']) > 0:
            for include in test['include'].split():
                f.write(f'#include {include}\n')
        f.write('#include "cs12x_test.h"\n\n')

        f.write('int main() {\n')
        f.write('    INIT_TEST;\n')
        f.write('    {}\n'.format('\n    '.join(test['code'].splitlines())))
        f.write('    RESULT(pass);\n')
        f.write('    return pass ? 0 : 1;\n')
        f.write('}\n')

def write_performance_test(test: Attributes) -> None:
    with open('performance_test.cpp', 'wt') as f:
        f.write(f"#include \"{test['target']}\"\n\n")
        f.write('#include <iostream>\n')
        f.write('#include <chrono>\n')
        if len(test['include']) > 0:
            for include in test['include'].split():
                f.write(f'#include {include}\n')
        f.write('#include "cs12x_test.h"\n\n')

        f.write('int main() {\n')
        f.write('    INIT_TEST;\n')
        f.write('    {}\n'.format('\n    '.join(test['code'].splitlines())))
        f.write('    RESULT(pass);\n')
        f.write('    return pass ? 0 : 1;\n')
        f.write('}\n')

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

def write_approved_includes_test(test: Attributes) -> None:
    test['script_content'] = f"./approved_includes.sh {test['target']} {' '.join(test['approved_includes'])}"
    write_script_test(test)

def write_coverage_test(test: Attributes) -> None:
    test['script_content'] = f"./coverage.sh {test['target']} {test['include']} {' '.join(test['approved_includes'])}"
    write_script_test(test)

def write_compile_test(test: Attributes) -> None:
    test['script_content'] = f"./compiles.sh {' '.join(test['approved_includes'])}"
    write_script_test(test)

def write_memory_errors_test(test: Attributes) -> None:
    test['script_content'] = f"./memory_errors.sh {' '.join(test['approved_includes'])}"
    write_script_test(test)

def compile_x_test(name: str, src: List[str] = None) -> Tuple[bool,str]:
    CXX = 'g++'
    FLAGS = f'-std=c++17 -g -o {name}'
    if src:
        SRC = ' '.join(src)
    else:
        SRC = f'{name}.cpp'
    compile_cmd = '{} {} {} 2>&1'.format(CXX, FLAGS, SRC)
    p = popen(compile_cmd)
    try:
        output = p.read()
    except Exception as e:
        output = str(e)
    ret = p.close()
    return ret == None, output

def compile_unit_test() -> Tuple[bool,str]:
    return compile_x_test('unit_test')

def compile_performance_test() -> Tuple[bool,str]:
    return compile_x_test('performance_test')

def compile_io_test(src: List[str]) -> Tuple[bool,str]:
    return compile_x_test('io_test', src)

def compile_script_test() -> Tuple[bool,str]:
    return True, ""

def compile_approved_includes_test() -> Tuple[bool,str]:
    return True, ""

def compile_coverage_test() -> Tuple[bool,str]:
    return True, ""

def compile_compile_test() -> Tuple[bool,str]:
    return True, ""

def compile_memory_errors_test() -> Tuple[bool,str]:
    return True, ""

def run_unit_test(timeout: float) -> Tuple[bool,str]:
    run_cmd = ["./unit_test", "2>&1"]
    p = subprocess.Popen(run_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        output_en, err_en = p.communicate(timeout=timeout) #p.stdout.decode('utf-8')
        output = output_en.decode('utf-8')
    except subprocess.TimeoutExpired as e:
        output = TIMEOUT_MSSG
    except Exception as e:
        output = str(e)
    ret = p.returncode
    return ret == 0, output

def run_performance_test(timeout: float) -> Tuple[bool,str]:
    run_cmd = ["./performance_test", "2>&1"]
    p = subprocess.Popen(run_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        output_en, err_en = p.communicate(timeout=timeout) #p.stdout.decode('utf-8')
        output = output_en.decode('utf-8')
    except subprocess.TimeoutExpired as e:
        output = "Timeout during test execution, check for an infinite loop\n"
    except Exception as e:
        output = str(e)
    ret = p.returncode
    return ret == 0, output

def remove_end_of_line_whitespace(s: str) -> str:
    lines = s.split('\n')
    lines = [line.rstrip() for line in lines]
    return '\n'.join(lines)


def run_io_test(timeout: float) -> Tuple[bool,str]:
    run_cmd = ["./io_test", "2>&1"]
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

    if os.path.exists('./DEBUG'):
        os.remove('./DEBUG')
    if os.path.exists('./OUTPUT'):
        os.remove('./OUTPUT')

    cmd = f'bash ./script.sh {args}'
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, shell=True)
    score = 0.0
    debug_string = ""
    output_string = "0"
    try:
        output, err = p.communicate(timeout=timeout)

        if os.path.exists('./OUTPUT'):
            with open('./OUTPUT', 'r') as file:
                output_string = file.read()
        else:
            print('[FATAL]: OUTPUT does not exist.')
            return False, "test failed to run", 0

        if os.path.exists('./DEBUG'):
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

def run_memory_errors_test(timeout: float) -> Tuple[bool,str,float]:
    return run_script_test(timeout)

class TestResult(TypedDict):
    number: str
    name: str
    score: float
    max_score: float
    output: str
    tags: Optional[List[str]]
    visibility: Optional[str]
    extra_data: Optional[Dict[Any,Any]]

class Result(TypedDict):
    score: float
    output: str
    execution_time: float
    visibility: str
    stdout_visibility: str
    tests: List[TestResult]

def write_test(test: Attributes) -> bool:
    if test['type'] == 'unit':
        write_unit_test(test)
    elif test['type'] == 'i/o':
        write_io_test(test)
    elif test['type'] == 'script':
        write_script_test(test)
    elif test['type'] == 'approved_includes':
        write_approved_includes_test(test)
    elif test['type'] == 'performance':
        write_performance_test(test)
    elif test['type'] == 'coverage':
        write_coverage_test(test)
    elif test['type'] == 'compile':
        write_compile_test(test)
    elif test['type'] == 'memory_errors':
        write_memory_errors_test(test)
    else:
        print(INFO_UNSUPPORTED_TEST)
        return False
    return True

def compile_test(test: Attributes) -> Tuple[bool, bool, str]:
    compile_output = ''
    if test['type'] == 'unit':
        compiles, compile_output = compile_unit_test()
    elif test['type'] == 'i/o':
        compiles, compile_output = compile_io_test([test['target'], test['include']])
    elif test['type'] == 'script':
        compiles, compile_output = compile_script_test()
    elif test['type'] == 'performance':
        compiles, compile_output = compile_performance_test()
    elif test['type'] == 'approved_includes':
        compiles, compile_output = compile_approved_includes_test()
    elif test['type'] == 'coverage':
        compiles, compile_output = compile_coverage_test()
    elif test['type'] == 'compile':
        compiles, compile_output = compile_compile_test()
    elif test['type'] == 'memory_errors':
        compiles, compile_output = compile_memory_errors_test()
    else:
        print(INFO_UNSUPPORTED_TEST)
        return False, False, None
    return True, compiles, compile_output

def run_test(test: Attributes) -> Tuple[bool, str, bool, bool, float, float]:
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
        runs, run_output = run_io_test(timeout)
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
    elif test['type'] == 'memory_errors':
        runs, run_output, point_multiplier = run_memory_errors_test(timeout)
    else:
        print(INFO_UNSUPPORTED_TEST)
        return False, '', False, False, 0.0, 0.0
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

    return True, run_output, unapproved_includes, sufficient_coverage, points, run_time

def main(args) -> Result:
    filename = args.tests_path
    test_number = args.tests
    debugmode = args.debugmode
    if debugmode:
        print('===DEBUGMODE===')

    result_score = 0.0
    test_results: List[TestResult] = list()
    extra_data = None
    leaderboard = None

    fail_result: Result = {
        'score': 0.0,
        'output': '',
        'execution_time': 0.0,
        'visibility': 'visible',
        'stdout_visibility': 'visible',
        'tests': []
        }
    try:
        tests = read_tests(filename)
    except Exception as err:
        fail_result['output'] = repr(err)
        print('[FATAL] Error occured while reading tests:')
        print(err)
        return fail_result


    if test_number != '*':
        # run only those tests with number that matches test_number
        #   '5' means run all tests numbered 5: 5[.1, 5.2, ...]
        #   '5.2' means run all tests numbered 5.2: 5.2[.1, 5.2.2, ...]
        for test in tests:
            if test['number'] == test_number or (test['number'].startswith(test_number) and (len(test['number']) == len(test_number) or test['number'][len(test_number)] == '.')):
                test['skip'] = False
            else:
                test['skip'] = True


    possible = 0.0
    total_time = 0.0
    for test in tests:
        if test['skip']:
            #print(f"test {test['number']}: {test['name']}\n[SKIP]")
            continue
        max_points = float(test['points'])
        possible += max_points
        print(f"test {test['number']}: {test['name']}")

        ok = write_test(test)
        if not ok:
            continue

        ok, compiles, compile_output = compile_test(test)
        if not ok:
            continue

        failed_to_compile = False
        if compiles:
            pack = run_test(test)
            ok, run_output, unapproved_includes, sufficient_coverage, points, run_time = pack
            if not ok:
                continue
            total_time += run_time
        else:
            print('[FAIL] failed to compile\n')
            failed_to_compile = True
            points = 0

        result_score += points

        test_result: TestResult = {
            'number': test['number'],
            'name': test['name'],
            'score': points,
            'max_score': max_points,
            'output': '',
            'tags': [],
            'visibility': 'visible',
            'extra_data': {}
            }

        if debugmode:
            test['show_output'] = 'true'

        if test['show_output'].lower() == 'true':
            has_compile_output = len(compile_output) > 0
            if has_compile_output:
                test_result['output'] += compile_output.strip()
            if len(run_output) > 0:
                if has_compile_output > 0:
                    test_result['output'] += '\n\n'
                test_result['output'] += run_output.strip()
        else:
            if failed_to_compile:
                test_result['output']  += 'Failed to compile.\n'
            test_result['output'] += 'Output is intentionally hidden'

        test_results.append(test_result)

    recorded_score = result_score;
    result_output = ''
    if unapproved_includes:
        recorded_score = 0
        result_output += 'Forbidden includes are used, your current submission score is 0.0\n'

    if not sufficient_coverage:
        recorded_score = 0
        result_output += 'Insufficient test coverage, so your current submission score is 0.0\n'

    # DISABLE SCORING FROM AUTOGRADER
    # results_score = 0

    # if results['visibility'] == 'visible' or results['stdout_visibility'] == 'visible':
    #     print(OCTOTHORPE_LINE)
    #     print(OCTOTHORPE_WALL)
    #     print('# WARNING WARNING WARNING #')
    #     print(OCTOTHORPE_WALL)
    #     if results['visibility'] == 'visible':
    #         print('# TESTS ARE VISIBLE       #')
    #     if results['stdout_visibility'] == 'visible':
    #         print('# STDOUT IS VISIBLE       #')
    #     print(OCTOTHORPE_WALL)
    #     print(OCTOTHORPE_LINE)

    t = int(result_score * 10000 + 0.5)
    result_score = t / 10000

    str_score = f'{result_score:6.2f}'
    str_possible = f'{possible:6.2f}'
    print(OCTOTHORPE_LINE)
    print(OCTOTHORPE_WALL)
    if unapproved_includes or not sufficient_coverage:
        str_score = str_score.replace(' ', '~')
        print(f'# points:~{str_score}~/ {str_possible} #')
        print(f'#         {recorded_score:6.2f} / {str_possible} #')
    else:
        print(f'# points: {str_score} / {str_possible} #')
    print(OCTOTHORPE_WALL)
    print(OCTOTHORPE_LINE)
    if unapproved_includes:
        print('!!! ZERO DUE TO UNAPPROVED INCLUDES')
    if not sufficient_coverage:
        print('!!! ZERO DUE TO INSUFFICIENT COVERAGE')

    results: Result = {
        'score': recorded_score,
        'output': result_output,
        'execution_time': total_time,
        'visibility': 'visible',
        'stdout_visibility': 'visible',
        'tests': test_results
        }

    if extra_data:
        results['extra_data'] = dict()
    if leaderboard:
        results['leaderboard'] = leaderboard

    return results

def snarky_comment_about_number_of_submissions(n: int) -> str:
    if n < 4:
        return "That's OK.  Make sure that you reflect on the feedback and think before you code.  Before making another submission, write test cases to reproduce the errors and then use your favorite debugging technique to isolate and fix the errors.  You can do it!"
    if n < 7:
        return "You should take some time before your next submission to think about the errors and how to fix them.  Start by reproducing the errors with test cases locally."
    if n < 10:
        return "Why don't you take a break, take a walk, take nap, and come back to this after you've had a chance to think a bit more.  Remember: start by reproducing the error, then isolate it and fix it."
    if n < 15:
        return "It looks like you're having difficulty finding and fixing your errors.  You should come to office hours.  We can help you."
    if n < 20:
        return "If you haven't gone to office hours yet, you really should.  We want to help you.  How's your coverage?  You can't test what you don't cover."
    if n < 30:
        return "Did you know that you can not only compile locally, but you can also test locally?  You should try it."
    if n < 40:
        return "literally nobody: \n             you: autograder go brrr."
    if n < 50:
        return "I'm almost out of snarky ways to comment on how many submissions you've made.  That's how many submissions you've made."
    if n < 75:
        return "Big yikes.  No cap, fam, take several seats. This ain't it, chief.  Your code and development process are sus AF.  Periodt."
    if n < 100:
        return "Your number of submissions to this assignment is too damn high."
    return "I'm not even mad, that's amazing."

def ordinal_suffix(n: int) -> str:
    if n > 10 and n < 20:
        return "th"
    return ["th", "st", "nd", "rd", "th", "th", "th", "th", "th", "th"][n%10]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('tests_path', type=str, help='path to tests (input)')
    parser.add_argument('-r', '--results_path', type=str, default='results.json', help='path to results (output) [default=./results.json]')
    parser.add_argument('-d', '--debugmode', help='force show test output', action='store_true')
    parser.add_argument('-t', '--tests', type=str, default='*')
    parser.add_argument('-l', '--language', type=str, default='c++')

    args = parser.parse_args()
    results_filename = args.results_path

    results = main(args)

    #print(json.dumps(results, sort_keys=True, indent=4))
    with open(results_filename,'wt') as f:
        json.dump(results, f, sort_keys=True, indent=4)


    # keep max score over all previous submissions
    if os.path.exists('/autograder/'):
        # running on gradescope
        previousMaxScore = 0.0
        submission_cnt = 0
        with open('/autograder/submission_metadata.json', 'r') as f:
            previousResultJson = json.load(f)
            submission_cnt = len(previousResultJson['previous_submissions'])
            for prevSubmission in previousResultJson['previous_submissions']:
                previousScore = float(prevSubmission["score"])
                if (previousScore > previousMaxScore):
                    previousMaxScore = previousScore

        with open('/autograder/results/results.json', 'r') as f:
            currentResult = json.load(f)

        if (previousMaxScore > float(currentResult['score'])):
            currentResult["output"] += "\n"
            currentResult["output"] += "Your current submission's score was " + str(float(currentResult["score"])) + ", however you get to keep your maximum submission score of " + str(previousMaxScore) + "\n"
            currentResult['score'] = previousMaxScore

        submission_cnt += 1
        currentResult["output"] += f"This is your {submission_cnt}{ordinal_suffix(submission_cnt)} submission.\n"
        currentResult["output"] += snarky_comment_about_number_of_submissions(submission_cnt) + "\n"

        with open('/autograder/results/results.json', 'w') as f:
            json.dump(currentResult, f, sort_keys=True, indent=4)
    # else running on local so no need to compute max score
