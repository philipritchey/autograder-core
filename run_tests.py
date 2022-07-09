#! /usr/bin/env python3

from collections import namedtuple
from typing import List, Tuple, Dict, Any, TypedDict, Optional
from os import popen
import os
import subprocess
from sys import argv
from time import time
import json

# TODO: move configuration stuff to configuration file (and let it be assignment-specific)
BEGIN_TEST_DELIMITER = '<test>'
END_TEST_DELIMITER = '</test>'
EMPTY_TEST_BLOCK = '<test/>'

DEFAULT_POINTS = 0.0
DEFAULT_TIMEOUT = 10.0
DEFAULT_SHOW_OUTPUT = 'false'

def unexpected_end_of_input(filename: str, index: int, line: str) -> Exception:
    # filename lineno offset text
    return SyntaxError('unexpected end of input', (filename, index, len(line), line))

def goto_next_line(index: int, lines: List[str], filename: str) -> Tuple[int, str]:
    index += 1
    if index >= len(lines):
        raise unexpected_end_of_input(filename, index, lines[-1])
    line = lines[index].strip()
    
    # skip blank lines
    index =  skip_blank_lines(index, lines)
    line = lines[index].strip()
    
    return index, line
    
def skip_blank_lines(index: int, lines: List[str]) -> int:
    while index < len(lines) and not lines[index].strip():
        index += 1
    return index

def eat_block_of_test(index, lines, filename) -> Tuple[int,str]:
    # go to next line
    index,line = goto_next_line(index, lines, filename)
    
    # expect start of test block
    if line == EMPTY_TEST_BLOCK:
        return index,line
    
    if line != BEGIN_TEST_DELIMITER:
        # filename lineno offset text
        raise SyntaxError(f'missing expected start of test block: "{BEGIN_TEST_DELIMITER}"', (filename, index+1, 1, line))
    
    # eat until end of test block
    while line != END_TEST_DELIMITER:
        # go to next line
        index, line = goto_next_line(index, lines, filename)
            
    return index,line
    
def eat_empty_test_block(index, lines, filename) -> Tuple[int,str]:
    # go to next line
    index,line = goto_next_line(index, lines, filename)
    
    # expect empty test block
    if line == BEGIN_TEST_DELIMITER:
        index,line = goto_next_line(index, lines, filename)
        if line != END_TEST_DELIMITER:
            raise SyntaxError(f'expected end of test: "{END_TEST_DELIMITER}"', (filename, index+1, 1, line))
        return index,line
    elif line != EMPTY_TEST_BLOCK:
        # filename lineno offset text
        raise SyntaxError(f'expected empty test block: "{EMPTY_TEST_BLOCK}"', (filename, index+1, 1, line))
    return index,line

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
    

def read_attributes(index: int, lines: List[str], filename: str) -> Tuple[int, Optional[Attributes]]:
    # skip blank lines
    index = skip_blank_lines(index, lines)
    if index >= len(lines):
        # at end of file
        return -1, None
    line = lines[index].strip()
    
    # expect start of multiline comment
    if line != '/*':
        # filename lineno offset text
        raise SyntaxError('missing expected start of multiline comment: "/*"', (filename, index+1, 1, line))

    # go to next line
    index, line = goto_next_line(index, lines, filename)

    attr_dict: Dict[str, Any] = dict()
    while line.startswith('@'):
        try:
            tag,value = line.split(sep=':', maxsplit=1)
        except ValueError:
            raise SyntaxError('missing attribute value? (attributes look like "@name: value")', (filename, index+1, 1, line))
        tag = tag.strip()[1:]
        value = value.strip()
        if tag in attr_dict:
            old_value = attr_dict[tag]
            print(f'[WARNING] ({filename}:{index+1}) tag "{tag}" already exists, old value will be overwritten: {old_value} --> {value}')
        if tag == "points":
            points = DEFAULT_POINTS
            try:
                points = float(value)
            except ValueError:
                print(f'[WARNING] ({filename}:{index+1}) points attribute has invalid value, using default value ({DEFAULT_POINTS})')
            attr_dict['points'] = points
        elif tag =='timeout':
            timeout = DEFAULT_TIMEOUT
            try:
                timeout = float(value)
                if timeout <= 0:
                    raise ValueError('timeout must be positive')
            except ValueError:
                print(f'[WARNING] ({filename}:{index+1}) timeout attribute has invalid value, using default value ({DEFAULT_TIMEOUT})')
            attr_dict['timeout'] = timeout
        else:
            attr_dict[tag] = value
        
        # go to next line
        index, line = goto_next_line(index, lines, filename)
        
    # expect end of multiline comment
    if line != '*/':
        # filename lineno offset text
        raise SyntaxError('missing expected end of multiline comment: "*/"', (filename, index+1, 1, line))
    
    # verify all required attributes are present
    required_attributes = ('name', 'points', 'type', 'target', 'number')
    for attribute in required_attributes:
        if attribute not in attr_dict:
            raise KeyError(f'({filename}:{index+1}) missing required attribute: {attribute}')
            
    # set timeouts to default if not specified
    if 'timeout' not in attr_dict:
        attr_dict['timeout'] = DEFAULT_TIMEOUT
        
    # set show_output to default if not specified
    if 'show_output' not in attr_dict:
        if attr_dict['type'] == 'approved_includes':
            attr_dict['show_output'] = 'True'
        else:
            attr_dict['show_output'] = DEFAULT_SHOW_OUTPUT
        
    if 'include' not in attr_dict:
        attr_dict['include'] = ''
    
    attributes: Attributes = {
        'number': attr_dict['number'],
        'name': attr_dict['name'],
        'points': attr_dict['points'],
        'type': attr_dict['type'],
        'target': attr_dict['target'],
        'show_output': attr_dict['show_output'],
        'timeout': attr_dict['timeout'],
        'include': attr_dict['include'],
        'code': '',
        'expected_input':'',
        'expected_output': '',
        'script_content': '',
        'approved_includes': []
        }
    
    return index, attributes

