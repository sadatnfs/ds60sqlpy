import java.util.*;

public class Main {

  record Row(String id, String group, int amount) {}

  record Summary(String group, int count, int total) {}

  interface Repository {
    List<Row> rows();
  }

  static Summary summarize(Repository repository, String group) {
    var rows = repository
      .rows()
      .stream()
      .filter(row -> row.group().equals(group))
      .toList();
    if (rows.isEmpty()) throw new NoSuchElementException("not found");
    return new Summary(group, rows.size(), rows.stream().mapToInt(Row::amount).sum());
  }

  static java.net.http.HttpResponse<String> send(
    java.net.http.HttpClient client,
    java.net.URI uri,
    String method
  ) throws Exception {
    var builder = java.net.http.HttpRequest.newBuilder(uri).timeout(
      java.time.Duration.ofSeconds(2)
    );
    if (method.equals("GET")) builder.GET();
    else builder.method(method, java.net.http.HttpRequest.BodyPublishers.noBody());
    return client.send(builder.build(), java.net.http.HttpResponse.BodyHandlers.ofString());
  }

  static final class DataServer implements AutoCloseable {

    final com.sun.net.httpserver.HttpServer server;
    boolean closed;

    DataServer(Repository repository) throws java.io.IOException {
      server = com.sun.net.httpserver.HttpServer.create(
        new java.net.InetSocketAddress("127.0.0.1", 0),
        0
      );
      server.createContext("/summary", exchange -> {
        try (exchange) {
          int status;
          String body;
          String query = exchange.getRequestURI().getRawQuery();
          if (!exchange.getRequestURI().getPath().equals("/summary")) {
            status = 404;
            body = "{\"error\":\"not_found\"}";
          } else if (!exchange.getRequestMethod().equals("GET")) {
            status = 405;
            body = "{\"error\":\"method_not_allowed\"}";
          } else if (query == null || !query.matches("group=[A-Z]")) {
            status = 400;
            body = "{\"error\":\"invalid_query\"}";
          } else {
            try {
              Summary result = summarize(repository, query.substring(6));
              status = 200;
              body =
                "{\"group\":\"" +
                result.group() +
                "\",\"count\":" +
                result.count() +
                ",\"total\":" +
                result.total() +
                "}";
            } catch (NoSuchElementException missing) {
              status = 404;
              body = "{\"error\":\"not_found\"}";
            }
          }
          byte[] bytes = body.getBytes(java.nio.charset.StandardCharsets.UTF_8);
          exchange.getResponseHeaders().set("Content-Type", "application/json; charset=utf-8");
          exchange.sendResponseHeaders(status, bytes.length);
          try (var output = exchange.getResponseBody()) {
            output.write(bytes);
          }
        }
      });
      server.start();
    }

    java.net.URI uri(String path) {
      return java.net.URI.create("http://127.0.0.1:" + server.getAddress().getPort() + path);
    }

    public void close() {
      server.stop(0);
      closed = true;
    }
  }

  public static void main(String[] args) throws Exception {
    // Exercise 1: Verify the domain summary
    Repository repository = () ->
      List.of(new Row("a1", "A", 10), new Row("a2", "A", 20), new Row("b1", "B", 5));
    assert summarize(repository, "A").equals(new Summary("A", 2, 30));
    assert summarize(repository, "B").equals(new Summary("B", 1, 5));

    // Exercise 2: Read a successful HTTPsummary
    try (
      DataServer server = new DataServer(repository);
      var client = java.net.http.HttpClient.newHttpClient()
    ) {
      var response = send(client, server.uri("/summary?group=A"), "GET");
      assert response.statusCode() == 200 &&
      response.body().equals("{\"group\":\"A\",\"count\":2,\"total\":30}");
    }

    // Exercise 3: Report an unknown valid group
    try (
      DataServer server = new DataServer(repository);
      var client = java.net.http.HttpClient.newHttpClient()
    ) {
      var response = send(client, server.uri("/summary?group=C"), "GET");
      assert response.statusCode() == 404 && response.body().contains("not_found");
    }

    // Exercise 4: Reject ambiguous or malformed queries
    try (
      DataServer server = new DataServer(repository);
      var client = java.net.http.HttpClient.newHttpClient()
    ) {
      assert send(client, server.uri("/summary?group=A&group=B"), "GET").statusCode() == 400;
      assert send(client, server.uri("/summary?group=a"), "GET").statusCode() == 400;
    }

    // Exercise 5: Reject unsupported methods andpathlookalikes
    try (
      DataServer server = new DataServer(repository);
      var client = java.net.http.HttpClient.newHttpClient()
    ) {
      assert send(client, server.uri("/summary?group=A"), "POST").statusCode() == 405;
      assert send(client, server.uri("/summary-extra?group=A"), "GET").statusCode() == 404;
    }

    // Exercise 6: Preserve storage and close the owned listener
    List<Row> before = repository.rows();
    DataServer server = new DataServer(repository);
    server.close();
    assert server.closed && repository.rows().equals(before) && repository.rows().size() == 3;
  }
}
