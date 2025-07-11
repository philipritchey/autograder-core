'''
Methods for parsing test specifications.
'''

from typing import List, Tuple, Dict, Any
from dataclasses import dataclass
from attributes import Attributes
from config import BEGIN_MULTILINE_COMMENT_DELIMITER, BEGIN_TEST_DELIMITER, DEFAULT_NUMBER,\
    DEFAULT_POINTS, DEFAULT_SHOW_OUTPUT, DEFAULT_TARGET, DEFAULT_TIMEOUT, DEFAULT_VISIBILITY,\
    EMPTY_TEST_BLOCK, END_MULTILINE_COMMENT_DELIMITER, END_TEST_DELIMITER, VISIBILITY_OPTIONS


@dataclass
class FilePosition:
    '''
    Stores file contents with position
    '''
    index: int
    lines: List[str]
    filename: str

def unexpected_end_of_input(file_pos: FilePosition) -> SyntaxError:
    '''
    construct a syntax error reaching an unexpected end of input.
    '''
    # filename lineno offset text
    return SyntaxError(
        'unexpected end of input',
        (file_pos.filename, file_pos.index+1, 1, file_pos.lines[file_pos.index]))

def goto_next_line(file_pos: FilePosition) -> str:
    '''
    go to the next non-blank line.
    '''
    file_pos.index += 1
    if file_pos.index >= len(file_pos.lines):
        raise unexpected_end_of_input(file_pos)

    # skip blank lines
    skip_blank_lines(file_pos)
    line = file_pos.lines[file_pos.index].rstrip()

    return line

def skip_blank_lines(file_pos: FilePosition) -> None:
    '''
    skip blank lines.
    '''
    while file_pos.index < len(file_pos.lines) and not file_pos.lines[file_pos.index].rstrip():
        file_pos.index += 1

def eat_block_of_test(file_pos: FilePosition) -> str:
    '''
    read the test body.
    '''
    # go to next line
    line = goto_next_line(file_pos)

    # expect start of test block
    if line == EMPTY_TEST_BLOCK:
        return line

    if line != BEGIN_TEST_DELIMITER:
        # filename lineno offset text
        raise SyntaxError(
            f'missing expected start of test block: "{BEGIN_TEST_DELIMITER}"',
            (file_pos.filename, file_pos.index+1, 1, line))

    # eat until end of test block
    while line != END_TEST_DELIMITER:
        # go to next line
        line = goto_next_line(file_pos)

    return line

def eat_empty_test_block(file_pos: FilePosition) -> str:
    '''
    read an empty test block or throw a syntax error if block is not empty.
    '''
    # go to next line
    line = goto_next_line(file_pos)

    # expect empty test block
    if line == BEGIN_TEST_DELIMITER:
        line = goto_next_line(file_pos)
        if line != END_TEST_DELIMITER:
            raise SyntaxError(
                f'expected end of test: "{END_TEST_DELIMITER}"',
                (file_pos.filename, file_pos.index+1, 1, line))
        return line

    if line != EMPTY_TEST_BLOCK:
        # filename lineno offset text
        raise SyntaxError(
            f'expected empty test block: "{EMPTY_TEST_BLOCK}"',
            (file_pos.filename, file_pos.index+1, 1, line))

    return line

def current_line(file_pos: FilePosition) -> str:
    '''
    get the current line from the file position structure.
    '''
    return file_pos.lines[file_pos.index].rstrip()

def expect_start_of_multiline_comment(file_pos: FilePosition) -> None:
    '''
    throw a syntax error if the next line is not the beginning of multiline comment delimiter.
    '''
    # expect start of multiline comment
    line = current_line(file_pos)
    if line != BEGIN_MULTILINE_COMMENT_DELIMITER:
        # filename lineno offset text
        raise SyntaxError(
            f'missing expected start of multiline comment: "{BEGIN_MULTILINE_COMMENT_DELIMITER}"',
            (file_pos.filename, file_pos.index+1, 1, line))