def read_block_of_test(index: int, lines: List[str], filename: str) -> Tuple[int, str]:
    code = str()
    got_code = True
    while got_code:
        index,line = goto_next_line(index, lines, filename)
        
        if line != END_TEST_DELIMITER:
            code += line + '\n'
        else:
            got_code = False
    
    return index, code

def read_tests(filename: str) -> List[Attributes]:
    tests = list()
    with open(filename) as f:
        lines = f.readlines()
    index = 0
    while index < len(lines):
        # expect next lines to be only attributes and values
        index, attributes = read_attributes(index, lines, filename)
        if index < 0:
            # at end of file
            break

        type = attributes['type']
        if type == 'unit' or type == 'performance':
            # go to next line
            index,line = goto_next_line(index, lines, filename)
            
            # expect start of test block
            if line != BEGIN_TEST_DELIMITER:
                # filename lineno offset text
                raise SyntaxError(f'missing expected start of test block: "{BEGIN_TEST_DELIMITER}"', (filename, index+1, 1, line))
            
            # expect next lines to be unit test code
            index, code = read_block_of_test(index, lines, filename)      
            attributes['code'] = code
            
            tests.append(attributes)

        elif type == 'i/o':
            # go to next line
            index,line = goto_next_line(index, lines, filename)
            if line != BEGIN_TEST_DELIMITER:
                # filename lineno offset text
                raise SyntaxError(f'missing expected start of i/o block: "{BEGIN_TEST_DELIMITER}"', (filename, index+1, 1, line))

            # expect start of code block
            index,line = goto_next_line(index, lines, filename)
            if line != 'input':
                # filename lineno offset text
                raise SyntaxError('missing expected start of i/o input section: "input"', (filename, index+1, 1, line))
            
            # go to next line
            index,line = goto_next_line(index, lines, filename)
            input_filename_string = line
            # print("Input filename: " + input_filename_string)

            index,line = goto_next_line(index, lines, filename)
            if line != 'output':
                # filename lineno offset text
                raise SyntaxError('missing expected start of i/o output section: "output"', (filename, index+1, 1, line))
            
            index,line = goto_next_line(index, lines, filename)
            output_filename_string = line
            # print("Output filename: " + output_filename_string)

            index,line = goto_next_line(index, lines, filename)
            if line != END_TEST_DELIMITER:
                # filename lineno offset text
                raise SyntaxError(f'missing expected end of i/o block: "{END_TEST_DELIMITER}"', (filename, index+1, 1, line))


            try:
                with open(input_filename_string, 'r') as f:
                    attributes['expected_input'] = f.read()
            except FileNotFoundError:
                raise SyntaxError(f'input file not found: {input_filename_string}', (filename, index+1, 1, line))
                
            try:
                with open(output_filename_string, 'r') as f:
                    attributes['expected_output'] = f.read()
            except FileNotFoundError:
                raise SyntaxError(f'output file not found: {output_filename_string}', (filename, index+1, 1, line))

            tests.append(attributes)

        elif type == 'script':
            # go to next line
            index,line = goto_next_line(index, lines, filename)
            if line != BEGIN_TEST_DELIMITER:
                # filename lineno offset text
                raise SyntaxError(f'missing expected start of script block: "{BEGIN_TEST_DELIMITER}"', (filename, index+1, 1, line))

            # go to next line
            index,line = goto_next_line(index, lines, filename)
            script_filename_string = line
            # print("Script filename: " + script_filename_string)

            index,line = goto_next_line(index, lines, filename)
            if line != END_TEST_DELIMITER:
                # filename lineno offset text
                raise SyntaxError(f'missing expected end of script block: "{END_TEST_DELIMITER}"', (filename, index+1, 1, line))

            try:
                with open(script_filename_string, 'r') as f:
                    attributes['script_content'] = f.read()
                
                tests.append(attributes)
            except FileNotFoundError:
                print(f'No such file or directory: \'{script_filename_string}\'')

        elif type == 'approved_includes':
            # go to next line
            index,line = goto_next_line(index, lines, filename)
            
            # expect start of test block
            if line != BEGIN_TEST_DELIMITER:
                # filename lineno offset text
                raise SyntaxError(f'missing expected start of test block: "{BEGIN_TEST_DELIMITER}"', (filename, index+1, 1, line))
            
            # go to next line
            index,line = goto_next_line(index, lines, filename)
            
            while line != END_TEST_DELIMITER:
                attributes['approved_includes'].append(line)
                index,line = goto_next_line(index, lines, filename)
            
            tests.append(attributes)
            
        else:
            #raise ValueError('undefined test type: {}'.format(type))
            print('WARNING: undefined test type: {}.  this one will be ignored: {}'.format(type, attributes['name']))
            index,line = eat_block_of_test(index, lines, filename)
                
        index += 1
    
    return tests

