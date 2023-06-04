# writing tests

tests must be located in `tests/<language>` in your assignment-specific repo and the filename(s) must match `*.tests`.

## test attributes

| tag | description |
| --- | --- |
| `@name` | **required.** a descriptive name for the test |
| `@points` | **required.** a floating-point value for the weight of the test |
| `@target` | **required.** target file of test. not required if type is `compile`, `memory_errors`, `script`, or `style` |
| `@type` | **required.** type of test |
| `@include` | *optional.* space-separated list of source or header files to include in test. this means `#include` / `import` or compile, depending on the test type. (default = empty) |
| `@number` | *optional.* actually a string, used for sorting tests |
| `@show_output` | *optional.* whether to show the output of the test to the student (`true`, default = `false`) |
| `@skip` | *optional.* whether to skip the test (`true`, default = `false`) |
| `@timeout` | *optional.* floating-point number of seconds before test times out (default = `10`) |
| `@visibility` | *optional.* when to show test to student (`hidden`, `after_due_date`, `after_published`, default = `visible`) |

## test types
| type | description |
| --- | --- |
| `approved_includes` | check that only approved includes are used |
| `compile` | check that the submission compiles without errors or warnings |
| `coverage` | check that the submitted tests cover at least 90% of the code |
| `i/o` | check that the submission responds correctly to standard input |
| `memory_errors` | (c++ only) check the submission for memory errors using valgrind |
| `performance` | check that the submission runs fast enough |
| `script` | run a user-defined custom test |
| `style` | (java only) check that the submission adheres to google's styleguide |
| `unit` | run a unit test |