def expect_end_of_multiline_comment(file_pos: FilePosition) -> None:
    '''
    throw a syntax error if the next line is not the end of multiline comment delimiter.
    '''
    # expect end of multiline comment
    line = current_line(file_pos)
    if line != END_MULTILINE_COMMENT_DELIMITER:
        # filename lineno offset text
        raise SyntaxError(
            f'missing expected end of multiline comment: "{END_MULTILINE_COMMENT_DELIMITER}"',
            (file_pos.filename, file_pos.index+1, 1, line))


def read_annotations(file_pos: FilePosition) -> Dict[str, Any]:
    '''
    read test annotations.
    '''
    expect_start_of_multiline_comment(file_pos)

    # go to next line
    line = goto_next_line(file_pos).rstrip()

    attr_dict: Dict[str, Any] = {}
    while line.startswith('@'):
        try:
            tag, value = line.split(sep=':', maxsplit=1)
        except ValueError as exc:
            raise SyntaxError(
                'missing attribute value? (attributes look like "@name: value")',
                (file_pos.filename, file_pos.index+1, 1, line)) from exc
        tag = tag.strip()[1:]
        value = value.strip()
        if tag in attr_dict:
            old_value = attr_dict[tag]
            print((
                f'[WARNING] ({file_pos.filename}:{file_pos.index+1})'
                f' tag "{tag}" already exists,'
                f'old value will be overwritten: {old_value} --> {value}'))
        if tag == "points":
            points = DEFAULT_POINTS
            try:
                points = float(value)
            except ValueError:
                print((
                    f'[WARNING] ({file_pos.filename}:{file_pos.index+1})'
                    f' points attribute has invalid value ({value}),'
                    f' using default value ({DEFAULT_POINTS})'))
            attr_dict['points'] = points
        elif tag == 'timeout':
            timeout = DEFAULT_TIMEOUT
            try:
                timeout = float(value)
                if timeout <= 0:
                    raise ValueError('timeout must be positive')
            except ValueError:
                print((
                    f'[WARNING] ({file_pos.filename}:{file_pos.index+1})'
                    f' timeout attribute has invalid value ({value}),'
                    f' using default value ({DEFAULT_TIMEOUT})'))
            attr_dict['timeout'] = timeout
        elif tag == 'visibility':
            visibility = DEFAULT_VISIBILITY
            if value not in VISIBILITY_OPTIONS:
                print((
                    f'[WARNING] ({file_pos.filename}:{file_pos.index+1})'
                    f' visibility attribute has invalid value ({value}),'
                    f' using default value ({DEFAULT_VISIBILITY})'))
            else:
                visibility = value
            attr_dict['visibility'] = visibility
        else:
            attr_dict[tag] = value

        # go to next line
        line = goto_next_line(file_pos)

    expect_end_of_multiline_comment(file_pos)

    return attr_dict


def verify_required_annotations(annotations: Dict[str, Any], file_pos: FilePosition) -> None:
    '''
    verify that all required attributes are present.
    '''
    # verify all required attributes are present
    # 'target' not required for script or style or compile or memory errors tests
    exempt_types = ('script', 'style', 'compile', 'memory_errors')
    required_attributes = ('name', 'points', 'type', 'target')

    additonal_details = str()
    for attr in annotations:
        additonal_details += f'  {attr}: {annotations[attr]}\n'

    for attribute in required_attributes:
        if attribute != 'target' or annotations['type'] not in exempt_types:
            if attribute not in annotations:
                raise KeyError((
                    f'({file_pos.filename}:{file_pos.index+1})'
                    f' missing required attribute: {attribute}'
                    f'\n{additonal_details}'))
            if annotations[attribute] == '':
                raise ValueError((
                    f'({file_pos.filename}:{file_pos.index+1})'
                    f' required attribute missing value: {attribute}'
                    f'\n{additonal_details}'))