def write_unit_test(test: Attributes) -> None:
    with open('unit_test.cpp', 'wt') as f:
        f.write(f"#include \"{test['target']}\"\n\n")    
        if len(test['include']) > 0:
            for include in test['include'].split():
                f.write(f'#include {include}\n')
        f.write('#include "cs12x_test.h"\n')    

        f.write('int main() {\n')
        f.write('    INIT_TEST;\n')
        f.write('    {}\n'.format('\n    '.join(test['code'].splitlines())))
        f.write('    RESULT(pass);\n')
        f.write('    return pass ? 0 : 1;\n')
        f.write('}\n')

def write_performance_test(test: Attributes) -> None:
    with open('performance_test.cpp', 'wt') as f:
        f.write(f"#include \"{test['target']}\"\n\n")
        f.write('#include<iostream>\n')
        f.write('#include<chrono>\n')
        if len(test['include']) > 0:
            for include in test['include'].split():
                f.write(f'#include {include}\n')
        f.write('#include "cs12x_test.h"\n')

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

def compile_X_test(name: str, src: str = '') -> Tuple[bool,str]:
    CXX = 'g++'
    FLAGS = f'-std=c++17 -g -o {name}'
    if src:
        SRC = src
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
    return compile_X_test('unit_test')

def compile_performance_test() -> Tuple[bool,str]:
    return compile_X_test('performance_test')

def compile_io_test(src_target) -> Tuple[bool,str]:
    return compile_X_test('io_test', src_target)

def compile_script_test() -> Tuple[bool,str]:
    return True, ""
    
def compile_approved_includes_test() -> Tuple[bool,str]:
    return True, ""
    
def run_unit_test(timeout: float) -> Tuple[bool,str]:
    run_cmd = ["./unit_test", "2>&1"]
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

