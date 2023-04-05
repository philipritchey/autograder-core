from typing import List, Tuple
from os import popen

from attributes import Attributes
from config import JAVA_CLASSPATH, JAVA_FLAGS, JAVAC
from test_types import UnsupportedTestException


def compile_x_test(src: List[str] = None) -> Tuple[bool,str]:
    SRC = ' '.join(src)

    compile_cmd = '{} {} {} 2>&1'.format(JAVAC, JAVA_FLAGS, SRC)
    p = popen(compile_cmd)
    try:
        output = p.read()
    except Exception as e:
        output = str(e)
    ret = p.close()
    return ret == None, output

def compile_unit_test(src: List[str]) -> Tuple[bool,str]:
    return compile_x_test(src + ['UnitTest.java', 'UnitTestRunner.java', 'TestRunner.java'])

def compile_performance_test(src: List[str]) -> Tuple[bool,str]:
    return compile_x_test(src)

def compile_io_test(src: List[str]) -> Tuple[bool,str]:
    return compile_x_test(src)

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

def compile_test(test: Attributes) -> Tuple[bool, str]:
    compiles = False
    compile_output = ''
    if test['type'] == 'unit':
        compiles, compile_output = compile_unit_test([test['target'], test['include']])
    elif test['type'] == 'i/o':
        compiles, compile_output = compile_io_test([test['target'], test['include']])
    elif test['type'] == 'script':
        compiles, compile_output = compile_script_test()
    elif test['type'] == 'performance':
        compiles, compile_output = compile_performance_test([test['target'], test['include']])
    elif test['type'] == 'approved_includes':
        compiles, compile_output = compile_approved_includes_test()
    elif test['type'] == 'coverage':
        compiles, compile_output = compile_coverage_test()
    elif test['type'] == 'compile':
        compiles, compile_output = compile_compile_test()
    elif test['type'] == 'memory_errors':
        compiles, compile_output = compile_memory_errors_test()
    else:
        # don't try to compile an unsupported test
        raise UnsupportedTestException(test['type'])
    return compiles, compile_output