def apply_default_annotations(annotations: Dict[str, Any]) -> None:
    '''
    apply default values to missing attributes.
    '''
    if 'number' not in annotations:
        annotations['number'] = DEFAULT_NUMBER

    if 'target' not in annotations:
        annotations['target'] = DEFAULT_TARGET

    # set timeouts to default if not specified
    if 'timeout' not in annotations:
        annotations['timeout'] = DEFAULT_TIMEOUT

    # set show_output to default if not specified
    if 'show_output' not in annotations:
        if (annotations['type'] == 'approved_includes' or
                annotations['type'] == 'coverage' or
                annotations['type'] == 'compile'):
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

def read_attributes(file_pos: FilePosition) -> Attributes:
    '''
    read, verify, andapply default values to test annotations.
    '''
    # skip blank lines
    skip_blank_lines(file_pos)
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
    if file_pos.index >= len(file_pos.lines):
        # at end of file
        return attributes

    annotations = read_annotations(file_pos)
    verify_required_annotations(annotations, file_pos)
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

def read_block_of_test(file_pos: FilePosition) -> str:
    '''
    read lines until and end test body delimited is read
    '''
    code = str()
    got_code = True
    while got_code:
        line = goto_next_line(file_pos)

        if line != END_TEST_DELIMITER:
            code += line + '\n'
        else:
            got_code = False

    return code

def expect_start_of_test_block(file_pos: FilePosition) -> None:
    '''
    throw a syntax error if the next line is not the begin test body delimiter
    '''
    # expect start of test block
    line = goto_next_line(file_pos)
    if line != BEGIN_TEST_DELIMITER:
        # filename lineno offset text
        raise SyntaxError(
            f'missing expected start of test block: "{BEGIN_TEST_DELIMITER}"',
            (file_pos.filename, file_pos.index+1, 1, line))


def expect_end_of_test_block(file_pos: FilePosition) -> None:
    '''
    throw a syntax error if the next line is not the end test body delimiter
    '''
    line = goto_next_line(file_pos)
    if line != END_TEST_DELIMITER:
        # filename lineno offset text
        raise SyntaxError(
            f'missing expected end of test block: "{END_TEST_DELIMITER}"',
            (file_pos.filename, file_pos.index+1, 1, line))


def read_unit_test(file_pos: FilePosition) -> str:
    '''
    read a unit test.
    '''

    expect_start_of_test_block(file_pos)

    # expect next lines to be unit test code
    code = read_block_of_test(file_pos)
    return code

def read_io_test(file_pos: FilePosition) -> Tuple[str, str]:
    '''
    read an i/o test.
    '''

    expect_start_of_test_block(file_pos)

    input_filename = None
    output_filename = None
    line = ''

    for _ in range(2):
        # go to next line
        line = goto_next_line(file_pos)

        try:
            tag, value = line.split(':')
        except ValueError as exc:
            # filename lineno offset text
            raise SyntaxError(
                'expected "tag: value" pair',
                (file_pos.filename, file_pos.index+1, 1, line)) from exc

        tag = tag.strip()
        value = value.strip()

        if tag == 'input':
            input_filename = value
        elif tag == 'output':
            output_filename = value
        else:
            # filename lineno offset text
            raise SyntaxError(
                f'unexpected tag ({tag}) in i/o test',
                (file_pos.filename, file_pos.index+1, 1, line))

    expect_end_of_test_block(file_pos)

    if not input_filename:
        raise SyntaxError(
            'missing output filename in i/o test',
            (file_pos.filename, file_pos.index+1, 1, line))
    if not output_filename:
        raise SyntaxError(
            'missing input filename in i/o test',
            (file_pos.filename, file_pos.index+1, 1, line))

    expected_input = None
    expected_output = None
    try:
        with open(input_filename, 'r', encoding='utf-8') as file:
            expected_input = file.read()
    except FileNotFoundError as exc:
        raise SyntaxError(
            f'input file not found: {input_filename}',
            (file_pos.filename, file_pos.index+1, 1, line)) from exc

    try:
        with open(output_filename, 'r', encoding='utf-8') as file:
            expected_output = file.read()
    except FileNotFoundError as exc:
        raise SyntaxError(
            f'output file not found: {output_filename}',
            (file_pos.filename, file_pos.index+1, 1, line)) from exc

    return expected_input, expected_output

