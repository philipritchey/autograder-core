import subprocess

from attributes import Attributes
from test_types import UnsupportedTestException


def compile_x_test(name: str, src: list[str] | None = None) -> tuple[bool,str]:
    if src:
        args = ['go', 'build', '-o', name] + src
    else:
        args = ['go', 'build', '-o', name, f"{name}.go"]
    result = subprocess.run(args, capture_output=True, text=True, check=False)
    return result.returncode == 0, result.stdout + '\n' + result.stderr

def compile_unit_test() -> tuple[bool,str]:
    # we don't need to compile unit tests, we just run them with `go test``
    return True, ''
    # return compile_x_test('unittest')  # name of executable == name of source (unittest.go)

def compile_io_test(src: list[str]) -> tuple[bool,str]:
    return compile_x_test('io_test', src)  # name of executable and explicit list of source files

def compile_script_test() -> tuple[bool,str]:
    return True, ''

def compile_approved_includes_test() -> tuple[bool,str]:
    return True, ''

def compile_coverage_test() -> tuple[bool,str]:
    return True, ''

def compile_compile_test() -> tuple[bool,str]:
    return True, ''

def compile_test(test: Attributes) -> tuple[bool, str]:
    compiles = False
    compile_output = ''
    if test['type'] == 'unit':
        compiles, compile_output = compile_unit_test()
    elif test['type'] == 'i/o':
        compiles, compile_output = compile_io_test(test['target'].split(' '))
    elif test['type'] == 'script':
        compiles, compile_output = compile_script_test()
    elif test['type'] == 'approved_includes':
        compiles, compile_output = compile_approved_includes_test()
    elif test['type'] == 'coverage':
        compiles, compile_output = compile_coverage_test()
    elif test['type'] == 'compile':
        compiles, compile_output = compile_compile_test()
    else:
        # don't try to compile an unsupported test
        raise UnsupportedTestException(test['type'])
    return compiles, compile_output
