from typing import Any, Dict, List, TypedDict


class TestResult(TypedDict):
    number:     str
    name:       str
    score:      float
    max_score:  float
    status:     str
    output:     str
    tags:       List[str]
    visibility: str
    extra_data: Dict[Any, Any]

class PartialTestResult(TypedDict):
    run_output:          str
    unapproved_includes: bool
    sufficient_coverage: bool
    points:              float
    run_time:            float

class Result(TypedDict):
    score:             float
    output:            str
    execution_time:    float
    visibility:        str
    stdout_visibility: str
    tests:             List[TestResult]
