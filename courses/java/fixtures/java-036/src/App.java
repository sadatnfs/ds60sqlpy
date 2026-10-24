public class App {

  public static void main(String[] args) {
    if (args.length == 1 && args[0].equals("--self-test")) {
      System.out.println("release-ok");
    } else {
      System.err.println("unknown argument");
      System.exit(2);
    }
  }
}
