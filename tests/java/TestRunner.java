import org.junit.runner.JUnitCore;
import org.junit.runner.Request;
import org.junit.runner.Result;
import org.junit.runner.notification.Failure;

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

  public void run() throws Exception{
    Result r = core.run(request);
    if (r.getFailureCount() != 0){
      String message = "";
      for (Failure failure : r.getFailures()){
        message += failure.getMessage() + "\n";
      }
      System.out.println(message);
      System.exit(1);
    }
    
  }
}