## Jump to Documentation by Type
* [approved includes](#approved-include-tests)
* [compile](#compile-tests)
* [coverage](#coverage-tests)
* [i/o](#io-tests)
* [memory errors](#memory-error-tests)
* [performance](#performance-tests)
* [script / custom](#script-tests)
* [style](#style-tests)
* [unit](#unit-tests)

# approved include tests
[top](#jump-to-documentation-by-type)

* `@target` is the file in which to verify that only approved includes are used
* set `@show_output` be true so the student knows which include was forbidden.
* the body of the test is a newline-separated list
* if at least one instance of this type of test is specified and an unapproved include is found (i.e. any of the approved include tests fail), then the score of the submission is 0.

## examples
### c++
```
/*
@name: approved includes for code.cpp
@points: 1
@target: code.cpp
@type: approved_includes
@show_output: true
*/
<test>
cstddef
iostream
stdexcept
code.h
</test>
```

### java
```
/*
@name: approved includes for Code.java
@points: 1
@target: Code.java
@type: approved_includes
@show_output: true
*/
<test>
java.util.LinkedList
</test>
```

# compile tests
[top](#jump-to-documentation-by-type)

* set `@show_output` to true so the student knows why the compilation failed
* the body of the test is a newline-separated list of files to compile

## examples
### c++
```
/*
@name: code compiles without errors or warnings
@points: 1
@type: compile
@show_output: true
*/
<test>
code_tests.cpp
code.cpp
</test>
```

### java
```
/*
@name: code compiles without errors or warnings
@points: 1
@type: compile
@show_output: true
*/
<test>
Code.java
CodeTests.java
CodeTestRunner.java
</test>
```

# coverage tests
[top](#jump-to-documentation-by-type)

* `@target` is the file whose coverage we care about
* set `@show_output` to true if you want to tell the student their coverage
  * since it runs their own tests, they could find this out without making a submission
* set `@timeout` to a reasonably large value, e.g. 30, since measuring coverage has non-trivial overhead
* the body of the test contains two `key: value` pairs
  * `source` is the source code file(s) to compile in addition to `@target`
    * this is usually the same as `@target`, but not always (e.g. it can be many files, separated by spaces)
  * `main` is the file that contains the entry point of the program (i.e. the `main` method)
* if at least one instance of this type of test is specified and the coverage of the `@target` is less than 90% (i.e. any of the coverage tests fail), then the score of the submission is 0.

## examples
### c++
```
/*
@name: test coverage
@points: 1
@target: code.cpp
@type: coverage
@timeout: 30
*/
<test>
  source: code.cpp
  main: code_tests.cpp
</test>
```

### java
```
/*
@name: test coverage
@points: 1
@target: Code.java
@type: coverage
@timeout: 30
*/
<test>
  source: Code.java
  main: CodeTestRunner.java
</test>
```

# i/o tests
[top](#jump-to-documentation-by-type)

* `@target` is the source file that contains the entry point (i.e `main` method)
* `@include` is a space-separated list of source files to compile with `@target`
* the body of the test has two `key: value` pairs:
  * `input` is the path to a file containing the input to provide to the program over standard input
  * `output` is the path to a file containing the expected output against which to check the output of the program.  end-of-line whitespace is removed before comparison.

## examples
### c++
```
/*
@name: example
@points: 5
@target: code_interactive.cpp
@type: i/o
@include: code.cpp
*/
<test>
    input: io_tests/example/input.txt
    output: io_tests/example/output.txt
</test>
```

### java
```
/*
@name: example
@points: 5
@target: Code.java
@type: i/o
*/
<test>
    input: io_tests/example/input.txt
    output: io_tests/example/output.txt
</test>
```

# memory error tests
[top](#jump-to-documentation-by-type)

| :warning: c++ only |
| --- |

* set `@timeout` to a reasonably large value, e.g. 30, since measuring coverage has non-trivial overhead
* the body of the test is a newline-separated list of files to compile, exactly one of which must contain the `main` method

## examples
### c++
```
/*
@name: memory errors
@points: 1
@type: memory_errors
@timeout: 30
*/
<test>
memory_errors_test.cpp
code.cpp
</test>
```

# performance tests
[top](#jump-to-documentation-by-type)

* if using c++, then `@target` is `#include`d in the generated test source file
* set `@timeout` to the maximum time allowed to complete the computation
  * should be small enough that inefficient implementations will not finish in time, but efficient implementations will
* the body of the test is source code that will be wrapped by timing code in an automatically-generated test function/file.

## examples
### c++
```
/*
@name: performance example
@points: 1
@target: code.cpp
@type: performance
@show_output: true
@timeout: 30
*/
<test>
    size_t cnt = 1;
    for (unsigned n = 3; n < 2000000; n++) {
      if (is_prime(n)) cnt++;
    }
    std::cout << "  found " << cnt << " primes." << std::endl;
    EXPECT_EQ(cnt, 148933);
</test>
```

### java
```
/*
@name: performance example
@points: 1
@target: Code.java
@type: performance
@show_output: true
@timeout: 30
*/
<test>
    long cnt = 1;
    for (int n = 3; n < 2000000; n++) {
      if (Code.isPrime(n)) {
        cnt++;
      }
    }
    System.out.println("  found " + cnt + " primes.");
    if (cnt != 148933) {
      System.out.println("[FAIL] incorrect number of primes.");
      System.exit(1);
    }
</test>
```

# script/custom tests
[top](#jump-to-documentation-by-type)

* the body of the test is a single line which is the path to an executable script
  * CLI arguments to the script can also be included (space-separated)
  * put a *hash-bang* at the top of the script, e.g. `#! /usr/bin/env bash`
  * the score on the test should be saved in the file `OUTPUT`
    * that percentage of the `@points` will be awarded
  * any debugging information for the student (only visible if `@show_output` is `true`) should be saved in the file `DEBUG`

## examples
### c++
```
/*
@name: script example
@points: 1
@type: script
@show_output: true
*/
<test>
  script_tests/example.sh
</test>
```

# style tests
[top](#jump-to-documentation-by-type)

| :warning: java only |
| --- |

* the body of the test is a newline-separated list of files of which to check the style
  * the files must have zero style warnings in order to pass the test
  * no partial credit is given

## exmaple
### java
```
/*
@name: check style
@points: 1
@type: style
*/
<test>
Code.java
</test>
```

# unit tests
[top](#jump-to-documentation-by-type)

* `@target` is the source file which contains the unit under test
* the body of the test is source code that will be placed into an automatically-generated test function/file.
  * for c++, use the bootleg google test syntax (see [cs12x_test.h](https://github.com/philipritchey/autograder-core/blob/main/tests/c%2B%2B/cs12x_test.h))
    * or go old school:
      ```c++
      if (actual_value != expected_value) {
        std::cout << "[FAIL] expected " << expected_value << ", got " << actual_value << std::endl;
        return 1; // signal failure to test runner
      } else {
        return 0; // signal success to test runner
      }
      ```
  * for java, use either junit or hamcrest syntax
    * or go old school:
      ```java
      if (actual_value != expected_value) {
        System.out.println("[FAIL] expected " + expected_value + ", got " + actual_value);
        System.exit(1); // signal failure to test runner
      } else {
        System.exit(0); // signal success to test runner
      }
      ```


## examples
### c++
```
/*
@name: unit example
@points: 1
@target: code.cpp
@type: unit
*/
<test>
    EXPECT_FALSE(is_prime(867));
    EXPECT_TRUE(is_prime(5309));
    EXPECT_TRUE(is_prime(8675309));
</test>
```

### java
```
/*
@name: unit example with hamcrest
@points: 1
@target: Code.java
@type: unit
*/
<test>
  assertThat(Code.isPrime(867), is(false));
  assertThat(Code.isPrime(5309), is(true));
  assertThat(Code.isPrime(8675309), is(true));
</test>
```
