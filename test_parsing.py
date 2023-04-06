from typing import List, Tuple, Dict, Any
from attributes import Attributes

from config import BEGIN_TEST_DELIMITER, DEFAULT_NUMBER, DEFAULT_POINTS, DEFAULT_SHOW_OUTPUT, DEFAULT_TARGET, DEFAULT_TIMEOUT, DEFAULT_VISIBILITY, EMPTY_TEST_BLOCK, END_TEST_DELIMITER

# file contents with position
class FilePosition:
    def __init__(self, index: int, lines: List[str], filename: str):
        self.index: int = index
        self.lines: List[str] = lines
        self.filename: str = filename

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

def current_line(fp: FilePosition) -> str:
    return fp.lines[fp.index].strip()

def expect_start_of_multiline_comment(fp: FilePosition) -> None:
    # expect start of multiline comment
    line = current_line(fp)
    if line != '/*':
        # filename lineno offset text
        raise SyntaxError('missing expected start of multiline comment: "/*"', (fp.filename, fp.index+1, 1, line))


def expect_end_of_multiline_comment(fp: FilePosition) -> None:
    # expect end of multiline comment
    line = current_line(fp)
    if line != '*/':
        # filename lineno offset text
        raise SyntaxError('missing expected end of multiline comment: "*/"', (fp.filename, fp.index+1, 1, line))


def read_annotations(fp: FilePosition) -> Dict[str, Any]:
    expect_start_of_multiline_comment(fp)

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

    expect_end_of_multiline_comment(fp)

    return attr_dict


def verify_required_annotations(annotations: Dict[str, Any], fp: FilePosition) -> None:
    # verify all required attributes are present
    # 'target' not required for script tests
    required_attributes = ('name', 'points', 'type', 'target')

    additonal_details = str()
    for attr in annotations:
        additonal_details += f'  {attr}: {annotations[attr]}\n'

    for attribute in required_attributes:
        # if test type is not script or attribute is not target
        #   -> target is not required for script tests or style tests
        if attribute != 'target' or annotations['type'] not in ['script', 'style']:
            if attribute not in annotations:
                raise KeyError(f'({fp.filename}:{fp.index+1}) missing required attribute: {attribute}\n{additonal_details}')
            if annotations[attribute] == '':
                raise ValueError(f'({fp.filename}:{fp.index+1}) required attribute missing value: {attribute}\n{additonal_details}')


def apply_default_annotations(annotations: Dict[str, Any]) -> None:
    if 'number' not in annotations:
        annotations['number'] = DEFAULT_NUMBER

    if 'target' not in annotations:
        annotations['target'] = DEFAULT_TARGET

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

    if 'visibility' not in annotations:
        annotations['visibility'] = DEFAULT_VISIBILITY

def read_attributes(fp: FilePosition) -> Attributes:
    # skip blank lines
    skip_blank_lines(fp)
    attributes: Attributes = {
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
            'script_args': '',
            'visibility': ''
        }
    if fp.index >= len(fp.lines):
        # at end of file
        return attributes

    annotations = read_annotations(fp)
    verify_required_annotations(annotations, fp)
    apply_default_annotations(annotations)

    attributes['number'] = annotations['number']
    attributes['name'] = annotations['name']
    attributes['points'] = annotations['points']
    attributes['type'] = annotations['type']
    attributes['target'] = annotations['target']
    attributes['show_output'] = annotations['show_output']
    attributes['timeout'] = annotations['timeout']
    attributes['include'] = annotations['include']
    attributes['skip'] = annotations['skip']
    attributes['visibility'] = annotations['visibility']

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

def expect_start_of_test_block(fp: FilePosition) -> None:
    # expect start of test block
    line = goto_next_line(fp)
    if line != BEGIN_TEST_DELIMITER:
        # filename lineno offset text
        raise SyntaxError(f'missing expected start of test block: "{BEGIN_TEST_DELIMITER}"', (fp.filename, fp.index+1, 1, line))


def expect_end_of_test_block(fp: FilePosition) -> None:
    line = goto_next_line(fp)
    if line != END_TEST_DELIMITER:
        # filename lineno offset text
        raise SyntaxError(f'missing expected end of test block: "{END_TEST_DELIMITER}"', (fp.filename, fp.index+1, 1, line))


def read_unit_test(fp: FilePosition) -> str:

    expect_start_of_test_block(fp)

    # expect next lines to be unit test code
    code = read_block_of_test(fp)
    return code

def read_io_test(fp: FilePosition) -> Tuple[str, str]:

    expect_start_of_test_block(fp)

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

    expect_end_of_test_block(fp)

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

    expect_start_of_test_block(fp)

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

    expect_end_of_test_block(fp)

    try:
        with open(script_filename_string, 'r') as f:
            script_content = f.read()
    except FileNotFoundError:
        print(f'No such file or directory: \'{script_filename_string}\'')

    return script_args, script_content

def read_approved_includes(fp: FilePosition) -> List[str]:

    expect_start_of_test_block(fp)

    # go to next line
    line = goto_next_line(fp)

    approved_includes = list()
    while line != END_TEST_DELIMITER:
        approved_includes.append(line)
        line = goto_next_line(fp)

    return approved_includes

def read_coverage_test(fp: FilePosition) -> Tuple[str, str, List[str]]:

    expect_start_of_test_block(fp)

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
    while len(lines) > 0 and lines[-1].strip() == '':
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

        elif test_type in ['approved_includes', 'compile', 'memory_errors', 'style']:
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
            print(f'WARNING: unsupported test type: {test_type}.  this one will be ignored: {attributes["number"]} {attributes["name"]}')
            _ = eat_block_of_test(fp)

        fp.index += 1

    return tests