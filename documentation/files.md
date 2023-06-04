
| file | description |
| ---- | ----------- |
| `documentation/files.md` | descriptions of all files |
| `support/c++/test_compiling.py` | helper methods for compiling c++ tests<br/>contains the method `compile_test(test: Attributes) -> Tuple[bool, str]` |
| `support/c++/test_running.py` | helper methods for running c++ tests<br/>contains the method `run_test(test: Attributes) -> PartialTestResult` |
| `support/c++/test_writing.py` | helper methods for writing c++ tests<br/>contains the method `write_test(test: Attributes) -> None` |
| `support/java/test_compiling.py` | helper methods for compiling java tests<br/>contains the method `compile_test(test: Attributes) -> Tuple[bool, str]` |
| `support/java/test_running.py` | helper methods for running java tests<br/>contains the method `run_test(test: Attributes) -> PartialTestResult` |
| `support/java/test_writing.py` | helper methods for writing java tests<br/>contains the method `write_test(test: Attributes) -> None` |
| `tests/c++/io_tests/example/input.txt` | example input for an io test |
| `tests/c++/io_tests/example/output.txt` | example expected output for an io test |
| `tests/c++/script_tests/example.sh` | example script for a custom (script) test |
| `tests/c++/approved_includes.sh` | script for checking that only approved includes are used |
| `tests/c++/code.tests` | :star: any file that matches `*.tests` is expected to contain test specifications<br/> see [/link/to/test-spec-doc](Test Specification) |
| `tests/c++/compiles.sh` | script for checking that submitted code compiles without warnings or errors |
| `tests/c++/coverage.sh` | script for checking that submitted tests achieve at least 90% coverage |
| `tests/c++/cs12x_test.h` | bootleg version of GoogleTest (C++ testing framework) |
| `tests/c++/memory_errors_test.cpp` | (bad) example test code used for checking for memory errors |
| `tests/c++/memory_errors.sh` | script for testing for the presence of memory errors |
| `tests/java/io_tests/example/input.txt` | example input for an io test |
| `tests/java/io_tests/example/output.txt` | example expected output for an io test |
| `tests/java/lib/checkstyle-10.7.0-all.jar` | jar that contains the checkstyle tool for checking style |
| `tests/java/lib/hamcrest-2.2.jar` | jar that contains the hamcrest matchers for writing nice unit tests |
| `tests/java/lib/jacocoagent.jar` | jar that contains the jacoco agent for coverage testing |
| `tests/java/lib/jacococli.jar` | jar that contains the jacoco cli for coverage testing |
| `tests/java/lib/junit-4.13.2.jar` | jar that contains junit4 for unit testing |
| `tests/java/script_tests/` | this is where example script tests would be, if i had any |
| `tests/java/approved_includes.sh` | script for checking that only approved imports are used |
| `tests/java/check_style.sh` | script for checking whether submitted code adhere's to Google's java styleguide |
| `tests/java/code.tests` | :star: any file that matches `*.tests` is expected to contain test specifications<br/> see [/link/to/test-spec-doc](Test Specification) |
| `tests/java/compiles.sh` | script for checking that submitted code compiles without warnings or errors |
| `tests/java/coverage.sh` | script for checking that submitted tests achieve at least 90% coverage |
| `tests/java/TestRunner.java` | a utility class used to run JUnit tests |
| `tests/java/UnitTestRunner.java` | the entry point for running a unit test |
| `.gitignore` | patterns of files that git should ignore |
| `.version` | version info in case that ever becomes a thing to worry about |
| `attributes.py` | a data structure for storing information about tests (i.e. internal representation of a test) |
| `config.py` | constants that are more-or-less configurable |
| `LICENSE` | GNU GPLv3 |
| `README.md` | frontpage documentation |
| `results.py` | data structures for test results |
| `run_autograder` | boilerplate for gradescope autograding entry point<br/>:note: your assignment-specific repository needs a copy of this file<br/> see [autograded assignment template](https://github.com/philipritchey/autograded-assignment-template) |
| `run_autograder_script.sh` | the part of the full autograder script that is **not** assignment-specific |
| `run_tests.py` | the workhorse, orchestrates running the tests and collecting the results |
| `setup.sh` | boilerplate for gradescope container setup<br/>:note: your assignment-specific repository needs a copy of this file<br/> see [autograded assignment template](https://github.com/philipritchey/autograded-assignment-template)  |
| `ssh_config` | ssh configuration file for pulling from 2 repos with 2 identities<br/>:note: your assignment-specific repository needs a copy of this file<br/> see [autograded assignment template](https://github.com/philipritchey/autograded-assignment-template)  |
| `test_parsing.py` | methods for parsing test specifications<br/>contains the method `read_tests(filename: str) -> List[Attributes]` |
| `test_types.py` | coantins `UnsupportedTestException` and the (currently unused) list of supported test types |


