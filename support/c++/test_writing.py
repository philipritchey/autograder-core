'''write tests for c++'''
from attributes import Attributes
from test_types import UnsupportedTestException

def write_unit_test(test: Attributes) -> None:
    with open('unit_test.cpp', 'wt', encoding='utf-8') as f:
        f.write(f"#include \"{test['target']}\"\n\n")
        if test['include']:
            for include in test['include'].split():
                f.write(f'#include {include}\n')
        f.write('#include "cs12x_test.h"\n\n')

        f.write('int main() {\n')
        f.write('    INIT_TEST;\n')
        f.write('    try {\n')
        f.write('        {}\n'.format('\n        '.join(test['code'].splitlines())))
        f.write('    } catch (const std::exception& err) {\n')
        f.write('        std::cout << "Caught unexpected std::exception, what: " << err.what() << std::endl;')
        f.write('        FAIL();\n')
        f.write('    } catch (...) {\n')
        f.write('        std::cout << "Caught unexpected non-std::exception" << std::endl;\n')
        f.write('        FAIL();\n')
        f.write('    }\n')
        f.write('    RESULT(pass);\n')
        f.write('    return pass ? 0 : 1;\n')
        f.write('}\n')

def write_performance_test(test: Attributes) -> None:
    with open('performance_test.cpp', 'wt', encoding='utf-8') as f:
        f.write(f"#include \"{test['target']}\"\n\n")
        f.write('#include <iostream>\n')
        f.write('#include <chrono>\n')
        if test['include']:
            for include in test['include'].split():
                f.write(f'#include {include}\n')
        f.write('#include "cs12x_test.h"\n\n')

        f.write('int main() {\n')
        f.write('    INIT_TEST;\n')
        f.write('    auto start = std::chrono::steady_clock::now();\n')
        f.write('    try {\n')
        f.write('        {}\n'.format('\n        '.join(test['code'].splitlines())))
        f.write('    } catch (const std::exception& err) {\n')
        f.write('        std::cout << "Caught unexpected std::exception, what: " << err.what() << std::endl;')
        f.write('        FAIL();\n')
        f.write('    } catch (...) {\n')
        f.write('        std::cout << "Caught unexpected non-std::exception" << std::endl;\n')
        f.write('        FAIL();\n')
        f.write('    }\n')
        f.write('    auto end = std::chrono::steady_clock::now();\n')
        f.write('    auto microseconds = std::chrono::duration_cast<std::chrono::microseconds>(end - start).count();\n')
        f.write('    std::cout << "operation took " << microseconds << " µs." << std::endl;\n')
        f.write('    RESULT(pass);\n')
        f.write('    return pass ? 0 : 1;\n')
        f.write('}\n')

# Writes out the input and output strings
def write_io_test(test: Attributes) -> None:
    with open('input.txt', 'wt', encoding='utf-8') as f:
        f.write(test['expected_input'])
        f.write("\n")
    with open('output.txt', 'wt', encoding='utf-8') as f:
        f.write(test['expected_output'])

def write_script_test(test: Attributes) -> None:
    with open('script.sh', 'wt', encoding='utf-8') as f:
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

def write_test(test: Attributes) -> None:
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
        # don't try to write an unsupported test
        raise UnsupportedTestException(test['type'])
