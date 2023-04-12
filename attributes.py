from typing import List, TypedDict


class Attributes(TypedDict):
    number: str
    name: str
    points: float
    type: str
    target: str
    show_output: str
    timeout: float
    include: str
    code: str
    expected_input: str
    expected_output: str
    script_content: str
    approved_includes: List[str]
    skip: bool
    script_args: str
    visibility: str