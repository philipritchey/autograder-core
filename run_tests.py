#! /usr/bin/env python3

'''
TODO(pcr):
* move configuration stuff to configuration file (and let it be assignment-specific)
* refine attribute requirements
* add command line option to run a specific test or set of tests
* use @target attribute for coverage tests and some other test(s) that don't use it but could/should
'''

from typing import List
from os.path import exists as path_exists
import json
from argparse import ArgumentParser, Namespace
from config import DEFAULT_STDOUT_VISIBILITY, DEFAULT_VISIBILITY, OCTOTHORPE_LINE, OCTOTHORPE_WALL
from results import Result, TestResult
from test_parsing import read_tests

def main(args: Namespace) -> Result:
    filename: str = args.tests_path
    test_number: str = args.tests
    debugmode: bool = args.debugmode
    if debugmode:
        print('===DEBUGMODE===')

    result_score: float = 0.0
    test_results: List[TestResult] = list()
    #extra_data: Optional[ExtraData] = None
    #leaderboard: Optional[LeaderboardEntry] = None

    try:
        tests = read_tests(filename)
    except Exception as err:
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


    if test_number != '*':
        # run only those tests with number that matches test_number
        #   '5' means run all tests numbered 5: 5[.1, 5.2, ...]
        #   '5.2' means run all tests numbered 5.2: 5.2[.1, 5.2.2, ...]
        for test in tests:
            if test['number'] == test_number or (test['number'].startswith(test_number) and (len(test['number']) == len(test_number) or test['number'][len(test_number)] == '.')):
                test['skip'] = False
            else:
                test['skip'] = True


    unapproved_includes = False
    sufficient_coverage = True
    possible = 0.0
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
        possible += max_points

        write_test(test)

        status = 'created'

        compiles, compile_output = compile_test(test)

        status = 'compiled'

        failed_to_compile = not compiles
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

    results: Result = {
        'score': recorded_score,
        'output': result_output,
        'execution_time': total_time,
        'visibility': DEFAULT_VISIBILITY,
        'stdout_visibility': DEFAULT_STDOUT_VISIBILITY,
        'tests': test_results
        }

    #if extra_data:
    #    results['extra_data'] = dict()
    #if leaderboard:
    #    results['leaderboard'] = leaderboard

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
    parser = ArgumentParser()
    parser.add_argument('tests_path', type=str, help='path to tests (input)')
    parser.add_argument('-r', '--results_path', type=str, default='results.json', help='path to results (output) [default=./results.json]')
    parser.add_argument('-d', '--debugmode', help='force show test output', action='store_true')
    parser.add_argument('-t', '--tests', type=str, default='*', help='test(s) to run by prefix [default=*]')
    parser.add_argument('-l', '--language', type=str, default='c++', help='supported languages: c++, java')

    args = parser.parse_args()

    results_filename = args.results_path
    language = args.language

    results: Result = {
        'score': 0,
        'output': '',
        'execution_time': 0,
        'visibility': DEFAULT_VISIBILITY,
        'stdout_visibility': DEFAULT_STDOUT_VISIBILITY,
        'tests': []
        }

    if language == 'c++':
        from test_writing_cpp import write_test
        from test_compiling_cpp import compile_test
        from test_running_cpp import run_test

        results = main(args)

    elif language == 'java':
        from test_writing_java import write_test
        from test_compiling_java import compile_test
        from test_running_java import run_test

        results = main(args)

    else:
        results['output'] = f'Unsupported Language: {language}'
        results['visibility'] = 'visible'
        results['stdout_visibility'] = 'visible'

    #print(json.dumps(results, sort_keys=True, indent=4))
    with open(results_filename,'wt') as f:
        json.dump(results, f, sort_keys=True, indent=4)


    # keep max score over all previous submissions
    if path_exists('/autograder/'):
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
