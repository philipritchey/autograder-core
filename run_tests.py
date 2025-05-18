#! /usr/bin/env python3

'''
TODO(pcr):
* move configuration stuff to configuration file (and let it be assignment-specific)
* refine attribute requirements
* add command line option to run a specific test or set of tests
* use @target attribute for coverage tests and some other test(s) that don't use it but could/should
'''

from typing import List, Dict, Any, Tuple
from os.path import exists as path_exists
import json
from argparse import ArgumentParser, Namespace
from config import DEFAULT_STDOUT_VISIBILITY, DEFAULT_VISIBILITY, OCTOTHORPE_LINE, OCTOTHORPE_WALL,\
    SNARKY_SUBMISSION_SCORE_THRESHHOLD
from results import Result, TestResult
from test_parsing import read_tests
from attributes import Attributes

 # these are importable once all the files are collected in the testbox
from test_writing import write_test
from test_compiling import compile_test
from test_running import run_test

def print_results(params: Dict[str, Any]) -> None:
    '''
    pretty-print the results
    '''
    test_results = params['test_results']
    unapproved_includes = params['unapproved_includes']
    sufficient_coverage = params['sufficient_coverage']
    possible = params['possible']
    result_score = params['result_score']
    recorded_score = params['recorded_score']

    passed = 0
    failed = 0
    partial = 0
    for test_result in test_results:
        status = test_result['status']
        if status == 'passed':
            passed += 1
        elif status == 'failed':
            failed += 1
        elif status == 'partial':
            partial += 1

    result_score = int(result_score * 10000 + 0.5) / 10000
    str_score = f'{result_score:6.2f}'
    str_possible = f'{possible:6.2f}'

    print(OCTOTHORPE_LINE)
    print(OCTOTHORPE_WALL)
    print(f'# {len(test_results):3d} tests {" "*13} #')
    print(f'#   {passed:3d} passed            #')
    print(f'#   {partial:3d} partial           #')
    print(f'#   {failed:3d} failed            #')
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

def apply_test_filter(test_number: str, tests: List[Attributes]) -> None:
    '''
    run only those tests with number that matches test_number
      '*' means run all tests
      '5' means run all tests numbered 5: 5[.1, 5.2, ...]
      '5.2' means run all tests numbered 5.2: 5.2[.1, 5.2.2, ...]
    '''
    if test_number != '*':
        for test in tests:
            if (test['number'] == test_number or
                (test['number'].startswith(test_number) and
                 (len(test['number']) == len(test_number) or
                  test['number'][len(test_number)] == '.'
                 )
                )
               ):
                test['skip'] = False
            else:
                test['skip'] = True

def possible_points(tests: List[Attributes]) -> float:
    '''
    sum of all possible points
    '''
    possible = 0.0
    for test in tests:
        if not test['skip']:
            possible += test['points']
    return possible

