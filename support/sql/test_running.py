from os.path import exists as path_exists
from os import remove
import subprocess
from time import time
from typing import Tuple
from attributes import Attributes

from config import JAVA_CLASSPATH, TIMEOUT_MSSG
from results import PartialTestResult
from test_types import UnsupportedTestException
import mysql.connector


def parse_test(test):
    test_details = {}
    lines = test['code'].split('\n')
    for l in lines:
        broken = l.strip().split(':')
        if len(broken) == 2:
            test_details[broken[0].strip()] = broken[1].strip()

    if "ordered" in test_details.keys():
        if test_details['ordered'] == 'true':
            test_details['ordered'] = True
        else:
            test_details['ordered'] = False
    else:
        test_details['ordered'] = False
        
    return test_details

def run_script(timeout: float, database:str, filename:str, statement = None, ordered = None):
    cnx = mysql.connector.connect(user='root', password='',
                              host='127.0.0.1',
                              database=database)

    results = []
    f = open(filename)
    lines = f.read().split('\n')
    for i in range(len(lines)):
        start = lines[i].find('-- ')
        if start != -1:
            lines[i] = lines[i][:start]
    
    new_lines = ""
    for l in lines:
        new_lines = new_lines + ' ' + l
    stmts = new_lines.split(';')

    with cnx.cursor() as cursor:
        if statement == None:
            for stmt in stmts:
                if stmt.strip() != "":
                    cursor.execute(stmt)
                    results.append(cursor.fetchall())
        else:
            stmt = stmts[int(statement) - 1]
            
            if stmt.strip() != "":
                if ordered:
                    words = stmt.split()
                    words_lower = []
                    for w in words:
                        words_lower.append(w.strip().lower())
                    if 'order' in words_lower and 'by' in words_lower:
                        cursor.execute(stmt)
                        x = cursor.fetchall()
                        results.append(x)
                    else:
                        results.append([('No order caluse in ordered query','')])
                else:
                    cursor.execute(stmt)
                    results.append(cursor.fetchall())

    cnx.close()
    return results

def run_statement(timeout: float, database:str, statement:str):
    cnx = mysql.connector.connect(user='root', password='',
                              host='127.0.0.1',
                              database=database)

    results = []
    stmts = [statement]

    with cnx.cursor() as cursor:
        for stmt in stmts:
            if stmt.strip() != "":
                cursor.execute(stmt)
                results.append(cursor.fetchall())
    cnx.close()

    return results

def result_to_set(list_of_list_of_tuples_of_strings, ordered = False):
    results = []
    for list_of_tuples_of_strings in list_of_list_of_tuples_of_strings:
        if ordered:
            result = []
        else:
            result = set()
        
        for tuple_of_strings in list_of_tuples_of_strings:
            o = ""
            for a_string in tuple_of_strings:
                o += str(a_string) + ', '
            if ordered:
                result.append(o)
            else:
                result.add(o)

        results.append(result)

    return results

def listOfSetToString(lstOSets):
    out = ""
    for aSet in lstOSets:
        for element in aSet:
            out += element + '\n'
        out += '\n\n'
    
    return out

def run_scripts(timeout: float, scripts, test_details, override_db = None):
    scripts = scripts.split(',')
    if 'statement' in test_details.keys(): 
        for t in scripts[:-1]:
            if override_db is None:
                return run_script(timeout, test_details['database'] , t.strip())
            else:
                return run_script(timeout, override_db , t.strip())
        
        t = scripts[-1]
        if override_db is None:
            return run_script(timeout, test_details['database'] , t.strip(), statement = test_details['statement'], ordered = test_details['ordered'])
        else:
            return run_script(timeout, override_db , t.strip(), statement = test_details['statement'], ordered = test_details['ordered'])

    else:
        results = []
        for t in scripts:
            if override_db is None:
                results = results + run_script(timeout, test_details['database'] , t.strip())
            else:
                results = results + run_script(timeout, override_db , t.strip())
        return results

