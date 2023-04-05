class UnsupportedTestException(RuntimeError):
    pass

SUPPORTED_TEST_TYPES = [
    'unit',
    'i/o',
    'script',
    'performance',
    'approved_includes',
    'coverage',
    'compile',
    'memory_errors']