def main(args: Namespace) -> Result:
    '''
    read, write, compile, run, and collect results of all tests.
    '''

    filename: str = args.tests_path
    test_number: str = args.tests
    debugmode: bool = args.debugmode
    if debugmode:
        print('===DEBUGMODE===')
        print(f'filename: {filename}')
        print(f'test_number: {test_number}')

    result_score: float = 0.0
    test_results: List[TestResult] = list()
    #extra_data: Optional[ExtraData] = None
    #leaderboard: Optional[LeaderboardEntry] = None

    try:
        tests = read_tests(filename)
    except(SyntaxError, KeyError, ValueError) as err:
        fail_result: Result = {
            'score': 0.0,
            'output': repr(err),
            'execution_time': 0.0,
            'visibility': 'visible',
            'stdout_visibility': 'visible',
            'tests': []
        }
        print('[FATAL] Error occured while reading tests:')
        print(err)
        return fail_result

    if debugmode:
        print(f'read {len(tests)} tests')

    apply_test_filter(test_number, tests)

    if debugmode:
        print(f'{len([test for test in tests if not test["skip"]])} tests will be run')

    unapproved_includes = False
    sufficient_coverage = True
    total_time = 0.0
    for test in tests:
        if test['skip']:
            #print(f"test {test['number']}: {test['name']}\n[SKIP]")
            continue

        print(f"test {test['number']}: {test['name']}")

        max_points = test['points']
        status = 'pre-write'
        compile_output = str()
        run_output = str()

        write_test(test)

        status = 'created'

        compiles, compile_output = compile_test(test)

        status = 'compiled'

        if compiles:
            result = run_test(test)

            run_output = result['run_output']
            points = result['points']

            if 0 < points < max_points:
                status = "partial"
            elif points >= max_points:
                status = "passed"
            else:  # points <= 0
                status = 'failed'

            if result['unapproved_includes']:
                status = 'failed'
                unapproved_includes = True

            if not result['sufficient_coverage']:
                status = 'failed'
                sufficient_coverage = False

            total_time += result['run_time']
        else:
            print('[FAIL] failed to compile\n')
            status = 'failed'
            points = 0
            run_output = ''

        result_score += points

        test_result: TestResult = {
            'number': test['number'],
            'name': test['name'],
            'score': points,
            'max_score': max_points,
            'status': status,
            'output': '',
            'tags': [],
            'visibility': test['visibility'],
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
            if not compiles:
                test_result['output'] += 'Failed to compile.\n'
            test_result['output'] += 'Output is intentionally hidden'

        test_results.append(test_result)

    recorded_score = result_score
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

    print_results(
        {
            'test_results': test_results,
            'unapproved_includes': unapproved_includes,
            'sufficient_coverage': sufficient_coverage,
            'possible': possible_points(tests),
            'result_score': result_score,
            'recorded_score': recorded_score
        })

    #if extra_data:
    #    results['extra_data'] = dict()
    #if leaderboard:
    #    results['leaderboard'] = leaderboard

    return Result(
        {
            'score': recorded_score,
            'output': result_output,
            'execution_time': total_time,
            'visibility': DEFAULT_VISIBILITY,
            'stdout_visibility': DEFAULT_STDOUT_VISIBILITY,
            'tests': test_results
        }
    )

def snarky_comment_about_number_of_submissions(num_submissions: int) -> str:
    '''
    make a snarky comment based on their number of submissions
    '''
    comment = "I'm not even mad, that's amazing."
    if num_submissions < 4:
        comment = (
            "That's OK.  Make sure that you reflect on the feedback and think before you code.  "
            "Before making another submission, write test cases to reproduce the errors and then "
            "use your favorite debugging technique to isolate and fix the errors.  You can do it!")
    elif num_submissions < 7:
        comment = (
            "You should take some time before your next submission to think about the errors and "
            "how to fix them.  Start by reproducing the errors with test cases locally.")
    elif num_submissions < 10:
        comment = (
            "Why don't you take a break, take a walk, take nap, and come back to this "
            "after you've had a chance to think a bit more.  "
            "Remember: start by reproducing the error, then isolate it and fix it.")
    elif num_submissions < 15:
        comment = (
            "It looks like you're having difficulty finding and fixing your errors.  "
            "You should come to office hours.  We can help you.")
    elif num_submissions < 20:
        comment = (
            "If you haven't gone to office hours yet, you really should.  "
            "We want to help you.  How's your coverage?  You can't test what you don't cover.")
    elif num_submissions < 30:
        comment = (
            "Did you know that you can not only compile locally, but you can also test locally?  "
            "You should try it.")
    elif num_submissions < 40:
        comment = (
            "literally nobody: \n"
            "             you: autograder go brrr.")
    elif num_submissions < 50:
        comment = (
            "I'm almost out of snarky ways to comment on how many submissions you've made.  "
            "That's how many submissions you've made.")
    elif num_submissions < 75:
        comment = (
            "Big yikes.  No cap, fam, take several seats.  This ain't it, chief.  "
            "Your code and development process are sus AF.  Periodt.")
    elif num_submissions < 100:
        comment = "Your number of submissions to this assignment is too damn high."
    return comment + '\n'

def ordinal_suffix(number: int) -> str:
    '''
    determine the ordinal suffix for the given integer, e.g. 1st, 2nd, 3rd, 4th, etc.
    '''
    if 10 < number < 20:
        return "th"
    return ["th", "st", "nd", "rd", "th", "th", "th", "th", "th", "th"][number % 10]

def get_command_line_args() -> Namespace:
    '''
    parse the command line arguments.
    '''
    parser = ArgumentParser()
    parser.add_argument(
        'tests_path',
        type=str,
        help='path to tests (input)')
    parser.add_argument(
        '-r',
        '--results_path',
        type=str,
        default='results.json',
        help='path to results (output) [default=./results.json]')
    parser.add_argument(
        '-d',
        '--debugmode',
        help='force show test output',
        action='store_true')
    parser.add_argument(
        '-t',
        '--tests',
        type=str,
        default='*',
        help='test(s) to run by prefix [default=*]')
    parser.add_argument(
        '-l',
        '--language',
        type=str,
        default='c++',
        help='supported languages: c++, java')

    return parser.parse_args()

def get_max_score() -> float:
    '''
    find the max score overall previous submissions.
    '''
    previous_max_score = 0.0
    with open('/autograder/submission_metadata.json', 'r') as file:
        previous_result_json = json.load(file)
        for previous_submission in previous_result_json['previous_submissions']:
            previous_score = float(previous_submission["score"])
            if previous_score > previous_max_score:
                previous_max_score = previous_score

    return previous_max_score

def keep_max_score(current_result: Any) -> None:
    '''
    override the score in the current result with the max score over all submissions.
    '''
    previous_max_score = get_max_score()
    if previous_max_score > float(current_result['score']):
        current_result["output"] += "\n"
        current_result["output"] += (
            f'Your current submission\'s score was {float(current_result["score"]):0.2f},'
            f' however you get to keep your maximum submission score of {previous_max_score:0.2f}'
            '\n')
        current_result['score'] = previous_max_score

def get_number_of_submissions_and_total_points() -> Tuple[int, float]:
    '''
    count the number of submissons and get the total points for the assignment.
    '''
    submission_cnt = 0
    total_points = 100.0
    with open('/autograder/submission_metadata.json', 'r') as file:
        previous_result_json = json.load(file)
        total_points = float(previous_result_json['assignment']['total_points'])
        submission_cnt = len(previous_result_json['previous_submissions'])

    return submission_cnt + 1, total_points

def report_submission_count(current_result: Any) -> None:
    '''
    add a message about the number of submissions to the results object.
    '''
    submission_cnt, total_points = get_number_of_submissions_and_total_points()
    current_result["output"] += (
        f"This is your {submission_cnt}{ordinal_suffix(submission_cnt)} submission.\n")
    if current_result['score'] < total_points * SNARKY_SUBMISSION_SCORE_THRESHHOLD:
        current_result["output"] += snarky_comment_about_number_of_submissions(submission_cnt)

def running_on_gradescope() -> bool:
    '''
    return true if we think we are in a gradescope container.
    '''
    return path_exists('/autograder/')

def read_results_from_file(filename: str) -> Any:
    '''
    read results (should be a Dict) from file.
    '''
    with open(filename, 'r') as file:
        results = json.load(file)
    return results

def write_results_to_file(results: Any, filename: str) -> None:
    '''
    write results (should be a Dict) to file.
    '''
    with open(filename, 'wt') as file:
        json.dump(results, file, sort_keys=True, indent=4)

def run_autograder() -> None:
    '''
    do the main-main autograding process.
    '''
    args = get_command_line_args()

    results_filename = args.results_path
    language = args.language

    # in case of resource exhaustion, pre-write a results file
    kill_mssg = '''
        the autograding process was killed,
        probably because it ran out of memory,
        probably because of too much output,
        probably because of a print statement in an infinite loop.
        check your code for infinite loops and other code that might print too much.
        '''
    results: Result = {
        'score': 0.0,
        'output': kill_mssg,
        'execution_time': 0.0,
        'visibility': 'visible',
        'stdout_visibility': 'visible',
        'tests': []
        }

    if running_on_gradescope():
        keep_max_score(results)
        write_results_to_file(results, '/autograder/results/results.json')

    original_language = language
    if language.lower() in ('c++', 'cpp', 'java', 'python'):
        # read, write, compile, and run tests
        results = main(args)

    else:
        # TODO(pcr): does this need to be student-facing? no, right?
        results['output'] = f'Unsupported Language: {original_language}'
        results['visibility'] = 'visible'
        results['stdout_visibility'] = 'visible'

    write_results_to_file(results, results_filename)

    if running_on_gradescope():
        current_result = read_results_from_file('/autograder/results/results.json')
        keep_max_score(current_result)
        report_submission_count(current_result)
        write_results_to_file(current_result, '/autograder/results/results.json')

if __name__ == '__main__':
    run_autograder()