def run_sql_test(timeout: float, test: Attributes, test_details) -> Tuple[bool,str]:
    try:
        # run setup
        run_script(timeout, '', test_details['setup'])

        # run solution before student corrupts data.
        if 'solution' in test_details.keys():
            expected = run_scripts(timeout, test_details['solution'] , test_details)
            expected = result_to_set(expected, test_details["ordered"]) 
        
        # run student
        
        actual = run_scripts(timeout, test['target'], test_details)
        actual = result_to_set(actual, test_details['ordered'])

        # match of solution exists   
        if 'solution' in test_details.keys():
            if (actual == expected):
                return True, ""        
            else:
                out = "Expected : \n"
                out += listOfSetToString(expected)
                out += "\n\nGot : \n"
                out += listOfSetToString(actual)
                return False, out
        
        else:
            out = "Got : \n"
            out += listOfSetToString(actual)
            return True, out

    except Exception as e:
        return False, str(e)

def run_table_populate_test(timeout: float, test: Attributes, test_details) -> Tuple[bool,str]:
    try:
        run_script(timeout, '', test_details['setup'])
        run_scripts (timeout, test['target'], test_details)
        actual = run_statement(timeout, test_details['database'] , "Select * from " + test_details['tablename'] + ";")
        
        run_script(timeout, '', test_details['setup_sol'])
        expected = run_statement(timeout, test_details['database_sol'] , "Select * from " + test_details['tablename_sol'] + ";")

        actual = result_to_set(actual)
        expected = result_to_set(expected)

        if (actual[0] == expected[0]):
            return True, ""
        
        else:
            out = "Expected : \n"
            for i in expected[0]:
                out += str(i) + '\n'
            
            out += "\n\nGot : \n"
            for i in actual[0]:
                out += str(i) + '\n'


            return False, out

    except Exception as e:
        return False, str(e)

def run_db_name_test(timeout: float, test: Attributes, test_details) -> Tuple[bool,str]:
    try:
        run_scripts (timeout, test['target'], test_details, override_db = "")
        result = run_statement(timeout, '', 'show databases;')

        for x in result[0]:
            if x[0].lower().strip() == test_details['database'].lower().strip() :
                return True, ''

        return False, 'database ' + test_details['database'] + ' not created.'
    except Exception as e:
        return False, str(e)

def run_table_exists_test(timeout: float, test: Attributes, test_details) -> Tuple[bool,str]:
    try:
        if 'setup' in test_details.keys():
            run_script(timeout, '', test_details['setup'])   

        run_scripts (timeout, test['target'], test_details, override_db = "")
        result = run_statement(timeout, test_details['database'], 'show tables;')

        for x in result[0]:
            if x[0].lower().strip()  == test_details['tablename'].lower().strip() :
                return True, ''

        return False, 'Table ' + test_details['tablename'] + ' not found in database ' + test_details['database'] + '.'
    except Exception as e:
        return False, str(e)

def make_set(l, column_no = None):
    s = set()
    for v in l:
        if column_no == None:
            s.add(v.lower().strip())
        else:
            s.add(v[column_no].lower().strip())
    return s

def run_table_column_names_test(timeout: float, test: Attributes, test_details) -> Tuple[bool,str]:
    try:
        if 'setup' in test_details.keys():
            run_script(timeout, '', test_details['setup'])            

        run_scripts (timeout, test['target'], test_details, override_db = "")
        result = run_statement(timeout, test_details['database'], 'describe ' + test_details['tablename'].upper() + ';')

        cols_expected = make_set(test_details['columns'].split(','))
        cols_actual = make_set(result[0], 0)

        if cols_actual == cols_expected:
            return True, ""
        else:
            return False, 'Expected : ' + str(cols_expected) + '\n Got : ' +  str(cols_actual) + '\n'
    
    except Exception as e:
        return False, str(e)

def run_table_primary_key_test(timeout: float, test: Attributes, test_details) -> Tuple[bool,str]:
    try:
        if 'setup' in test_details.keys():
            run_script(timeout, '', test_details['setup'])   

        run_scripts (timeout, test['target'], test_details, override_db = "")
        stmt =  "SELECT COLUMN_NAME FROM KEY_COLUMN_USAGE " + \
                "WHERE TABLE_SCHEMA = '" + test_details['database'] + "' " + \
                "AND TABLE_NAME = '" + test_details['tablename'].upper() + "' " + \
                "AND CONSTRAINT_NAME = 'PRIMARY';" 
        result = run_statement(timeout, 'information_schema', stmt)

        cols_expected = make_set(test_details['columns'].split(','))
        cols_actual = make_set(result[0], 0)

        if cols_actual == cols_expected:
            return True, ""
        else:
            return False, 'Expected : ' + str(cols_expected) + '\n Got : ' +  str(cols_actual) + '\n'
    
    except Exception as e:
        return False, str(e)

