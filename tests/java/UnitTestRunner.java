/**
 * Runs the unit tests.
 */
public class UnitTestRunner {
  /**
   * Entry point.
   *
   * @param args command line arguments
   */
  public static void main(String[] args) {
    TestRunner runner = new TestRunner(UnitTest.class);
    runner.run();
  }
}
