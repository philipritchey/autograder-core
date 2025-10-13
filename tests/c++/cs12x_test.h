#pragma once

#include <iostream>
#include <stdexcept>
#include <cmath>
#include <string>

/*
#include <iostream>
#include "test_helpers.h"
// your header file(s) here

using std::cout, std::endl;

bool test_() {
  bool pass = true;

  {
    // TEST
  }

  RESULT(pass);
  return pass;
}

int main() {
  unsigned pass_cnt = 0, fail_cnt = 0, skip_cnt = 0;

  //TEST();
  //SKIP();

  cout << "passing " << pass_cnt << "/" << (pass_cnt + fail_cnt) << " tests" << endl;
  if (skip_cnt > 0) {
    cout << "skipped " << skip_cnt << " tests" << endl;
  } else if (fail_cnt == 0) {
    cout << "ALL TESTS PASSING" << endl;
  }
}
*/

struct cout_redirect {
 private:
    std::streambuf* old;
 public:
    cout_redirect(std::streambuf* new_buffer) : old(std::cout.rdbuf(new_buffer)){}

    cout_redirect(const cout_redirect& other) : old(other.old) {}
    ~cout_redirect() { std::cout.rdbuf(old); }
    cout_redirect& operator=(const cout_redirect& rhs) {
        if (this != &rhs) {
            old = rhs.old;
        }
        return *this;
    }
};

#define INIT_TEST bool pass = true;

#define RESULT(X) if (X) {\
	std::cout << "[PASS] all tests passing";\
} else {\
	std::cout << "[FAIL] some test(s) failed";\
}\
std::cout << " in " << __FUNCTION__ << std::endl;

