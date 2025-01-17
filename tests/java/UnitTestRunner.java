/**
 * Runs the unit tests.
 */
public class UnitTestRunner {
  /**
   * Entry point.
   *
   * @param args command line arguments
      * @throws Exception 
      */
     public static void main(String[] args) throws Exception {
      TestRunner runner = new TestRunner(UnitTest.class);
      runner.run();
  }
}
