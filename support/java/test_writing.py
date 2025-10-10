from attributes import Attributes
from test_types import UnsupportedTestException

def write_unit_test(test: Attributes) -> None:
    with open('UnitTest.java', 'wt') as f:
        f.write('import static org.hamcrest.MatcherAssert.assertThat;\n')
        f.write('import static org.hamcrest.Matchers.*;\n')
        f.write('import static org.junit.Assert.assertThrows;\n\n')
        f.write('import java.util.ArrayList;\n\n')

        f.write('import junit.framework.TestCase;\n')
        f.write('import org.junit.Test;\n\n')

        f.write('public class UnitTest extends TestCase {\n')
        f.write('  @Test\n')
        f.write('  public void testUnit() {\n')
        f.write('    {}\n'.format('\n    '.join(test['code'].splitlines())))
        f.write('  }\n')
        f.write('}\n')

def write_performance_test(test: Attributes) -> None:
    with open('PerformanceTest.java', 'wt') as f:
        f.write('public class PerformanceTest {\n')
        f.write('  public static void main(String[] args) {\n')
        f.write('    long start = System.currentTimeMillis();\n')
        f.write('    {}\n'.format('\n    '.join(test['code'].splitlines())))
        f.write('    long end = System.currentTimeMillis();\n')
        f.write('    long milliseconds = end - start;\n')
        f.write('    System.out.println("operation took " + milliseconds + " ms.");\n')
        f.write('  }\n')
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

def write_style_test(test: Attributes) -> None:
    test['script_content'] = f"./check_style.sh {' '.join(test['approved_includes'])}"
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
    elif test['type'] == 'style':
        write_style_test(test)
    else:
        # don't try to write an unsupported test
        raise UnsupportedTestException(test['type'])