def run_io_test(timeout: float) -> Tuple[bool,str]:
    run_cmd = ["./io_test", "2>&1"]
    with open('input.txt', 'r') as file:
        input_data = file.read()
    p = subprocess.Popen(run_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    output_str = ""
    err_str = ""
    gt_string = ""
    message_to_student = ""

    try:
        output, err = p.communicate(input_data.encode('utf-8'), timeout=timeout)
        output_str = output.decode('utf-8').rstrip()
        err_str = err.decode('utf-8')

        with open('output.txt', 'r') as file:
            gt_string = file.read().replace('\r', '').rstrip()
        message_to_student = "Your output: " + output_str + "\n"
        message_to_student += "\n\n"
        message_to_student += "Expected output: " + gt_string + "\n"

    except subprocess.TimeoutExpired as e:
        output_str = "Timeout during test execution, check for an infinite loop\n"
        message_to_student += output_str
    except Exception as e:
        output_str = str(e)
        message_to_student += output_str

    return (output_str == gt_string), message_to_student

def run_script_test(timeout: float) -> Tuple[bool,str,float]:

    #print("Can write: ")
    #print(os.access('./', os.W_OK))

    if os.path.exists('./DEBUG'):
        os.remove('./DEBUG')
    if os.path.exists('./OUTPUT'):
        os.remove('./OUTPUT')

    cmd = ["bash ./script.sh"]
    #print('cmd = {}'.format(cmd))
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, shell=True)
    # p = popen(cmd)
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
            raise FileNotFoundError('./OUTPUT')

        if os.path.exists('./DEBUG'):
            with open('./DEBUG', 'r') as file:
                debug_string = "Debug:\n" + file.read()
                #print("Debug: ")
                #print(debug_string)

        score = float(output_string)
    except subprocess.TimeoutExpired as e:
        debug_string = "Timeout during test execution, check for an infinite loop\n"

    return (score > 0.0), debug_string, score

def run_approved_includes_test(timeout: float) -> Tuple[bool,str,float]:
    return run_script_test(timeout)

def check_approved_includes(target: str, approved_includes: List[str]) -> Tuple[bool,str]:
    
    cmd = ["bash"]
    #print('cmd = {}'.format(cmd))
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # p = popen(cmd)
    output, err = p.communicate("./approved_includes.sh {} {}".format(target, ' '.join(approved_includes)).encode('utf-8'))
    output_str = output.decode('utf-8')
    err_str = err.decode('utf-8')
    # try:
    #     output = p.stdout.decode('utf-8')
    # except Exception as e:
    #     output = str(e)
    forbidden_found = False
    if "FORBIDDEN" in output_str:
        forbidden_found = True
    return forbidden_found, output_str

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

