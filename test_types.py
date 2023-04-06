class UnsupportedTestException(RuntimeError):
    pass

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