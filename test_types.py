'''
Information about supported test types.
'''

class UnsupportedTestException(RuntimeError):
    '''
    Raised when the test type is not supported.
    '''

SUPPORTED_TEST_TYPES = [
    'approved_includes',
    'compile',
    'coverage',
    'i/o',
    'memory_errors',
    'performance',
    'script',
    'style',
    'unit']