def main(filename) -> Result:
    result_score = 0.0
    test_results: List[TestResult] = list()
    tests = read_tests(filename)
    possible = 0.0
    total_time = 0.0
    unapproved_includes = False
    for test in tests:
        max_points = float(test['points'])
        possible += max_points
        print(f"test: {test['name']}")
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
        else:
            print("[INFO] Unsupported test")
            continue
        compile_output, run_output = '',''
        if test['type'] == 'unit':
            compiles, compile_output = compile_unit_test()
        elif test['type'] == 'i/o':
            compiles, compile_output = compile_io_test(test['target'])
        elif test['type'] == 'script':
            compiles, compile_output = compile_script_test()
        elif test['type'] == 'performance':
            compiles, compile_output = compile_performance_test()
        elif test['type'] == 'approved_includes':
            compiles, compile_output = compile_approved_includes_test()
        else:
            print("[INFO] Unsupported test")
            continue
        if compiles:
            runs, run_output, point_multiplier = True, '', 100.0
            point_multiplier = 100.0
            timeout = float(test['timeout'])
            time_start = time()
            if test['type'] == 'unit':
                runs, run_output = run_unit_test(timeout)
            elif test['type'] == 'i/o':
                runs, run_output = run_io_test(timeout)
            elif test['type'] == 'script':
                runs, run_output, point_multiplier = run_script_test(timeout)
            elif test['type'] == 'performance':
                runs, run_output = run_performance_test(timeout)
            elif test['type'] == 'approved_includes':
                runs, run_output, point_multiplier = run_approved_includes_test(timeout)
                if not runs:
                    unapproved_includes = True
            else:
                print("[INFO] Unsupported test")
                continue
            time_end = time()
            total_time += time_end - time_start
            
            if runs:
                if point_multiplier < 100.0:
                    print(f"[PASS - PARTIAL] ran correctly, but only recieved {point_multiplier:0.2f}% partial credit\n")    
                else:
                    print('[PASS] ran correctly\n')
                points = max_points * (point_multiplier / 100.0)
            else:
                print('[FAIL] incorrect behavior\n')
                #print(run_output.strip())
                #print()
                points = 0
            
        else:
            print('[FAIL] failed to compile\n')
            #print(compile_output)
            points = 0
        
        result_score += points
        
        test_result: TestResult = {
            'number': test['number'],
            'name': test['name'],
            'score': points,
            'max_score': max_points,
            'output': '',
            'tags': None,
            'visibility': None,
            'extra_data': None
            }
        
        if test['show_output'].lower() == 'true':
            has_compile_output = len(compile_output) > 0
            if has_compile_output:
                test_result['output'] += compile_output.strip()
            if len(run_output) > 0:
                if has_compile_output > 0:
                    test_result['output'] += '\n\n'
                test_result['output'] += run_output.strip()
        else:
            test_result['output'] = 'Output is intentionally hidden'
        
        test_results.append(test_result)
    
    '''
    targets = set()
    for test in tests:
        targets.add(test['target'])
    
    # TODO: integrate approved includes test into standard test processing (above)
    unapproved_includes = False  
    for target in targets: 
        print(f'test: approved includes for {target}')
        list_of_approved_includes = list()
        try:
            with open(f'approved_includes_{target}') as f:
                for line in f:
                    list_of_approved_includes.append(line.strip())
        except FileNotFoundError:
            print('[WARNING] approved_includes_{} not found: assuming default deny all'.format(target))
        
        forbidden_found, output = check_approved_includes(target, list_of_approved_includes)
        ai_test_result: TestResult = {
            'number':'00',
            'name': f'Approved includes for {target}',
            'score': 0,
            'max_score': 0,
            'output': output.strip(),
            'tags': None,
            'visibility': None,
            'extra_data': None
            }
        if (forbidden_found):
            print('[FAIL] found a forbidden include\n')
            print(output)
            #test_result['score'] = 0
            #print(test_result['score'])
            unapproved_includes = True
        else:
            print('[PASS] all includes are approved\n')
        test_results.append(ai_test_result)
        result_score += ai_test_result['score']
    '''
    
    result_output = ''
    if unapproved_includes:
        result_score = 0
        result_output = 'Forbidden includes are used, so we set your current submission score to 0.0'
        earned = 0
    
    # DISABLE SCORING FROM AUTOGRADER
    # results_score = 0
    
    #results['execution_time'] = total_time
    
    #results['visibility'] = 'visible'
    #results['stdout_visibility'] = 'visible'
    # if results['visibility'] == 'visible' or results['stdout_visibility'] == 'visible':
    #     print('###########################')
    #     print('#                         #')
    #     print('# WARNING WARNING WARNING #')
    #     print('#                         #')
    #     if results['visibility'] == 'visible':
    #         print('# TESTS ARE VISIBLE       #')
    #     if results['stdout_visibility'] == 'visible':
    #         print('# STDOUT IS VISIBLE       #')
    #     print('#                         #')
    #     print('###########################')
    #results['extra_data'] = dict()
    #results['tests'] = test_results
    #results['leaderboard'] = leaderboard
    
    t = int(result_score * 10000 + 0.5)
    result_score = t / 10000
    
    print('###########################')
    print('#                         #')
    print('# points: {:6.2f} / {:6.2f} #'.format(result_score,possible))
    print('#                         #')
    print('###########################')
    
    results: Result = {
        'score': result_score,
        'output': result_output,
        'execution_time': total_time,
        'visibility': 'visible',
        'stdout_visibility': 'visible',
        'tests': test_results
        }
    
    return results
    

if __name__ == '__main__':
    results_filename = 'results.json'
    if len(argv) == 1:
        tests_filename = input('path to tests: ')
    else:
        tests_filename = argv[1]
        if len(argv) > 2:
            # path to results.json (e.g. /autograder/results/results.json) is optional 2nd arg
            results_filename = argv[2]
    results = main(tests_filename)
    #print(json.dumps(results, sort_keys=True, indent=4))
    with open(results_filename,'wt') as f:
        json.dump(results, f, sort_keys=True, indent=4)

    if os.path.exists('/autograder/'):
        # running on gradescope
        previousMaxScore = 0.0
        with open('/autograder/submission_metadata.json', 'r') as f:
            previousResultJson = json.load(f)
            for prevSubmission in previousResultJson['previous_submissions']:
                previousScore = float(prevSubmission["score"])
                if (previousScore > previousMaxScore):
                    previousMaxScore = previousScore

        with open('/autograder/results/results.json', 'r') as f:
            currentResult = json.load(f)

        if (previousMaxScore > float(currentResult['score'])):
            currentResult["output"] +="\n"
            currentResult["output"] += "Your current submission's score was " + str(float(currentResult["score"])) + ", however you get to keep your maximum submission score of " + str(previousMaxScore)
            currentResult['score'] = previousMaxScore

        with open('/autograder/results/results.json', 'w') as f:
            json.dump(currentResult, f)
    # else running on local so no need to compute max score