def read_script_test(file_pos: FilePosition) -> Tuple[str, str]:
    '''
    read a script/custom test.
    '''

    expect_start_of_test_block(file_pos)

    # go to next line
    line = goto_next_line(file_pos).strip()
    values = line.split(None, 1)
    script_args = str()
    script_content = str()
    if len(values) == 0:
        raise SyntaxError(
            'missing expected name of script, e.g. scripts/example.sh',
            (file_pos.filename, file_pos.index+1, 1, line))

    if len(values) == 1:
        # does not have args (only script path)
        script_filename_string = line
    else:
        # has args
        script_filename_string = values[0]
        script_args = values[1]

    # print("Script filename: " + script_filename_string)

    expect_end_of_test_block(file_pos)

    try:
        with open(script_filename_string, 'rt', encoding='utf-8') as file:
            script_content = file.read()
    except FileNotFoundError:
        print(f'No such file or directory: \'{script_filename_string}\'')

    return script_args, script_content

def read_approved_includes(file_pos: FilePosition) -> List[str]:
    '''
    read an approved include test.
    '''

    expect_start_of_test_block(file_pos)

    # go to next line
    line = goto_next_line(file_pos)

    approved_includes: list[str] = []
    while line != END_TEST_DELIMITER:
        approved_includes.append(line)
        line = goto_next_line(file_pos)

    return approved_includes

def read_coverage_test(file_pos: FilePosition) -> Tuple[str, List[str]]:
    '''
    read a coverage test.
    '''

    expect_start_of_test_block(file_pos)

    source: list[str] = []
    main = str()

    # go to next line
    line = goto_next_line(file_pos)

    while line != END_TEST_DELIMITER:
        try:
            tag, values = line.split(':')
        except ValueError as exc:
            # filename lineno offset text
            raise SyntaxError(
                'expected "tag: value" pair',
                (file_pos.filename, file_pos.index+1, 1, line)) from exc

        tag = tag.strip()

        if tag == 'source':
            source = values.split()
        elif tag == 'main':
            main = values.strip()
        else:
            # filename lineno offset text
            raise SyntaxError(
                f'unexpected tag ({tag}) in coverage test',
                (file_pos.filename, file_pos.index+1, 1, line))

        # go to next line
        line = goto_next_line(file_pos)

    if not main:
        # filename lineno offset text
        raise SyntaxError(
            'missing expected main and/or target in coverage test',
            (file_pos.filename, file_pos.index+1, 1, line))

    return main, source


def read_tests(filename: str) -> List[Attributes]:
    '''
    read tests from file into a list.
    '''
    with open(filename, encoding='utf-8') as file:
        lines = file.readlines()

    # trim empty lines at end of file
    while len(lines) > 0 and lines[-1].strip() == '':
        del lines[-1]

    file_pos = FilePosition(0, lines, filename)
    tests: list[Attributes] = []
    while file_pos.index < len(file_pos.lines):
        # expect next lines to be only attributes and values
        attributes = read_attributes(file_pos)

        if file_pos.index < 0:
            # at end of file
            break

        test_type = attributes['type']
        if test_type in ('unit', 'performance'):
            attributes['code'] = read_unit_test(file_pos)
            tests.append(attributes)

        elif test_type == 'i/o':
            attributes['expected_input'], attributes['expected_output'] = read_io_test(file_pos)
            tests.append(attributes)

        elif test_type == 'script':
            attributes['script_args'], attributes['script_content'] = read_script_test(file_pos)
            tests.append(attributes)

        elif test_type in ('approved_includes', 'compile', 'memory_errors', 'style'):
            attributes['approved_includes'] = read_approved_includes(file_pos)
            tests.append(attributes)

        elif test_type == 'coverage':
            attributes['include'], attributes['approved_includes'] = read_coverage_test(file_pos)
            tests.append(attributes)

        else:
            print((
                f'WARNING: unsupported test type: {test_type}.'
                f'  this one will be ignored: {attributes["number"]} {attributes["name"]}'
            ))
            _ = eat_block_of_test(file_pos)

        file_pos.index += 1

    return tests
