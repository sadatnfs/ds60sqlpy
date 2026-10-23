import java.util.*;

public class Main {
    static final class LocalServer implements AutoCloseable {
        final com.sun.net.httpserver.HttpServer server;boolean closed;
        LocalServer() throws java.io.IOException {
            server=com.sun.net.httpserver.HttpServer.create(new java.net.InetSocketAddress("127.0.0.1",0),0);
            server.createContext("/health",exchange -> {try(exchange){int status;String body;if(!exchange.getRequestURI().getPath().equals("/health")){status=404;body="not found";}else if(!exchange.getRequestMethod().equals("GET")){status=405;body="method not allowed";}else{status=200;body="ok";}byte[] bytes=body.getBytes(java.nio.charset.StandardCharsets.UTF_8);exchange.getResponseHeaders().set("Content-Type","text/plain; charset=utf-8");exchange.sendResponseHeaders(status,bytes.length);try(var output=exchange.getResponseBody()){output.write(bytes);}}});server.start();
        }
        java.net.URI uri(String path){return java.net.URI.create("http://127.0.0.1:"+server.getAddress().getPort()+path);}
        public void close(){server.stop(0);closed=true;}
    }
    public static void main(String[] args) throws Exception {
        // Exercise 1: Call an owned loopback endpoint
        try(LocalServer server=new LocalServer();var client=java.net.http.HttpClient.newBuilder().connectTimeout(java.time.Duration.ofSeconds(2)).build()) {
            var response=client.send(java.net.http.HttpRequest.newBuilder(server.uri("/health")).timeout(java.time.Duration.ofSeconds(2)).GET().build(),java.net.http.HttpResponse.BodyHandlers.ofString());
            assert response.statusCode()==200 && response.body().equals("ok");
        }

        // Exercise 2: Inspect content metadata
        try(LocalServer server=new LocalServer();var client=java.net.http.HttpClient.newHttpClient()) {
            var response=client.send(java.net.http.HttpRequest.newBuilder(server.uri("/health")).timeout(java.time.Duration.ofSeconds(2)).GET().build(),java.net.http.HttpResponse.BodyHandlers.ofString());
            assert response.headers().firstValue("Content-Type").orElseThrow().equals("text/plain; charset=utf-8");
        }

        // Exercise 3: Reject an unsupported method
        try(LocalServer server=new LocalServer();var client=java.net.http.HttpClient.newHttpClient()) {
            var request=java.net.http.HttpRequest.newBuilder(server.uri("/health")).timeout(java.time.Duration.ofSeconds(2)).POST(java.net.http.HttpRequest.BodyPublishers.noBody()).build();
            var response=client.send(request,java.net.http.HttpResponse.BodyHandlers.ofString());assert response.statusCode()==405 && response.body().equals("method not allowed");
        }

        // Exercise 4: Reject a prefix lookalike
        try(LocalServer server=new LocalServer();var client=java.net.http.HttpClient.newHttpClient()) {
            var response=client.send(java.net.http.HttpRequest.newBuilder(server.uri("/health-extra")).timeout(java.time.Duration.ofSeconds(2)).GET().build(),java.net.http.HttpResponse.BodyHandlers.ofString());assert response.statusCode()==404;
        }

        // Exercise 5: Keep error status separate from transport success
        try(LocalServer server=new LocalServer();var client=java.net.http.HttpClient.newHttpClient()) {
            var response=client.send(java.net.http.HttpRequest.newBuilder(server.uri("/missing")).timeout(java.time.Duration.ofSeconds(2)).GET().build(),java.net.http.HttpResponse.BodyHandlers.ofString());assert response.statusCode()==404;
        }

        // Exercise 6: Verify local-only target and closure
        LocalServer owned=new LocalServer();assert owned.uri("/health").getHost().equals("127.0.0.1") && owned.uri("/health").getPort()>0;owned.close();assert owned.closed;
    }
}
