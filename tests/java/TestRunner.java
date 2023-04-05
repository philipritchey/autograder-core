import org.junit.runner.JUnitCore;
import org.junit.runner.Request;

/**
 * Common code to run JUnit tests.
 */
public class TestRunner {
  private JUnitCore core;
  private Request request;

  /**
   * Construct a test runner.
   *
   * @param classes list of classes containging tests.
   */
  public TestRunner(Class<?>... classes) {
    core = new JUnitCore();
    request = Request.classes(classes);
  }

  public void run() {
    core.run(request);
  }
}