#define TRY(X,Y,Z,COND,FUNC) \
try {\
  auto x = X;\
  auto y = Y;\
  if (COND) {\
    FUNC(#X, x, #Y, y, __FUNCTION__, __LINE__);\
    Z;\
  }\
} catch (const std::exception& err) {\
  std::cout << "did not expect " << #X << " to throw an exception, but got " << err.what() << std::endl;\
  Z;\
} catch (...) {\
  std::cout << "did not expect " << #X << " to throw an exception, but got non-std::exception" << std::endl;\
  Z;\
}

#define FAIL() RESULT(false); return 1; std::cout

#define CHECK_EQ(X, Y, Z) TRY(X,Y,Z,!(x == y),explain_eq)
#define EXPECT_EQ(X, Y) CHECK_EQ(X, Y, pass = false)
#define ASSERT_EQ(X, Y) CHECK_EQ(X, Y, RESULT(false); return 1)

#define CHECK_STREQ(X, Y, Z) TRY(X,Y,Z,!(std::string(x) == std::string(y)),explain_streq)
#define EXPECT_STREQ(X, Y) CHECK_STREQ(X, Y, pass = false)
#define ASSERT_STREQ(X, Y) CHECK_STREQ(X, Y, RESULT(false); return 1)

#define CHECK_NE(X, Y, Z) TRY(X,Y,Z,!(x != y),explain_ne)
#define EXPECT_NE(X, Y) CHECK_NE(X, Y, pass = false)
#define ASSERT_NE(X, Y) CHECK_NE(X, Y, RESULT(false); return 1)

#define CHECK_LT(X, Y, Z) TRY(X,Y,Z,!(x < y),explain_lt)
#define EXPECT_LT(X, Y) CHECK_LT(X, Y, pass = false)
#define ASSERT_LT(X, Y) CHECK_LT(X, Y, RESULT(false); return 1)

#define CHECK_LE(X, Y, Z) TRY(X,Y,Z,!(x <= y),explain_le)
#define EXPECT_LE(X, Y) CHECK_LE(X, Y, pass = false)
#define ASSERT_LE(X, Y) CHECK_LE(X, Y, RESULT(false); return 1)

#define CHECK_GT(X, Y, Z) TRY(X,Y,Z,!(x > y),explain_gt)
#define EXPECT_GT(X, Y) CHECK_GT(X, Y, pass = false)
#define ASSERT_GT(X, Y) CHECK_GT(X, Y, RESULT(false); return 1)

#define CHECK_GE(X, Y, Z) TRY(X,Y,Z,!(x >= y), explain_ge)
#define EXPECT_GE(X, Y) CHECK_GE(X, Y, pass = false)
#define ASSERT_GE(X, Y) CHECK_GE(X, Y, RESULT(false); return 1)

#define CHECK_NEAR(X, Y, Z, W) TRY(X,Y,W,!(std::abs(x-y) <= Z), explain_near)
#define EXPECT_NEAR3(X, Y, Z) CHECK_NEAR(X, Y, Z, pass = false)
#define ASSERT_NEAR3(X, Y, Z) CHECK_NEAR(X, Y, Z, RESULT(false); return 1)
#define EXPECT_NEAR2(X, Y) EXPECT_NEAR3(X, Y, 0.00005)
#define ASSERT_NEAR2(X, Y) ASSERT_NEAR3(X, Y, 0.00005)

#define EXPAND(X) X
#define GET_EXPECT_NEAR(_1,_2,_3,NAME, ...) NAME
#define EXPECT_NEAR(...) EXPAND( GET_EXPECT_NEAR(__VA_ARGS__, EXPECT_NEAR3, EXPECT_NEAR2)(__VA_ARGS__) )
#define GET_ASSERT_NEAR(_1,_2,_3,NAME, ...) NAME
#define ASSERT_NEAR(...) EXPAND( GET_ASSERT_NEAR(__VA_ARGS__, ASSERT_NEAR3, ASSERT_NEAR2)(__VA_ARGS__) )

#define TRY_TF(X,Y,Z,COND) \
try {\
  bool x = X;\
  if (COND) {\
    explain_tf(#X, x, Y, __FUNCTION__, __LINE__);\
    Z;\
  }\
} catch (const std::exception& err) {\
  std::cout << "did not expect " << #X << " to throw an exception, but got " << err.what() << std::endl;\
  Z;\
} catch (...) {\
  std::cout << "did not expect " << #X << " to throw an exception, but got non-std::exception" << std::endl;\
  Z;\
}

#define CHECK_TRUE(X, Y, Z) TRY_TF(X,Y,Z,!(x))
#define EXPECT_TRUE(X) CHECK_TRUE(X, true, pass = false)
#define ASSERT_TRUE(X) CHECK_TRUE(X, true, RESULT(false); return 1)

#define CHECK_FALSE(X, Y, Z) TRY_TF(X,Y,Z,x)
#define EXPECT_FALSE(X) CHECK_FALSE(X, false, pass = false)
#define ASSERT_FALSE(X) CHECK_FALSE(X, false, RESULT(false); return 1)

#define EXPECT(X) EXPECT_TRUE(X)
#define ASSERT(X) ASSERT_TRUE(X)
#define EXPECT_NOT(X) EXPECT_FALSE(X)
#define ASSERT_NOT(X) ASSERT_FALSE(X)

#define TRY_NULL(X,Z,COND) \
try {\
  auto x = X;\
  if (COND) {\
    explain_null(#X, X, __FUNCTION__, __LINE__);\
    Z;\
  }\
} catch (const std::exception& err) {\
  std::cout << "did not expect " << #X << " to throw an exception, but got " << err.what() << std::endl;\
  Z;\
} catch (...) {\
  std::cout << "did not expect " << #X << " to throw an exception, but got non-std::exception" << std::endl;\
  Z;\
}

#define CHECK_NULL(X, Z) TRY_NULL(X, Z, x)
#define EXPECT_NULL(X) CHECK_NULL(X, pass = false)
#define ASSERT_NULL(X) CHECK_NULL(X, RESULT(false); return 1)

#define CHECK_NOT_NULL(X, Z) TRY_NULL(X, Z, !X)
#define EXPECT_NOT_NULL(X) CHECK_NOT_NULL(X, pass = false)
#define ASSERT_NOT_NULL(X) CHECK_NOT_NULL(X, RESULT(false); return 1)

#define EXPECT_THROW(X,Y) \
try {\
  X;\
  std::cout << "expected " << #X << " to throw " << #Y <<", but nothing thrown" << std::endl;\
  pass = false;\
} catch (const Y& err) {}\
catch (const std::exception& err) {\
  std::cout << "expected " << #X << " to throw " << #Y <<", but got " << err.what() << std::endl;\
  pass = false;\
}\
catch (...) {\
  std::cout << "expected " << #X << " to throw " << #Y <<", but got a non-std::exception" << std::endl;\
  pass = false;\
}

#define EXPECT_THROW_MSSG(X,Y,Z) \
try {\
  X;\
  std::cout << "expected " << #X << " to throw " << #Y <<", but nothing thrown" << std::endl;\
  pass = false;\
} catch (const Y& err) { EXPECT_STREQ(err.what(), Z); }\
catch (const std::exception& err) {\
  std::cout << "expected " << #X << " to throw " << #Y <<", but got " << err.what() << std::endl;\
  pass = false;\
}\
catch (...) {\
  std::cout << "expected " << #X << " to throw " << #Y <<", but got a non-std::exception" << std::endl;\
  pass = false;\
}

#define ASSERT_THROW(X,Y) \
try {\
  X;\
  std::cout << "expected " << #X << " to throw " << #Y <<", but nothing thrown" << std::endl;\
  FAIL;\
} catch (const Y& err) {}\
catch (const std::exception& err) {\
  std::cout << "expected " << #X << " to throw " << #Y <<", but got " << err.what() << std::endl;\
  FAIL;\
}\
catch (...) {\
  std::cout << "expected " << #X << " to throw " << #Y <<", but got a non-std::exception" << std::endl;\
  FAIL;\
}

#define ASSERT_THROW_MSSG(X,Y,Z) \
try {\
  X;\
  std::cout << "expected " << #X << " to throw " << #Y <<", but nothing thrown" << std::endl;\
  FAIL;\
} catch (const Y& err) { ASSERT_STREQ(err.what(), Z); }\
catch (const std::exception& err) {\
  std::cout << "expected " << #X << " to throw " << #Y <<", but got " << err.what() << std::endl;\
  FAIL;\
}\
catch (...) {\
  std::cout << "expected " << #X << " to throw " << #Y <<", but got a non-std::exception" << std::endl;\
  FAIL;\
}

#define EXPECT_NO_THROW(X) \
try {\
  X;\
} catch (const std::exception& err) {\
  std::cout << "expected " << #X << " to throw no exception, but got " << err.what() << std::endl;\
  pass = false;\
}\
catch (...) {\
  std::cout << "expected " << #X << " to throw no exception, but got a non-std::exception" << std::endl;\
  pass = false;\
}

#define ASSERT_NO_THROW(X) \
try {\
  X;\
} catch (const std::exception& err) {\
  std::cout << "expected " << #X << " to throw no exception, but got " << err.what() << std::endl;\
  FAIL;\
}\
catch (...) {\
  std::cout << "expected " << #X << " to throw no exception, but got a non-std::exception" << std::endl;\
  FAIL;\
}

#define STARTING(X) std::cout << "Starting test_" << #X << "..." << std::endl;
#define TEST(X) STARTING(X); test_##X() ? pass_cnt++ : fail_cnt++;
#define SKIP(X) std::cout << "Skipping test_" << #X << "..." << std::endl; skip_cnt++;

std::ostream& operator<<(std::ostream& os, std::nullptr_t) {
  os << "nullptr";
  return os;
}

template <typename T1, typename T2>
void explain_eq(
    const char actual_expression[],
    const T1& actual_value,
    const char expected_expression[],
    const T2& expected_value,
    const char func[],
    const size_t line) {
  std::cout << func << ":" << line << ": Failure" << std::endl;
  std::cout << "Expected " << actual_expression << " to equal " << expected_expression << std::endl;
  std::cout << "     Got " << actual_value << " != " << expected_value << std::endl;
}

template <typename T1, typename T2>
void explain_ne(
    const char actual_expression[],
    const T1& actual_value,
    const char expected_expression[],
    const T2& expected_value,
    const char func[],
    const size_t line) {
  std::cout << func << ":" << line << ": Failure" << std::endl;
  std::cout << "Expected " << actual_expression << " to not equal " << expected_expression << std::endl;
  std::cout << "     Got " << actual_value << " == " << expected_value << std::endl;
}

template <typename B=bool>
void explain_tf(
    const char name[],
    B actual,
    B expected,
    const char func[],
    const size_t line) {
  std::cout << func << ":" << line << ": Failure" << std::endl;
  std::cout << "Expected " << name << " to be " << std::boolalpha << expected << ", got " << actual << std::endl;
}

template <typename T>
void explain_null(
    const char name[],
    const T& actual,
    const char func[],
    const size_t line) {
  std::cout << func << ":" << line << ": Failure" << std::endl;
  std::cout << "Expected " << name << " to be null, got " << actual << std::endl;
}

template <typename T1, typename T2>
void explain_lt(
    const char actual_expression[],
    const T1& actual_value,
    const char expected_expression[],
    const T2& expected_value,
    const char func[],
    const size_t line) {
  std::cout << func << ":" << line << ": Failure" << std::endl;
  std::cout << "Expected " << actual_expression << " to be less than " << expected_expression << std::endl;
  std::cout << "     Got " << actual_value << " >= " << expected_value << std::endl;
}

template <typename T1, typename T2>
void explain_le(
    const char actual_expression[],
    const T1& actual_value,
    const char expected_expression[],
    const T2& expected_value,
    const char func[],
    const size_t line) {
  std::cout << func << ":" << line << ": Failure" << std::endl;
  std::cout << "Expected " << actual_expression << " to be less than or equal to " << expected_expression << std::endl;
  std::cout << "     Got " << actual_value << " > " << expected_value << std::endl;
}

template <typename T1, typename T2>
void explain_gt(
    const char actual_expression[],
    const T1& actual_value,
    const char expected_expression[],
    const T2& expected_value,
    const char func[],
    const size_t line) {
  std::cout << func << ":" << line << ": Failure" << std::endl;
  std::cout << "Expected " << actual_expression << " to be greater than " << expected_expression << std::endl;
  std::cout << "     Got " << actual_value << " <= " << expected_value << std::endl;
}

template <typename T1, typename T2>
void explain_ge(
    const char actual_expression[],
    const T1& actual_value,
    const char expected_expression[],
    const T2& expected_value,
    const char func[],
    const size_t line) {
  std::cout << func << ":" << line << ": Failure" << std::endl;
  std::cout << "Expected " << actual_expression << " to be greater than or equal to " << expected_expression << std::endl;
  std::cout << "     Got " << actual_value << " < " << expected_value << std::endl;
}

template <typename T1, typename T2>
void explain_near(
    const char actual_expression[],
    const T1& actual_value,
    const char expected_expression[],
    const T2& expected_value,
    const char func[],
    const size_t line) {
  std::cout << func << ":" << line << ": Failure" << std::endl;
  std::cout << "Expected " << actual_expression << " to be near " << expected_expression << std::endl;
  std::cout << "     Got " << actual_value << " which is not near " << expected_value << std::endl;
}

// construct a representation of a string that is intended to be unambiguous
std::string repr(const std::string& str) {
    std::string rstr;
    rstr.push_back('"');
    for (char c : str) {
        switch(c) {
        case '"':
            rstr.append("\\\"");
            break;
        case '\t':
            rstr.append("\\t");
            break;
        case '\r':
            rstr.append("\\r");
            break;
        case '\n':
            rstr.append("\\n");
            break;
        case '\f':
            rstr.append("\\f");
            break;
        case '\v':
            rstr.append("\\v");
            break;
        case '\\':
            rstr.append("\\\\");
            break;
        default:
            if (c < 32 or c == 127) {
                // non-printable -> use hex
                char HEX[]{'0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f'};
                rstr.append("\\x");
                rstr.push_back(HEX[c / 16]);
                rstr.push_back(HEX[c % 16]);
            } else {
                // printable
                rstr.push_back(c);
            }
        }
    }
    rstr.push_back('"');
    return rstr;
}

void explain_streq(
    const char actual_expression[],
    const std::string& s1,
    const char expected_expression[],
    const std::string& s2,
    const char func[],
    const size_t line) {
  std::cout << func << ":" << line << ": Failure" << std::endl;
  std::cout << "Expected equality of these values:" << std::endl;
  std::cout << " " << actual_expression << std::endl;
  std::cout << "  Which is: " << repr(s1) << std::endl;
  std::cout << " " << expected_expression << std::endl;
  std::cout << "  Which is: " << repr(s2) << std::endl;
}