def run_table_foreign_key_test(timeout: float, test: Attributes, test_details) -> Tuple[bool,str]:
    try:
        if 'setup' in test_details.keys():
            run_script(timeout, '', test_details['setup'])   

        run_scripts (timeout, test['target'], test_details, override_db = "")
        stmt =  "SELECT REFERENCED_COLUMN_NAME FROM KEY_COLUMN_USAGE " + \
                "WHERE TABLE_SCHEMA = '" + test_details['database'] + "' " + \
                "AND TABLE_NAME = '" + test_details['tablename'].upper() + "' " + \
                "AND referenced_table_name = '" + test_details['referenced_table'].upper() + "' "\
                "AND COLUMN_NAME = '" + test_details['columns'].upper().strip() + "';" 
        
        result = run_statement(timeout, 'information_schema', stmt)

        cols_expected = make_set(test_details['referenced_columns'].split(','))
        cols_actual = make_set(result[0], 0)

        if cols_actual == cols_expected:
            return True, ""
        else:
            return False, 'Expected : ' + str(cols_expected) + '\n Got : ' +  str(cols_actual) + '\n'
    
    except Exception as e:
        return False, str(e)

def run_table_check_constraint_test(timeout: float, test: Attributes, test_details) -> Tuple[bool,str]:
    try:
        if 'setup' in test_details.keys():
            run_script(timeout, '', test_details['setup'])   
            
        run_scripts (timeout, test['target'], test_details, override_db= "")

        if 'allowed_inserts' in test_details.keys():
            try:
                run_script(timeout, '', test_details['allowed_inserts'])
            except Exception as e:
                return False, 'Allowed insert failed with error : ' + str(e)

        if 'forbidden_inserts' in test_details.keys():
            try:
                run_script(timeout, '', test_details['forbidden_inserts'])
                return False, 'Invalid data inserted sucessfully'
            except Exception as e:
                out = str(e)
                if ('3819' in out):
                    return True, ""
                else:
                    return False, out    
        
        return True, ""
    
    except Exception as e:
        return False, str(e)

def run_test(test: Attributes) -> PartialTestResult:
    # get test characteristics
    max_points = float(test['points'])
    runs = True
    point_multiplier = 100.0
    unapproved_includes = False
    sufficient_coverage = True
    timeout = float(test['timeout'])
    time_start = time()

    # start db
    run_cmd = ["service", "mysql", "start"]
    p = subprocess.Popen(run_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        _, output_err = p.communicate(timeout=timeout)
        output = output_err.decode('utf-8')
    except Exception as e:
        output = str(e)
        exit("DB failed to start 2")

    # Actual running starts here 
    test_details = parse_test(test)

    if test_details['type'] == 'sql':
        runs, run_output = run_sql_test(timeout, test, test_details)
    elif test_details['type'] == 'db_name':
        runs, run_output = run_db_name_test(timeout, test, test_details)
    elif test_details['type'] == 'table_exists':
        runs, run_output = run_table_exists_test(timeout, test, test_details)
    elif test_details['type'] == 'table_column_names':
        runs, run_output = run_table_column_names_test(timeout, test, test_details)
    elif test_details['type'] == 'table_primary_key':
        runs, run_output = run_table_primary_key_test(timeout, test, test_details)
    elif test_details['type'] == 'table_foreign_key':
        runs, run_output = run_table_foreign_key_test(timeout, test, test_details)
    elif test_details['type'] == 'table_populate':
        runs, run_output = run_table_populate_test(timeout, test, test_details)
    elif test_details['type'] == 'table_check_constraint':
        runs, run_output = run_table_check_constraint_test(timeout, test, test_details)
    else:
        # don't try to run an unsupported test
        raise UnsupportedTestException(test_details['type'])
    time_end = time()
    run_time = time_end - time_start

    run_script(timeout, '', 'cleanup.sql')

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